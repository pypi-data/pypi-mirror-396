"""The ``_Options`` class handles checking ``dpi``, ``resolution``,
``backend``, and ``ncpus`` for validity. These settings would break 
all plots ifnot valid so an extra layer of protections is provided.
``_Options`` is not instantiated directlly, but rather when the 
module is imported as a module variable ``voptions``. In the future,
users will be able to subclass ``_Options`` to add custom 
enforcments for other variables.
"""

from .plot_backend import MPL_Figure,_vispipe_backend_api
import warnings,importlib
from copy import copy

class _Options(dict):
    _defaults={
        "dpi":500,
        "resolution":(3840,2160),
        "backend":MPL_Figure,
        "ncpus":None
    }

    def __init__(self):
        """Dictionary subclass for options that require higher levels of enforcement."""
        super().__init__(self._defaults)
        self._check_map={"dpi":self._check_dpi,"resolution":self._check_resolution,"backend":self._check_backend,"ncpus":self._check_ncpus}

    def __setitem__(self, key, value) -> None:
        if key in self._check_map:
            value=self._check_map[key](value)        
        super().__setitem__(key,value)

    @staticmethod
    def _check_dpi(dpi: int):
        "Rule for checking dpi."
        try:
            dpi=int(dpi)
            assert dpi>0
            return dpi
        except AssertionError:
            raise ValueError("dpi must be greater than 0.")
        except Exception as e:
            raise e
    
    @staticmethod
    def _check_resolution(resolution: tuple[int,int]):
        "Rule for checking resolution"
        try:
            x,y=int(resolution[0]),int(resolution[1])
            assert x>0 and y>0
            return x,y
        except AssertionError:
            raise ValueError("x and y of resolution must be greater than 0.")
        except TypeError:
            raise TypeError("Resolution must be an iterable.")
        except Exception as e:
            raise e

    @staticmethod
    def _check_backend(backend):
        """Rule for checking plotting backend. 

        Notes
        -----
        The only hard check that happens is if a module string fails to import. A soft check is performed on `backend` for a subclassing of `vispipe.plot_backend._vispipe_backend_api`. Only a warning is thrown if that check fails.
        
        """
        try:
            if isinstance(backend,str):
                backend=getattr(importlib.import_module(".".join((readlist:=backend.split("."))[:-1])),readlist[-1])
            if not issubclass(backend,_vispipe_backend_api):
                warnings.warn("Backend is not subclass of _vispipe_backend_api.")
            return backend
        except Exception as e:
            raise e
        
    @staticmethod
    def _check_ncpus(ncpus: int | None):
        "Rule for checking for cpus"
        if ncpus is None:
            return
        try:
            ncpus=int(ncpus)
            assert ncpus>0
            return ncpus
        except AssertionError:
            raise ValueError("ncpus must be greater than 0")
        except Exception as e:
            raise e
    
    def set_plot(self,plotdict):
        "Checks entries in a plotdict for defaults and adds them if missing or checks them if present."
        for key in self:
            if key not in plotdict:
                plotdict[key]=self[key]
            elif key in self._check_map:
                plotdict[key]=self._check_map[key](plotdict[key])

    def copy(self):
        "Returns a shallow copy of `self`."
        return copy(self)
    
    def reset(self):
        "Resets options to default and clears non default settings."
        self.clear()
        self.__init__()

    def update(self,mapping):
        "Updates `self` inplace from a mapping. If a key is present in the mapping but not `self` that key and item are added."
        for key,item in dict(mapping).items():
            self[key]=item

voptions=_Options()