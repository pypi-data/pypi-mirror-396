"""``vispipe._vispipe`` is where the pipeline is executed. All
members in this submodule are used `directly and exclusively 
by ``vispipe()`` and ``_pipeline()``."""
from multiprocessing import Pool
from pint import UnitRegistry
import matplotlib.pyplot as plt
import numpy as np
import os,shutil,json,fitz,logging
import importlib
from .plot_backend import MPL_Figure
from vispipe._options import voptions 
from functools import partial
__all__=["vispipe"]

#[ ] Start with multiplot be in serial then figure out how to get procs to comunicate.
#[ ] lru_cache for vals that have been read already.
#[ ] make better logger
    
def _getfunc(plm):
    """Imports a function from a package.module.function string."""
    func=getattr(importlib.import_module(".".join((readlist:=plm.split("."))[:-1])),readlist[-1])
    return func

#Writes the individule .pngs to a .pdf page.
def _writepdf(pngpath,width,height):
    """Adds png to pdf page."""
    file=fitz.open()
    #width and height are in pixels.
    page=file.new_page(width=width,height=height)
    page.insert_image([0,0,width,height], filename=pngpath)
    pdfname=pngpath.split("/")[-1][:-4]
    file.save(os.path.join(os.path.dirname(os.path.dirname(pngpath)),f"pages/{pdfname}.pdf"))

#Creates the main pdf from the indiviual pdfs.
def _orderpdf(title):
    """Compiles pdf pages into a full document."""
    pages=os.listdir(os.path.join(os.path.dirname(title),"pages"))
    pages=sorted([float(i[:-4]) for i in pages])
    doc=fitz.open()
    for page in pages:
        file=fitz.open(os.path.join(os.path.dirname(title),f"pages/{page}.pdf"))
        doc.insert_pdf(file)
    doc.save(f"{title}")

def _merge_func_setting(high,low,key,library={}):
    """Merges function settings from configs and setting.json."""
    if isinstance(high[key],str):
        high[key]={"name":high[key]}
        high[key].update(library.get(high[key]["name"],{}))

    if "name" not in high[key]:
        high[key]={**low[key],**high[key]}
        high[key]["kwargs"]={**low[key].get("kwargs",{}),**high[key].get("kwargs",{})}

    elif key in low and low[key]["name"]==high[key]["name"]:
        high[key]={**low[key],**high[key]}
        high[key]["kwargs"]={**low[key].get("kwargs",{}),**high[key].get("kwargs",{})}
    
    return high[key]

#[ ] Make recursive to better facilitate lists.
def _read_sig(plotter,vals,kwargs,plotargs,plotkwargs,locals,recnumber):
    """Prepares inputs to the plot function from a sig in the plotter dictionary."""
    plotsig=plotter.pop("sig")
    exclusive=plotsig.pop("exclusive",False)
    par=()
    pkw={}
    for key in plotkwargs:
        plotsig.pop(key,None)

    addargs="vp:plotargs" not in plotsig and "plotargs" in plotter 
    for key,item in plotsig.copy().items():
        
        if "*" in key:
            if "**" in key: break
            del plotsig[key]
            if item is not None:
                par+=vals[int(item)] if "vp:" not in str(item) else tuple(kwargs.pop(item[3:],locals.get(item[3:])))
            break
        del plotsig[key]

        if str(item).isdigit():
            item=vals[int(item)]
            if key=="rec" and recnumber is not None: item=item[recnumber]
            par+=(item,)
            continue
        elif isinstance(item,list):
            par+=tuple(vals[int(i)] if "vp:" not in str(i) else kwargs.pop(i[3:],locals.get(item[3:])) for i in item)
            continue
        elif isinstance(item,str) and "vp:" in item:
            item=kwargs.pop(item[3:],locals.get(item[3:]))
            if key=="rec" and recnumber is not None: item=item[recnumber]
            par+=(item,)
            continue
    
    plotargs=par+(plotargs if addargs else ())
    
    for key,item in plotsig.items():
        if "**" in key:
            if item is not None and item!="vp:plotkwargs":
                pkw.update(vals[int(item)] if "vp:" not in str(item) else tuple(kwargs.pop(item[3:],locals.get(item[3:]))))
            elif item=="vp:plotkwargs":
                plotkwargs={**pkw, **plotkwargs}
                break
            else:
                break
        if str(item).isdigit(): 
            pkw[key]=vals[int(item)]
            continue
        elif isinstance(item,list):
            pkw[key]=tuple(vals[int(i)] if "vp:" not in str(i) else kwargs.pop(i[3:],locals.get(item[3:])) for i in item)
            continue
        elif isinstance(item,str) and "vp:" in item:
            pkw[key]=kwargs.pop(item[3:],locals.get(item[3:]))
            continue
    else:
        plotkwargs={**pkw, **plotkwargs}
    if not exclusive:
        plotkwargs.update(kwargs)
    
    return plotargs,plotkwargs
            
