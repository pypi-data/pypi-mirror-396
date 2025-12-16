import json,os,glob
from copy import deepcopy
import numpy

def opt_reader(opt_path: str | os.PathLike | list[str | os.PathLike],/,filepre: str="",titlepre: str="",fill: bool=True,specname: dict=None,dump: bool=False) -> dict | None:
    """Reader to conver opt files into config dictionaries or json files

    Parameters
    ----------
    opt_path : str | PathLike | iterable[str| PathLike,...]
        Path or paths to opt files.

    filepre : str, optional
        A common file prefix for all output files.

    titlepre : str, optional
        A common title prefix for all plots.

    fill : bool, default=True
        Adds missing datatypes to groups from deflist or settings.json

    specname : dict, optional
        Dictionary used to pass nonstandard file names. Keys are datatypes in the opt file.
    
    dump : bool, default=False
        Writes config to a json file instead of returning it as a dictionary.

    Returns
    -------
    dict | None
        Returns a dictionary to be used by vispipe. If `dump` is true `None` is returned.

    """
    
    #[ ] Redo this
    if "opt" in opt_path:
        files=[os.path.abspath(opt_path)]
        run_path=os.path.dirname(files[0])
    elif hasattr(opt_path,"__iter__") and len(opt_path):
        files=[os.path.abspath(op) for op in opt_path]
        run_path=os.path.dirname(files[0])
    else:
        if not opt_path:
            run_path=os.getcwd()
        else:
            run_path=os.path.abspath(opt_path[0])
        files=glob.glob(os.path.join(run_path,"*_opt*"))

    with open(os.path.join(os.path.dirname(__file__),"settings.json")) as file:
        opt_opts=json.load(file).get("opt",{})
    

    config={"globals":{},"plots":{}}
    for file in files:
        with open(file) as opt:
            jason=json.load(opt)
        globals=jason.pop("globals",{})

        if "models" in jason:
            model_tipe=jason.pop("models")
        else:
            model_tipe=[os.path.basename(file).split("_")[2]]

        data_types={}
        for mt in model_tipe:
            data_types={**data_types,**opt_opts.get(mt,{})}

        if "deflist" in globals:
            data_types={tipe:data_types.get(tipe,{}) for tipe in globals.pop("deflist")}

        global_kwargs=globals.get("global_kwargs",{})
        fill=global_kwargs.pop("fill",fill)
        for tipe,settings in data_types.items():
            if specname and tipe in specname:
                output_path=f"{run_path}/{specname[tipe]}"#.format(run_path=run_path,filename=)
            else:
                output_path=f"{run_path}/{filepre+'_' if filepre else ''}{settings.get('file_base',tipe)}"#.format(run_path=run_path,filepre=filepre,tipe=tipe,tail=tail)

            globals_settings=globals.get(tipe,{})
            globals_settings["path"]=output_path

            glk=deepcopy(global_kwargs)
            glk.update(globals_settings)
            config["globals"][tipe]=glk
        
        plotcount={ data_type:0 for data_type in data_types}
        
        for key,group in jason.items():
            if group is None:
                group={}
            group_type=key.split(":")[0]
            group_item=(group.pop("group") if group_type=="group" else {group_type:group.pop(group_type)}) if group_type!="default" else None
            do_fill=group.pop("fill",fill)
            titlepre=titlepre.replace("\\n","\n") if titlepre else data_types.get("titlepre","")
            
            for plotkey,plotitem in group.items():
                plotkey=plotkey.split(":")[0]
                plotname=f"{plotkey}:{plotcount[plotkey]}"#.format(plotkey=plotkey,plotcount=plotcount[plotkey])
                plotcount[plotkey]+=1
                plotitem={} if plotitem=="default" or plotitem is None else plotitem
                if group_item:
                    plot_params=deepcopy(group_item)
                    plot_params.update(plotitem)
                else:
                    plot_params=plotitem
                
                fin_title=f"{titlepre+' ' if titlepre and 'title' in plot_params else titlepre}{plot_params.get('title','')}"#.format(titlepre=titlepre,title=plot_params.get('title'))
                if fin_title: plot_params["title"]=fin_title
                config["plots"][plotname]=plot_params

            if do_fill:
                for tipe in data_types:
                    if tipe not in group:
                        plotname=f"{tipe}:{plotcount[tipe]}"#.format(plotkey=tipe,plotcount=plotcount[tipe])
                        plotcount[tipe]+=1
                        plot_params=deepcopy(group_item) if group_item else {}
                        fin_title=f"{titlepre+' ' if titlepre and 'title' in plot_params else titlepre}{plot_params.get('title','')}"#.format(titlepre=titlepre,title=plot_params.get('title'))
                        if fin_title: plot_params["title"]=fin_title
                        config["plots"][plotname]=plot_params

        #for key,cnt in plotcount.items(): 
        #    if not cnt: del config["globals"][key]

    if not dump:
        return config
    else:
        jsonpath=f"{run_path}/{filepre+'_' if filepre else ''}vispipe.json"#.format(run_path=run_path,filepre=filepre)
        with open(jsonpath,"w") as configjason:
            json.dump(config,configjason,indent=4)

