from . import vispipe
from ._opt_reader import opt_reader
import logging,shutil,os,argparse

def main():
    _vispipe_parser = argparse.ArgumentParser(description='CSTORM Visulization Pipeline')
    _vispipe_parser.add_argument('config',nargs="*",type=str,help='Required vispipe configuration file.')
    _vispipe_parser.add_argument('-p',"--pdf",action='store_true',help="Generates a pdf. Sets images to False.",default=False)
    _vispipe_parser.add_argument('-i',"--image",action='store_false',help="Toggles if */pngs is kept. Keeps */pngs at the end of the run if -p is called.",default=True)
    _vispipe_parser.add_argument('-c',"--compress",action='store_true',help="Compress */pngs to a .tar.gz. Sets images to False.",default=False)
    _vispipe_parser.add_argument("--swap_settings",action="store_true",help="Add a custom \"settings.json\". Old files are renamed in vispipe dir.",default=False)
    _vispipe_parser.add_argument('-v',"--verbose",action='store_const',const=10,help="Show debugging messages.",default=30)
    _vispipe_parser.add_argument("-o","--opts",action="store_true",help="Read in an opt file instead of a json.",default=False)
    _vispipe_parser.add_argument("-f","--filepre",type=str,help="-o only: Common file prefix for all data files.",default="")
    _vispipe_parser.add_argument("-t","--titlepre",type=str,help="-o only: Common title prefix for all plots.",default="")
    _vispipe_parser.add_argument("-n","--nofill",action="store_false",help="-o only: Does not add missing datatypes to groups from deflist or settings.json.",default=True)
    _vispipe_parser.add_argument("--specname",nargs="*",help="-o only: Key value pairs of non standard file name for a type. Input looks like 'key0 val0 key1 val1 ... keyn valn'.",default=None)
    _vispipe_parser.add_argument("-d","--dump",action="store_true",help="-o only: Dumps opt into a opt.json. Does not run `vispipe()`.",default=False)
    
    args=_vispipe_parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s',level=args.verbose)

    if args.swap_settings:
        path=os.path.dirname(os.path.abspath(__file__))
        settings=os.path.join(path,"settings.json")
        shutil.move(settings,os.path.join(path,f"{len(os.listdir(path))-4}_settings.json"))
        newsettings=os.path.abspath(*args.config)
        shutil.copy2(newsettings,settings)
    else:    
        try:
            if args.opts:
                if args.specname: args.specname={ key:val for key,val in zip(args.specname[::2],args.specname[1::2]) }
                args.config=[opt_reader(args.config,**{"filepre":args.filepre,"titlepre":args.titlepre,"fill":args.nofill,"specname":args.specname,"dump":args.dump})]
                if args.config[0] is None:
                    exit()
            vispipe(*args.config,**{"image":args.image,"pdf":args.pdf,"compress":args.compress,"loglevel":args.verbose})
        except Exception as e:
            logging.exception(f"{e}")