def _squash_level(high,low,readers_jason={},plotters_jason={}):
    if "reader" in high:
        high["reader"]=_merge_func_setting(high,low,"reader",readers_jason)

    if "plotter" in high:
        high["plotter"]=_merge_func_setting(high,low,"plotter",plotters_jason)

    if "stattable" in high:
        high["stattable"]=_merge_func_setting(high,low,"stattable")

    if "recs" in high or "recs" in low:
        rhigh=high.get("recs",{})
        if isinstance(rhigh,list):
            rhigh=dict.fromkeys(rhigh)
        elif isinstance(rhigh,str):
            rhigh={rhigh: None}
        
        rlow=low.get("recs")

        if rlow:        
            if rhigh and isinstance(rlow,dict):
                for key,rhigh_item in rhigh.items():
                    rlow_item=rlow.get(key,{})
                    rlow_item={rli_key:rli_item for rli_key,rli_item in rlow.get(key,{}).items() if rli_key not in high}
                    if rhigh_item and rlow_item:
                        rhigh[key]=_squash_level(rhigh_item,rlow_item,readers_jason,plotters_jason) 
                    elif not rhigh_item:
                        rhigh[key]=rlow_item

            elif not rhigh:
                if isinstance(rlow,list):
                    rlow=dict.fromkeys(rlow)
                elif isinstance(rlow,str):
                    rlow={rlow: None}
                rhigh=rlow

        high["recs"]=rhigh

    return {**low,**high}
    
def _parse_file_records(uni_datatype):
    frecs=uni_datatype.pop("file_records")
    for i,key in enumerate(frecs):
        frecs[key]["recnumber"]=i
    if "recs" in uni_datatype:
        recs=uni_datatype.pop("recs")
        if isinstance(recs,list):
            recs=dict.fromkeys(recs,{})
        elif isinstance(recs,str):
            recs={recs: {}}
        return {rkey:{**frecs[rkey],**recs[rkey]} for rkey in recs}
    else:
        return frecs
    

