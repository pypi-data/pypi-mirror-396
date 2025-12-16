"""
This module provides a built in backend for internal plotting. 
:doc:`MPL_Figure<plot_backend/MPL_Figure>` is currently the 
only built in backend but this can be swapped. `MPL_Figure` uses
functions from :doc:`vispipe._gridedit<plot_backend/gridedit>` to
remove subgrids from larger grids.

"""



import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.tri import Triangulation
import numpy as np
from ._gridedit import meshgridcut,tri_bbox_prep
from abc import ABCMeta

#[ ] Clean up inputs
__all__=["MPL_Figure"]

class _vispipe_backend_api(metaclass=ABCMeta):
    """Base class for plot backends used by voptions to check compatability. Currently has no method enforcment."""
    pass

class MPL_Figure(_vispipe_backend_api):
    def __init__(self,
    id=None,
    fig=None,
    ax=None,
    subplots=None,
    title=None,
    layout="compressed",
    figsize=None,
    subplots_kw={},
    legend=False) -> None:
        """Matplotlib backend used by vispipe.
        
        Parameters
        ----------
        id : int | str, optional
            Identifier for the figure. Will be used in the future.

        fig : matplotlib.figure.Figure | None, default=None
            A matplotlib figure. If `fig==None and ax==None` `plt.subplots()` is called .

        ax : Axes | Iterable | None, default=None
            `Axes` or collection of Axes.

        subplots : tuple[int,int], optional
            If not `None`, it is unpacked and used for `nrows` and `ncols` for `plt.subplots()`.

        title : str, optional
            If not `None`, it will be used by `self._fig.suptitle(title)`.
                    
        layout : {'constrained', 'compressed', 'tight', 'none', LayoutEngine, None}, default='compressed'
            Layout of `self._fig`. 

        figsize : tuple[float,float] | None, default=None
            Used for `figsize` `plt.subplots()`.

        subplots_kw : dict, optional
            Other keyword arguments used by `plt.subplots()`.

        legend : bool | dict, optional
            Toggles legends for the plot. The keyword argument `label` must be passed to the plot, otherwise the legend is ignored. If a `dict` is passed then `legend` is used as keyword arguments for `ax.legend()`.

        Note
        ----
        If `plt.subplots()` with multiple axes, the axes array is flattened. This is done to facilitate simple itteration over the instance.
        
        Atributes
        ---------
        figure : matplotlib.figure.Figure 
            Figure used by the backend instance.
        
        subfigs : ndarray[Axes,...]
            Flat array of axes used by the backend instance.

        """

        self._id=id
        if ax is None and not fig:
            fig,ax=plt.subplots(*(subplots if subplots else (1,1)),figsize=figsize,**subplots_kw)

        self._fig=fig
        if isinstance(ax,np.ndarray):
            self._ax=ax.flatten() 
        elif isinstance(ax,mpl.axes.Axes):
            self._ax=np.array([ax])
        elif hasattr(ax,"__init__"):
            self._ax=np.asarray(ax)
        else:
            raise AttributeError("self._ax could not be set.")
        
        self._current_ax=self._ax[0]
        
        self._figsize=figsize
        self._bbox=None
        if title: self._fig.suptitle(title)
        self._fig.set_layout_engine(layout)
        self._legend=legend
    

    @property
    def figure(self): 
        "The `Figure` used for the plot."
        return self._fig

    @property
    def subfigs(self): 
        "The `Axes` for the plot."
        return self._ax
    
    def __getitem__(self,index):
        return self._ax[index]
    def __iter__(self):
        self._pos=-1
        self._stop=len(self._ax)-1
        return self
    def __next__(self):
        if self._pos == self._stop:
            raise StopIteration
        self._pos+=1
        return self._ax[self._pos]

    def gca(self):
        "Returns the current axis being used."
        return self._current_ax
    
    def sca(self,ax):
        "Sets the the provided axis to be the current axis."
        self._current_ax=ax
        plt.sca(ax)

    def return_fig(self):
        "Returns the the figure and the axes."
        return self._fig,self._ax
    
    def get_title(self):
        "Returns the title of the figure as a `str`."
        return self._fig._suptitle.get_text()

    def set_title(self,t,**kwargs):
        """Sets the title of the figure.
        
        Parameters
        ----------
        t : str
            The text for the plot.

        **kwargs
            Keyword arguments used by `fig.suptitle()`.
        
        Returns
        -------
        Text
            A `matplotlib.text.Text` object.

        """
        return self._fig.suptitle(t,**kwargs)
    
    def get_subtitle(self,ax=None):
        """Gets the title of an axis.

        Parameters
        ----------
        ax : Axes | None, optional
            If `None` the current axis is used.

        Returns
        -------
        str

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        return ax.get_title()

    def set_subtitle(self,label,loc=None,pad=None,*,y=None,ax=None,**kwargs):
        """Sets the lable for an axis.
        
        Parameters
        ----------
        label : str
            The title for the axis.

        loc : {"center", "left", "right"}, optional
            Location of the title.

        pad : float, optional
            The position of the label.
            
        y : float, optional
            Y position of the title
        
        ax : Axes | None, optional
            Padding in points from the axis.

        **kwargs
            Keyword arguments used by `ax.set_title()`

        Returns
        -------
        Text
            A `matplotlib.text.Text` object.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)

        return ax.set_title(label,loc,pad,y=y,**kwargs)
    
    def get_xlabel(self,ax=None):
        "Returns the label of the xaxis of the current or specified axis."
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
            
        return ax.xaxis.get_label()

    def set_xlabel(self,xlabel,labelpad=None,*,loc=None,ax=None,**kwargs):
        """Sets the label of the xaxis.
        
        Parameters
        ----------
        xlabel : str
            The label that will be placed on the xaxis.

        labelpad : float, optional
            The padding in points of the label from the xaxis.

        loc :  {"center", "left", "right"}, optional
            The position of the label.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **kwargs
            Keyword arguments used by `ax.set_xlabel()`.

        Returns
        -------
        Text
            A `matplotlib.text.Text` object.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        return ax.set_xlabel(xlabel,labelpad,loc=loc,**kwargs)
    
    def get_ylabel(self,ax=None,**kwargs):
        "Returns the label of the yaxis of the current or specified axis."
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
            
        return ax.yaxis.get_label()

    def set_ylabel(self,ylabel,labelpad=None,*,loc=None,ax=None,**kwargs):
        """Sets the label of the yaxis.
        
        Parameters
        ----------
        ylabel : str
            The label that will be placed on the yaxis.

        labelpad : float, optional
            The padding in points of the label from the yaxis.

        loc :  {"center", "bottom", "top"}, optional
            The position of the label.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **kwargs
            Keyword arguments used by `ax.set_ylabel()`.

        Returns
        -------
        Text
            A `matplotlib.text.Text` object.
        
        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        return ax.set_ylabel(ylabel,labelpad,loc=loc,**kwargs)

    def set_xticks(self,xticks,labels=None,*,minor=False,ax=None,**kwargs):
        """Sets the xticks.
        
        Parameters
        ----------
        xticks : array-like
            1D of the tick locations.

        labels : list[str,...], optional
            List of labels of all ticks.

        minor : bool, optional
            Toggles if minor ticks are included

        **kwargs
            Keyword arguments used by `ax.set_xticks()`.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        ax.set_xticks(xticks,labels,minor=minor,**kwargs)

    
    def set_yticks(self,yticks,labels=None,*,minor=False,ax=None,**kwargs):
        """Sets the yticks.
        
        Parameters
        ----------
        yticks : array-like
            1D of the tick locations.

        labels : list[str,...], optional
            List of labels of all ticks.

        minor : bool, optional
            Toggles if minor ticks are included

        **kwargs
            Keyword arguments used by `ax.set_yticks()`.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        ax.set_yticks(yticks,labels,minor=minor,**kwargs)


    def set_aspect(self,aspect,adjustable=None,anchor=None,share=False,ax=None):
        """Sets relative spacing of y to x data.
        
        Parameters
        ----------
        aspect : {"auto","equal"} | float
            The aspect ratio to be set. If a `float` is passed than the aspect ratio will be 1:`aspect`.

        adjustable : {"box","datadim"}, optional
            Used to specify which parameter will be changed.

        anchor : str | (float,float), optional
            Defines where the axis is drawn.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.
        
        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)

        ax.set_aspect(aspect,adjustable,anchor,share)

        
    def set_grid(self,visible=None,which='major',axis='both',ax=None,**kwargs):
        """Sets grid lines for the axis
        
        Parameters
        ----------
        visible : bool | None, default=None
            If keyword arguments are passed `visible` is assumed to be `True`. If `visible` is `None` and no keyword arguments are passed the current state is toggled.

        which : {"major", "minor", "both"}, optional
            Which grid lines are being changed.

        axis : {"both", "x", "y"}, optional
            Which axis' grid lines are being changed.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **kwargs
            Keyword arguments used by `ax.grid()`.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        ax.grid(visible,which,axis,**kwargs)

    def get_bbox(self,ax=None):
        "Returns the xlim and ylim of the axis."
        if self._bbox:
            return self._bbox
        else:
            if ax is None: ax=self.gca()
            xlim=ax.get_xlim()
            ylim=ax.get_ylim()
            return (xlim[0],ylim[0],xlim[1],ylim[1])
        
    def set_bbox(self,bbox,ax=None):
        """Sets the xlim and ylim of the plot.
        
        Parameters
        ----------
        bbox : list[x0,y0,x1,y1] | None, optional
            typing.Iterable containing x0,y0,x1,y1 where point 0 is the bottem left and point 1 is the top right of the bounding box.
        
        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.
        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        
        ax.set(xlim=(bbox[0],bbox[2]),ylim=(bbox[1],bbox[3]))

    def set(self,ax=None,**plot_kw):
        "Calls ax.set()"
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        ax.set(**plot_kw)

    def link_subplots(self,ax1,*ax2,sharex=True,sharey=True):
        if ax2 is None:
            parent_ax:plt.Axes=self.gca()
            child_axs=(ax1,)
        else:
            parent_ax=ax1
            child_axs=ax2

        for ax in child_axs:
            if sharex: ax1._shared_axes["x"].join(parent_ax,ax)
            if sharey: ax1._shared_axes["y"].join(parent_ax,ax)
            
    #[ ]Utilize bbox's to trim all data types.
    #[ ]Rework to include standard ax.plot() call sigs.
    def line(self,points,*args,T=True,ax=None,**linekwargs):
        """Calls ax.plot()
        
        Parameters
        ----------
        Points : np.ndarray
            Array of x and y coordinates. Array should have shape (2,n)

        T : bool, default=True
            If `True` the points array is transposed. Used for arrays with shape (n,2)

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        *args 
            Arguments passed to ax.plot()

        **linekwargs
            Keyword arguments passed to ax.plot()
        
        Returns
        -------
        list[Line2d,...]
            The line artists for the data.

        """
        plt.plot()
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        if T:
            points=points.T
        return ax.plot(*points,*args,**linekwargs)
    
    #[ ]Rework to include standard ax.scatter() call sigs.
    def scatter(self,points,*args,T=True,ax=None,**scatterkwargs):
        """Calls ax.scatter()
        
        Parameters
        ----------
        Points : np.ndarray
            Array of x and y coordinates. Array should have shape (2,n).

        T : bool, default=True
            If `True` the points array is transposed. Used for arrays with shape (n,2).

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        *args 
            Arguments passed to ax.scatter().

        **scatterkwargs
            Keyword arguments passed to ax.scatter().
        
        Returns
        -------
        PathCollections
            Collection of scatter paths.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)

        if T:
            points=points.T
        return ax.scatter(*points,*args,**scatterkwargs)

    #[ ] def line3d():

    def triplot(self,*meshdata,bbox=None,ax=None,**trikwargs):
        """Call ax.triplot()
        
        Parameters
        ----------
        *meshdata : triangulation | np.ndarray,np.ndarray
            matplotlib triangulation of the grid or raw nodes and elemcomps.

        bbox : list[x0,y0,x1,y1] | None, optional
            typing.Iterable containing x0,y0,x1,y1 where point 0 is the bottem left and point 1 is the top right of the bounding box.
        
        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **trikwargs
            Keyword arguments passed to ax.triplot().

        Returns 
        -------
        Lines : Line2d
            Lines generated by ax.triplot().

        Markers : Line2d
            The markers at each node.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        if bbox is None: bbox=self._bbox
        
        if not isinstance(meshdata[0],Triangulation):
            mesh=Triangulation(meshdata[0][:,0],meshdata[0][:,1],meshdata[1])
        else:
            mesh=meshdata[0]
            
        if np.any(bbox):
            mesh=tri_bbox_prep(mesh,bbox)

        return ax.triplot(mesh,**trikwargs)
    
    #[ ] Decht this
    def contour(self,vals,mesh,bbox=None,fill=True,limits=None,levels=101,ax=None,**conkwargs):
        """Calls ax.contour() or ax.contourf().

        Parameters
        ----------
        vals : np.ndarray
            2d array of shape(ni,nj) coresponding to the mesh.
    
        mesh : np.ndarray
            Array containing xv and yv arrays generated from a np.meshgrid().
        
        bbox : list[x0,y0,x1,y1] | None, optional
            typing.Iterable containing x0,y0,x1,y1 where point 0 is the bottem left and point 1 is the top right of the bounding box.

        fill : bool, default=True 
            If True, contourf is called. If False, contour is called.

        limits : list[lower,upper] | None, optional
            A list of the lower and upper values of the contour.

        levels : int, default=101
            The number of countor levels that will be generated.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **conkwargs
            Keyword arguments passed to `ax.contour()` or `ax.contourf()`.

        Returns
        -------
        QuadContourSet    
            Gridded contour set.
        
        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        if bbox is None: bbox=self._bbox
            
        if np.any(bbox):
            mesh,vals=meshgridcut(mesh,bbox,vals=vals)

        if not limits:
            low=np.min(vals)
            high=np.max(vals)
            levels=np.linspace(low,high,101,endpoint=True)
        else:
            levels=conkwargs.pop("levels")
        conkwargs.pop("emptyval",None)
        #Creates the filled contour to be plotted.
        if fill: 
            cm=ax.contourf(mesh[0],mesh[1],vals,levels=levels,**conkwargs)
            #conlabel=False
        else: cm=ax.contour(mesh[0],mesh[1],vals,levels=levels,**conkwargs)

        return cm
    
    #[ ] Decht this
    def tricontour(self,vals,*meshdata,bbox=None,fill=True,limits=None,levels=101,emptyval=None,ax=None,**triconkwargs):
        """Calls ax.tricontour() or ax.tricontourf().

        Parameters
        ----------
        vals : np.ndarray
            Array containing data to be plotted.
    
        *meshdata : triangulation | np.ndarray,np.ndarray
            matplotlib triangulation of the grid or raw nodes and elemcomps.
        
        bbox : list[x0,y0,x1,y1] | None, optional
            typing.Iterable containing x0,y0,x1,y1 where point 0 is the bottem left and point 1 is the top right of the bounding box.

        fill : bool, default=True 
            If True, tricontourf is called. If False, tricontour is called.

        limits : list[lower,upper] | None, optional
            A list of the lower and upper values of the contour.

        levels : int, default=101
            The number of countor levels that will be generated.

        emptyval : float | None, optional
            Value that will be masked out before the plot.

        ax : Axes | None, optional
            `Axes` to plot onto. If `None` self.gca() is called.

        **triconkwargs
            Keyword arguments passed to `ax.tricontour()` or `ax.tricontourf()`.

        Returns
        -------
        TriCountourSet
            Triangulated contour set.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        if bbox is None: bbox=self._bbox

        if not isinstance(meshdata[0],Triangulation):
            mesh=Triangulation(meshdata[0][:,0],meshdata[0][:,1],meshdata[1])
        else:
            mesh=meshdata[0]
        
        if np.any(bbox):
            mesh,valsstats=tri_bbox_prep(mesh,bbox,vals=vals)
            valsstats=valsstats[valsstats!=emptyval]
        else:
            valsstats=vals[vals!=emptyval]
        if not limits:
            low=np.min(valsstats)
            high=np.max(valsstats)
            mesh.set_mask(np.all(np.isin(mesh.triangles,np.asarray(vals==emptyval).nonzero()),axis=1))
        else:
            low=limits[0]
            high=limits[1]
        levels=np.linspace(low,high,levels,endpoint=True)
        #Creates the filled contour to be plotted.
        if fill: cm=ax.tricontourf(mesh,vals,levels=levels,**triconkwargs)
        else: cm=ax.tricontour(mesh,vals,levels=levels,**triconkwargs)

        return cm

    def hist(self,vals,bins,cmap=None,valsrange=None,emptyval=-99999,ax=None,**histkwargs):
        """Calls `ax.hist()`.
        
        Parameters
        ----------
        vals : np.ndarray
            Array containing data to be plotted.

        bins : int | list | {"auto", "fd", "doane", "scott", "stone", "rice", "sturges", "sqrt"}
            Tells `ax.hist()` how to bin the data. If `bins` is an `int` it is the number of bins used. If it is a `list` it is the edges used by each bin including the extreme left and right edges. Stings used by `np.histogram_bin_edges` can also be used.

        cmap : Colormap | None, optional
            If a Colormap is provided each patch in the histogram has its facecolor changed to its relative color in `cmap`.
        
        bbox : list[x0,y0,x1,y1] | None, optional
            typing.Iterable containing x0,y0,x1,y1 where point 0 is the bottem left and point 1 is the top right of the bounding box.

        valsrange : list[float,float] | None, optoinal
            If provided, only values with [valsrange[0],valsrange[1]] will be plotted.

        emptyval : float | None, default=-99999
            Value that will be masked out before the plot.

        ax : Axes | None, optional
           `Axes`to plot onto. If `None` self.gca() is called.

        **histkwargs
            Keyword arguments passed to `ax.hist()`.
        
        Returns
        -------
        n : np.ndarray | list[np.ndarray,...]
            Value of each bin.

        bins : np.ndarray 
            Edges of each bin.

        patches : BarContainer | list[Polygon,...]
            The artists used in the plot.

        """
        if ax is None:
            ax=self.gca()
        else:
            self.sca(ax)
        if valsrange:
            vals=vals[vals>=valsrange[0]]
            vals=vals[vals<=valsrange[1]]
        n,bins,patches=ax.hist(vals[vals!=emptyval],bins,**histkwargs)

        if cmap:
            frac=n.size
            cmap=plt.get_cmap(cmap)

            for f,patch in enumerate(patches):
                patch.set_facecolor(cmap(f/frac))

        return (n,bins,patches)
    
    def cbar(self,mappable,cax=None,ax=None,label=None,label_kwargs={},**colorbarkwargs):
        """Calls plt.colorbar().
        
        Parameters
        ----------
        mappable : ScalarMappable
            A mappable object that will be used by the colorbar.

        cax : Axes | None, optional
            `Axes` to place the colorbar. If `None` a new `Axes` is created from the current `Axes`.

        ax : Axes | None, optional
           `Axes`to plot onto. If `None` self.gca() is called.

        label : str | None, optional
            Adds a label to the colorbars y axis.

        label_kwargs : dict, optional
            Keyword arguments used by `cbar.ax.set_ylabel()`. `rotation` `labelpad` are set to 90 and 18 by default.
        
        **colorbarkwargs
            Keyword arguments used by `plt.colorbar()`.

        Returns
        -------
        Colorbar
            The generated Colorbar instance.
        """
        if ax is None:
            ax=self.gca()
        elif isinstance(ax,np.ndarray):
            self.sca(ax[0])
        else:
            self.sca(ax)
        cbar=plt.colorbar(mappable,cax=cax,ax=ax,**colorbarkwargs)
        if label: cbar.ax.set_ylabel(label,**{**{"rotation":90,"labelpad":18},**label_kwargs})
        return cbar
        
    """ def show(self,*args,**kwargs):
        if self._legend:
            for axn in self._ax:
                if not axn.get_legend_handles_labels() == ([], []):
                    axn.legend(**self._legend if isinstance(self._legend,dict) else {})
            
        plt.show(*args,**kwargs) """

    def savefig(self,path,dpi=None):
        """Calls `fig.savefig()`.
        
        Parameters
        ----------
        path : str | PathLike
            Path that the file will be saved to.

        dpi : int | None, optional
            DPI of the saved image.
        
        """
        if self._legend:
            for axn in self._ax:
                if not axn.get_legend_handles_labels() == ([], []):
                    axn.legend(**self._legend if isinstance(self._legend,dict) else {})

        self._fig.set_dpi(dpi)
        return self._fig.savefig(path,dpi=dpi)