#pipeline handes all operations associated with individual plots. 
def _pipeline(kwargs):
    """Called by the `Pool` in `vispipe()`. Creates the pngs and pages."""
    try:
        dpi,(width,height),plot_api=kwargs.pop("dpi"),kwargs.pop("resolution"),kwargs.pop("backend")
        plt.set_loglevel("warning")
        logging.basicConfig(format='%(levelname)s: %(message)s',level=kwargs.pop("loglevel"))
        if "type" in kwargs: del kwargs["type"]
        reader=kwargs.pop("reader",None)
        path=kwargs.pop("path",None)
        pagenumber=kwargs.pop("pagenumber",None)
        recnumber=kwargs.pop("recnumber",None)
        
        plotter=kwargs.pop("plotter",None)
        savedir=kwargs.pop("savedir",None)
        pdf=kwargs.pop("pdf",None)
        useback=not kwargs.pop("no_back",False)

        loggingsuffix=f"\n\tfile={path}\n\tfig={pagenumber}\n"
        logging.info(f"Preparing plot for fig {pagenumber}")

        #Checks for a reader and the assigns vals to be plotted.
        if reader:   
            logging.debug("Reading in vals.")     
            readfunc=_getfunc(reader["name"])
            readargs=reader.pop("args",())
            readkwargs=reader.pop("kwargs",{})
            vals=readfunc(path,*readargs,**readkwargs)
            logging.debug(f"Fig {pagenumber} vals read.")
        else:
            vals=kwargs.pop("vals")
            kwargs.pop("meshtype",None)


        #Checks if the unit needs to be changed.
        try:
            if kwargs.get("defunit") and kwargs["unit"]!=kwargs.get("defunit") and kwargs.get("mesh"):
                logging.debug(f"Converting unit from {kwargs.get('defunit')} to {kwargs['unit']} for fig {pagenumber}.")
                ureg=UnitRegistry()
                tempvals=vals[vals!=kwargs.get("empty_value")]
                vals[vals!=kwargs.pop("empty_value",np.nan)]=ureg.Quantity(tempvals,kwargs.pop("defunit")).to(kwargs.get("unit")).magnitude
            else:
                if "defunit" in kwargs: del kwargs["defunit"]
                if "empty_value" in kwargs: del kwargs["empty_value"]

            if not useback:
                kwargs["cbarunit"]=kwargs.pop("unit",None)
            elif "cbar" in kwargs:
                if not isinstance(kwargs["cbar"],dict):
                    kwargs["cbar"]={"label":kwargs.pop("unit")}
                elif "label" not in kwargs["cbar"]: 
                    kwargs["cbar"]["label"]=kwargs.pop("unit")
            else:
                del kwargs["unit"]

        except:
            if not useback:
                kwargs["cbarunit"]=kwargs.get("defunit")
            elif "cbar" in kwargs:
                if not isinstance(kwargs["cbar"],dict):
                    kwargs["cbar"]={"label":kwargs.get("defunit")}
                elif "label" not in kwargs["cbar"]: 
                    kwargs["cbar"]["label"]=kwargs.get("defunit")
            if "unit" in kwargs: del kwargs["unit"]
            if "empty_value" in kwargs: del kwargs["empty_value"]
            logging.warning(f"\t\nUsing default unit ({kwargs.pop('defunit')}) for:{loggingsuffix}")
    
        if "title" in kwargs:
            titlepre=kwargs.pop("titlepre",False)
            title=kwargs.pop("title")
            if titlepre:
                title=f"{titlepre} for {title}".replace("\\n","\n")
        elif kwargs.get("titlepre"):
            title=kwargs.pop("titlepre")
        if "table" in kwargs:
            plot: MPL_Figure=plot_api(pagenumber,subplots=(1,2),title=title,figsize=(width/dpi,height/dpi),layout=kwargs.pop("layout","tight"),subplots_kw=kwargs.pop("subplots_kw",{}))
            fig,(table_ax,ax)=plot.return_fig()
            table=kwargs.pop("table")
            tableargs=table.pop("args",())
            tablekwargs=table.pop("kwargs",{})
            tablefunc=_getfunc(table["name"])
            tableargs,tablekwargs=_read_sig(table,vals,kwargs.copy(),tableargs,tablekwargs,locals(),recnumber)
            tablefunc(*tableargs,**tablekwargs)
        else:
            plot: MPL_Figure=plot_api(pagenumber,title=title,figsize=(width/dpi,height/dpi),layout=kwargs.pop("layout","compressed"),subplots_kw=kwargs.pop("subplots_kw",{}))
            fig,(ax,)=plot.return_fig()

        
        #Preps args and kwargs for the plot
        if useback:
            plotsettings={key:kwargs.pop(key) for key in kwargs.copy() if key in ("subtitle","xlabel","ylabel","xticks","yticks","aspect","grid","bbox","set","cbar")}
            if "subtitle" in plotsettings:
                plot.set_subtitle(plotsettings["subtitle"],ax=ax) if not isinstance(plotsettings["subtitle"],dict) else plot.set_subtitle(ax=ax,**plotsettings["subtitle"])
            
            if "xlabel" in plotsettings:
                plot.set_xlabel(plotsettings["xlabel"],ax=ax) if not isinstance(plotsettings["xlabel"],dict) else plot.set_xlabel(ax=ax,**plotsettings["xlabel"])
            
            if "ylabel" in plotsettings:
                plot.set_ylabel(plotsettings["ylabel"],ax=ax) if not isinstance(plotsettings["ylabel"],dict) else plot.set_ylabel(ax=ax,**plotsettings["ylabel"])

            if "xticks" in plotsettings:
                plot.set_xticks(plotsettings["xticks"],ax=ax) if not isinstance(plotsettings["xticks"],dict) else plot.set_xticks(ax=ax,**plotsettings["xticks"])

            if "yticks" in plotsettings:
                plot.set_yticks(plotsettings["yticks"],ax=ax) if not isinstance(plotsettings["yticks"],dict) else plot.set_yticks(ax=ax,**plotsettings["yticks"])

            if "aspect" in plotsettings:
                plot.set_aspect(plotsettings["aspect"],ax=ax) if not isinstance(plotsettings["aspect"],dict) else plot.set_aspect(ax=ax,**plotsettings["aspect"])

            if "grid" in plotsettings:
                plot.set_grid(plotsettings["grid"],ax=ax) if not isinstance(plotsettings["grid"],dict) else plot.set_grid(ax=ax,**plotsettings["grid"])

            if "bbox" in plotsettings:
                plot.set_bbox(plotsettings["bbox"],ax=ax) if not isinstance(plotsettings["bbox"],dict) else plot.set_bbox(ax=ax,**plotsettings["bbox"])

            if "set" in plotsettings:
                plot.set(ax=ax,**plotsettings["set"])

        plotfunc=getattr(plot,plotter["name"],None)
        if plotfunc is None:
            plotfunc=_getfunc(plotter["name"])
        plotargs=plotter.pop("args",())
        plotkwargs=plotter.pop("kwargs",{})

        #sets up plot kw/args
        if "sig" not in plotter:
            plotargs=((vals,) if not isinstance(vals,tuple) else vals)+kwargs.pop("mesh",())+plotargs
            plotkwargs.update(kwargs)
        else:
            plotargs,plotkwargs=_read_sig(plotter,vals,kwargs,plotargs,plotkwargs,locals(),recnumber)
        
        logging.debug(f"Fig {pagenumber}\nplotargs: {plotargs}")
        logging.debug(f"plotkwargs: {plotkwargs}")
        logging.debug(f"Plotting fig {pagenumber}.")

        cm=plotfunc(*plotargs,**plotkwargs)
        if useback and "cbar" in plotsettings:
            plot.cbar(cm,ax=ax,**plotsettings.pop("cbar",) if isinstance(plotsettings["cbar"],dict) else {})
        
        pngpath=os.path.join(savedir,f"pngs/{os.path.basename(path).split('.')[0]+'-' if not pdf else ''}{pagenumber}.png")
        logging.debug(f"Fig {pagenumber} plotted.")

        plot.savefig(pngpath,dpi=dpi)
        logging.info(f"Fig saved for page {pagenumber}")

        if pdf: _writepdf(pngpath,width,height)
        logging.info(f"Page {pagenumber} succesfully writen.")
    except Exception as e:
        logging.error(f"An error occured for fig {pagenumber}.")
        logging.exception(f"{e}")
        

def vispipe(config,image=True,pdf=False,compress=False,loglevel=30):
    """Function to run batch visuilize numerical model outputs.

    Parameters
    ----------
    config : str | dict
        Path to config json file or a config formatted dict.

    image : bool, default=True
        Deterimins whether pngs dir is saved.

    pdf : bool, default=False
        Deterimins if a pdf is generated. If True, `image` is set to `not image`.
        
    compress : bool, default=False
        If True, compresses pngs dir to a .tar.gz and `image` is set to `not image`. 

    loglevel : int, default=30
        Log level for logging module.
    
    Notes
    -----
    If `pdf` and `compress` are `True` `image` will only be `not`ed once. If `image` is set to `False` when either is set to `True`, `images` will be switched to `True`.
    
    """
    
    if pdf or compress: image=not image
    
    logging.debug("Reading universal settings.")
    with open(os.path.join(os.path.dirname(__file__),"settings.json")) as file:
        settings_jason=json.load(file)
        options_jason=settings_jason.get("options",{})
        format_jason=settings_jason.get("format",{})
        readers_jason=settings_jason.get("readers",{})
        plotters_jason=settings_jason.get("plotters",{})
        universal_jason: dict[str,dict]=settings_jason["universals"]

    if options_jason:
        voptions.update(options_jason)

    squash_level=partial(_squash_level,readers_jason=readers_jason,plotters_jason=plotters_jason)

    if not isinstance(config,dict):
        logging.debug("Reading config.")
        with open(config) as file:
            config=json.load(file)
    global_jason=config["globals"]
    plots_jason: dict=config["plots"]

    if "options" in global_jason:
        voptions.update(global_jason.pop("options"))
    
    ncpus=voptions.pop("ncpus")
    
    savedir=global_jason.get("save_path",os.path.abspath(os.curdir))
    if ".pdf"==savedir[-4:]:
        savedir,savepdf=os.path.split(savedir)
    elif pdf:
        savepdf=f"{os.path.basename(savedir)}.pdf"


    logging.debug("Setting format.")
    formattype=global_jason.pop("format",format_jason.get("default")).lower()
    fmtset=set(format_jason["set"])
    for key,settings in universal_jason.items():
        #Selecting proper format settings
        if formattype and fmtset & settings.keys():
            fmtsettings=settings.pop(formattype,{})
            for delkeys in fmtset-set([formattype]):
                settings.pop(delkeys,None)
            settings.update(fmtsettings)

        if "file_records" in settings:
            settings["recs"]=_parse_file_records(settings)
        #Pulling settings from the base 
        #[ ] Try turning this into a for loop
        if "base" in settings:
            base=settings.pop("base")
            if "file_records" in settings:
                universal_jason[base]["recs"]=_parse_file_records(universal_jason[base])

            universal_jason[key]=squash_level(settings,universal_jason[base])
            

    logging.debug(f"Format set to {formattype}.")
    globsets=[(key,item) for key,item in global_jason.items()]
    
    for key,item in globsets:
        if key=="grd" or isinstance(item,dict) and (meshtype:=item.get("meshtype")):
            logging.debug(f"Reading mesh {key}.")
            if key=="grd":
                meshtype=None
                if not isinstance(item,dict): 
                    if formattype!="netcdf4":
                        item={"path":item}
                    else:
                        item={"path":global_jason[item] if not isinstance(global_jason[item],dict) else global_jason[item]["path"]}
                    global_jason[key]=item
            reader=item.pop("reader",universal_jason.get("grd",universal_jason.get(meshtype)).pop("reader"))
            readerargs=item.pop("reader_args",universal_jason.get("grd",universal_jason.get(meshtype)).pop("reader_args",()))
            readerkwargs=item.pop("reader_kwargs",universal_jason.get("grd",universal_jason.get(meshtype)).pop("reader_kwargs",{}))

            readfunc=_getfunc(reader)
            global_jason[key]["vals"]=readfunc(global_jason[key]["path"],*readerargs,**readerkwargs)
    

    logging.debug("Making pngs and pages dirs.")
    pngpath=os.path.join(savedir,"pngs")
    if not os.path.exists(pngpath): os.mkdir(pngpath)
    if pdf:
        pagespath=os.path.join(savedir,"pages")
        if not os.path.exists(pagespath): os.mkdir(pagespath)
    
    inputs=[]
    globkwargs=global_jason.pop("global_kwargs",{})

    logging.debug("Updating global settings.")
    for globkey,glob in global_jason.items():
        if globkey in universal_jason:
            universalkey=globkey
        elif "type" in global_jason[globkey]:
            universalkey=global_jason[globkey]["type"]
        elif "meshtype" in global_jason[globkey]:
            universalkey=global_jason[globkey]["meshtype"]
        else:
            continue

        if isinstance(glob,str):
            glob={"path":glob}
        glob=squash_level(glob,universal_jason[universalkey])
        global_jason[globkey]={**globkwargs,**glob}
    

    logging.debug("Updating plot settings.")

    for i,(key,plot) in enumerate(plots_jason.items()):
        logging.debug(f"Making setting plot settings for {key}.")
        logging.debug(f"Setting references.")
        if plot is None: plot={}
        """ if "type" in plot:
            globkey=plot["type"]
        else: """
        globkey=key.split(":")[0]
        
        if globkey in universal_jason:
            universalkey=globkey
        elif "type" in global_jason[globkey]:
            universalkey=global_jason[globkey]["type"]
        elif "meshtype" in global_jason[globkey]:
            universalkey=global_jason[globkey]["meshtype"]
        else:
            universalkey=None
        
        logging.debug(f"Reference keys are:\n\tplot: {key}\n\tglobal: {globkey}\n\tuniversalkey: {universalkey}")

        logging.debug("Updating universal settings.")
        glob=global_jason.get(globkey,universal_jason.get(universalkey,{}))
        plotdict=squash_level(plot,glob)

        if plotdict.get("table"):
            plotdict["table"]=plotdict.pop("stattable",False)
        else:
            if "stattable" in plotdict:
                del plotdict["stattable"]
            if "table" in plotdict:
                del plotdict["table"]
        logging.debug("Adding save path and units.")

        plotdict["savedir"]=savedir
        plotdict["pdf"]=pdf
        voptions.set_plot(plotdict)

        recs=plotdict.pop("recs",{0:{}})
        
        for j,(rkey,rec) in enumerate(recs.items()):
            if "recnumber" in rec:
                rec=rec.copy()
                locplotdict=plotdict.copy()
                locplotdict["recnumber"]=rec.pop("recnumber")

                locplotdict=squash_level(rec,locplotdict)
            else:
                locplotdict=plotdict

            if locplotdict["plotter"].get("mesh"):
                logging.debug(f"Adding mesh data from {locplotdict['mesh']}.")
                if locplotdict.get("mesh") is None or isinstance(locplotdict["mesh"],bool):
                    locplotdict["mesh"]="grd"
                locplotdict["mesh"]=global_jason[locplotdict["mesh"]]["vals"]
            elif "mesh" in locplotdict:
                del locplotdict["mesh"]

            if "unit" in locplotdict:
                punit=locplotdict["unit"]
                if "recs" in universal_jason.get(universalkey):
                    uunit=universal_jason.get(universalkey)["recs"][rkey].get("unit",punit)
                else:
                    uunit=universal_jason.get(universalkey).get("unit",punit)
                if punit!=uunit:
                    locplotdict["defunit"]=uunit

            logging.debug("Checking minreqs.")
            minreqs=set(locplotdict.pop("minimum",locplotdict.keys()))
            dif=minreqs-set(locplotdict.keys())
            if not dif or "vals" in locplotdict and not len(dif)-1:
                logging.debug(f"All minreqs found for {key}.") 
                locplotdict["loglevel"]=loglevel
                locplotdict["pagenumber"]=i+j/10
                print(locplotdict["titlepre"])
                inputs.append(locplotdict)
            else:
                logging.error(f"Keys {minreqs - set(locplotdict.keys())} are missing for plot {key}. Skipping.")
        
    #Pool() is a function used in multiprocessing. It creates a pool of functions all running at the same time. This is used in place of a for loop to speed things up drastically. 
    #The time to complete the entire proccess is roughly how long it takes to complete the largest set, instead waiting for all to finish one after the other.
    with Pool(ncpus) as pool:
        result=pool.map_async(_pipeline,inputs)
        result.wait()
    #This orders the individual pages and saves them as one file before cleaning up the work space.
    #This try block allows for the error to be 
    try:
        if pdf: _orderpdf(os.path.join(savedir,savepdf))
    except Exception as e:
        logging.exception(f"{e}")
        if not image: shutil.rmtree(pngpath)
        if pdf: shutil.rmtree(pagespath)
        return

    #Cleans up workspace based on command line flags.
    if compress:
        import tarfile
        if os.path.isfile(f"{pngpath}.tar.gz"): 
            import pathlib
            pathlib.Path.unlink(f"{pngpath}.tar.gz")
        with tarfile.open(f"{pngpath}.tar.gz", "x:gz" ) as tar:
            tar.add(pngpath,arcname="pngs")
    if not image: shutil.rmtree(pngpath)
    if pdf: shutil.rmtree(pagespath)
    
    