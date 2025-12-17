# -*- coding: utf-8 -*-
from numpy import fill_diagonal, nan, triu, tril_indices, tril, triu_indices, array, zeros,where,abs
from pandas import DataFrame, Categorical
from pandas.api.types import is_numeric_dtype
from scipy.stats import pearsonr
from plotnine import ggplot, aes, theme, element_blank, theme_minimal,element_text,geom_point,geom_text,ggtitle,geom_tile,scale_size_continuous,guides,scale_fill_gradient2,coord_fixed
from collections import OrderedDict
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform

#interns functions
from .utils import check_is_dataframe

def get_melt(
        X
):
    """
    Stack DataFrame

    Pivot data from wide to long

    Parameters
    ----------
    X : DataFrame of shape (n_rows, n_columns)
        Input data.

    Returns
    -------
    Y : DataFrame of shape (n_rows*n_columns, 3)
        Stacked data.

    Examples
    --------
    >>> from plotnine.data import mtcars
    >>> from ggcorrplot import get_melt
    >>> mtcars = mtcars.set_index("name") # set name as index
    >>> mtcars_long = get_melt(mtcars)
               name Variable  value
    0     Mazda RX4      mpg   21.0
    1     Mazda RX4      cyl    6.0
    2     Mazda RX4     disp  160.0
    3     Mazda RX4       hp  110.0
    4     Mazda RX4     drat    3.9
    ..          ...      ...    ...
    347  Volvo 142E     qsec   18.6
    348  Volvo 142E       vs    1.0
    349  Volvo 142E       am    1.0
    350  Volvo 142E     gear    4.0
    351  Volvo 142E     carb    2.0
    """
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if X is an object of class pd.DataFrame
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    check_is_dataframe(X)
    return X.stack().rename_axis(('Var1', 'Var2')).reset_index(name='value')

def hc_cormat_order(
        cormat, method='complete'
):
    """
    Hierarchy order

    Parameters
    ----------
    X : DataFrame of shape (n_rows, n_columns)
        Correlation matrix.

    Returns
    -------
    res : OrderedDict
        Hierarchy order informations
    """
    #check if cormat is an object of class pd.DataFrame
    check_is_dataframe(cormat)
    #from correlation matrix to distance matrix
    X = (1-cormat)/2
    Z = hierarchy.linkage(squareform(X),method=method,metric="euclidean")
    order = hierarchy.leaves_list(Z)
    return OrderedDict(order=order,height=Z[:,2],method=method,merge=Z[:,:2],n_obs=Z[:,3],data=cormat)

def match_arg(
        x, lst
):
    """
    Match arguments

    Parameters
    ----------
    x : 

    lst : list
        List in which to match

    Returns
    -------

    """
    return [el for el in lst if x in el][0]

def no_panel():
    """
    Remove panel to ggplot
    """
    return theme(axis_title_x=element_blank(),axis_title_y=element_blank())

def remove_diag(
        cormat
):
    """
    Remove diagonal

    Parameters
    ----------
    cormat : DataFrame of shape (n_columns, n_columns)
        Correlation matrix.

    Returns
    -------
    cormat : DataFrame of shape (n_columns, n_columns)
        Correlation matrix where diagonal is replace by NA.    
    """
    if cormat is None:
        return cormat
    
    #check if cormat is an object of class pd.DataFrame
    check_is_dataframe(cormat)
    #off diagonal
    fill_diagonal(cormat.values, nan)
    return cormat

def get_upper_tri(
        cormat,show_diag=False
):
    """
    Get upper tri 

    Parameters
    ----------
    cormat : DataFrame of shape (n_columns, n_columns)
        Correlation matrix

    show_diag : bool, default = False
        if True, add diagonal to upper triangle matrix.

    Returns
    -------
    cormat : DataFrame of shape (n_columns, n_columns)
        Upper triangular correlation matrix.
    """
    if cormat is None:
        return cormat
    
    #check of cormat is an object of class pd.DataFrame
    cormat = DataFrame(triu(cormat),index=cormat.index,columns=cormat.columns)
    cormat.values[tril_indices(cormat.shape[0], -1)] = nan
    #off diag
    if not show_diag:
        fill_diagonal(cormat.values,nan)
    return cormat

def get_lower_tri(
        cormat,show_diag=False
):
    """
    Get lower tri

    Parameters
    ----------
    cormat : DataFrame of shape (n_columns, n_columns)
        Correlation matrix

    show_diag : bool, default = False
        if True, add diagonal to lower triangular matrix.

    Returns
    -------
    cormat : DataFrame of shape (n_columns, n_columns)
        Lower triangular correlation matrix.
    """
    if cormat is None:
        return cormat
    
    #check if cormat is an object of class pd.DataFrame
    cormat = DataFrame(tril(cormat),index=cormat.index,columns=cormat.columns)
    cormat.values[triu_indices(cormat.shape[0], 1)] = nan
    #off-diagonal to lower triangular matrix
    if not show_diag:
        fill_diagonal(cormat.values,nan)
    return cormat

def cor_pmat(
        X,**kwargs
):
    """
    Compute a correlation matrix p-values

    Parameters
    ----------
    X : Dataframe of shape (n_rows, n_columns)
        Input data.

    **kwargs : 
        Others arguments to be passed to the function `scipy.stats.pearsonr <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html>`_.

    Return
    ------
    p_mat : Dataframe of shape (n_columns, n_columns)
        The p-value associated.
    """
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if X is an object of class pd.DataFrame
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    check_is_dataframe(X)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check all columns are numerics
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not all(is_numeric_dtype(X[k]) for k in list(X.columns)):
        raise TypeError("All columns in X must be numerics")


    y = array(X)
    n = y.shape[1]
    p_mat = zeros((n,n))
    fill_diagonal(p_mat,0)
    for i in range(n-1):
        for j in range(i+1,n):
            tmps = pearsonr(y[:,i],y[:,j],**kwargs)
            p_mat[i,j] = p_mat[j,i] = tmps[1]
    return DataFrame(p_mat,index=X.columns,columns=X.columns)

def ggcorrplot(
        X,
        matrix_type = "correlation",
        method = "square",
        type = "full",
        title = None,
        show_legend = True,
        legend_title = "Corr",
        show_diag = None,
        colors = ("blue","white","red"),
        outline_color = "gray",
        hc_order = False,
        hc_method = "complete",
        label = False,
        label_color = "black",
        lab_size = 11,
        p_mat = None,
        sig_level=0.05,
        insig = "pch",
        pch = "x",
        pch_color = "black",
        pch_cex = 5,
        tl_cex = 12,
        tl_color = "black",
        tl_srt = 45,
        xtickslab_rotation = 45,
        digits = 2,
        ggtheme = None
):
    """
    Visualization of a correlation matrix using ggplot

    A graphical display of a correlation matrix using plotnine
    
    Parameters
    ----------
    X : DataFrame of shape (n_rows, n_columns) or (n_columns, n_columns)
        Input data. Original data or correlation matrix.

    matrix_type : str, default = 'correlation'
        Which matrix in input. Possible values are: "correlation" (default) or "completed"

    method : str, default = 'square'
        the visualization method of correlation matrix to be used. Possible values are "square", "circle".

    type : str, default = 'full'
        Which correlation matrix to use. Possible values are : "full" (default), "lower" or "upper" display.

    title : str, 
        Title of the graph

    show_legend : bool, default = True
        If True, the legend is displayed.

    legend_title : str, default = "Corr"
        The legend title. lower triangular, upper triangular or full matrix.

    show_diag : None or bool, default = None
        Whether display the correlation coefficients on the principal diagonal. If None, the default is to show diagonal correlation for type = "full" and to remove it when type is one of "upper" or "lower".
    
    colors : list or tuple, default = ("blue","white","red")
        3 colors for low, mid and high correlation values

    outline_color : str, default = 'gray'
        The outline color of square or circle.

    hc_order : bool, default = False
        If True, correlation matrix will be hc_ordered using `scipy.cluster.hierarchy.linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html#scipy.cluster.hierarchy.linkage>`_ function.

    hc_method : str, default = 'complete'
        The agglomeration method to be used in `scipy.cluster.hierarchy.linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html#scipy.cluster.hierarchy.linkage>`_.

    label : bool, default = False. 
        If True, add correlation coefficient on the plot.

    label_color : str, default = 'black' 
        Color to be used for the correlation coefficients labels. Used when label = True.

    label_size : int, default = 11
        Size to be used for the correlation coefficients labels. Used when label = True.

    p_mat : DataFrame of shape (n_columns, n_columns)
        Matrix of correlation p-value. If None, arguments sig_level, insig, pch, pch_col, pch_ces is invalid.

    sig_level : float, default = 0.05
        Significant level, if the p-value in p_mat is bigger than sig_level, then the corresponding correlation coefficient is regarded as insignificant.

    insig : str, default = 'pch'
        Specialized insignificant correlation coefficients, "pch" (default), "blank". If "blank" wipe away the corresponding glyphs. if "pch", add characters (see pch for details) on corresponding glyphs
        
    pch : str, default = 'x'
        Add character on the glyphs of insignificant correlation coefficients (only valid when insig is "pch"). Default value is 'x'.

    pch_color : str, default = 'black'
        the color of pch (only valid when insig is "pch").
    
    pch_cex : int, default = 5
        the cex (size) of pch (only valid when insig is "pch").

    tl_cex : int, default = 12
        The size  of text label (variable names).

    tl_color : str, default = 'black'
        The color of text label (variable names).

    tl_srt : int, default = 45
        The rotation of text label (variable names).

    xtickslab_rotation : int, default = 45
        X-ticks rotation angle.

    digits : float, default = 2
        Decides the number of decimal digits to be displayed.

    ggtheme : function, default = None
        Plotnine `theme <https://plotnine.org/guide/themes-basics.html>`_ name.

    Returns
    -------
    a ggplot graph

    Examples
    --------
    >>> from plotnine.data import mtcars
    >>> from ggcorrplot import ggcorrplot
    >>> mtcars = mtcars.set_index("name") # set name as index
    >>> #with correlation matrix
    >>> p = ggcorrplot(mtcars.corr())
    >>> p
    >>> #with original data
    >>> p = ggcorrplot(mtcars, matrix_type = "completed")
    >>> p 
    """
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if X is an object of class pd.DataFrame
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    check_is_dataframe(X)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if matrix_type not in ["completed","correlation"]
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not isinstance(matrix_type,str):
        raise TypeError("'matrix_type' should be a string")
    elif matrix_type not in ["completed","correlation"]:
        raise ValueError("'matrix_type' should be one of 'completed', 'correlation'")

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if p_mat is an object of class pd.DataFrame
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if p_mat is not None:
        #check if p_mat is a pandas dataframe
        check_is_dataframe(p_mat)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if type in ["full", "lower", "upper"]
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not isinstance(type,str):
        raise TypeError("'type' should be a string")
    elif type not in ["full","lower","upper"]:
        raise ValueError("'type' should be one of 'full','lower', 'upper'")
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if method in ["square","circle"]
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not isinstance(method,str):
        raise TypeError("'method' sould be a string")
    elif method not in ["square","circle"]:
        raise ValueError("'method' should be one of 'square', 'circle'")
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if insig in ["pch", "blank"]
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not isinstance(insig,str):
        raise TypeError("'insig' should be a string")
    elif insig not in ["pch","blank"]:
        raise ValueError("'insig' should be one of 'pch', 'blank'")

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #set type
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if show_diag is None:
        if type == "full":
            show_diag = True
        else:
            show_diag = False
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #compute correlation matrix
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if matrix_type == "completed":
        corr = X.corr(method="pearson").round(decimals=digits)
    elif matrix_type == "correlation":
        corr = X.round(decimals=digits)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #hierarchical clustering
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if hc_order:
        ord = hc_cormat_order(corr,method=hc_method)["order"]
        corr = corr.iloc[ord,ord]
        if p_mat is not None:
            p_mat = p_mat.iloc[ord,ord]
            p_mat = p_mat.round(decimals=digits)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #remove diag
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not show_diag:
        corr = remove_diag(corr)
        if p_mat is not None:
            p_mat = remove_diag(p_mat)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #get lower or upper triangle
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if type == "lower":
        corr = get_lower_tri(corr,show_diag)
        if p_mat is not None:
            p_mat = get_lower_tri(p_mat,show_diag)
    elif type == "upper":
        corr = get_upper_tri(corr,show_diag)
        if p_mat is not None:
            p_mat = get_upper_tri(corr,show_diag)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #reshape corr and p_mat
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    corr.columns = Categorical(corr.columns,categories=corr.columns)
    corr.index = Categorical(corr.columns,categories=corr.columns)
    corr = get_melt(corr)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #set p_mat
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if p_mat is not None:
        p_mat = get_melt(p_mat)
        corr = corr.assign(
            coef = lambda x : x["value"],
            pvalue = p_mat["value"],
            signif = lambda x : where(x["pvalue"] <= sig_level,1,0)
        )
        #corr["coef"] = corr["value"]
        #corr["pvalue"] = p_mat["value"]
        #corr["signif"] = where(p_mat["value"] <= sig_level,1,0)
        p_mat = p_mat.query('value > @sig_level')
        if insig == "blank":
            corr = corr.assign(value = lambda x : x["value"]*x["signif"])
            #corr["value"] = corr["value"]*corr["signif"]

    corr = corr.assign(abs_corr = lambda x : 10*abs(x["value"]))
    #corr["abs_corr"] = 10*abs(corr["value"]) 

    #initialized graph
    p = ggplot(corr,aes(x="Var1",y="Var2",fill="value"))
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #modification based on method
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if method == "square":
        p = p + geom_tile(color=outline_color)
    elif method == "circle":
        p = p + geom_point(aes(size="abs_corr"),color=outline_color,shape="o") + scale_size_continuous(range=(4,10)) + guides(size=None)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #adding colors
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    p = p + scale_fill_gradient2(low = colors[0],high = colors[2],mid = colors[1],midpoint = 0,limits = [-1,1],name = legend_title)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #depending on the class of the object, add the specified theme
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if ggtheme is None:
        ggtheme = theme_minimal()
    p = p + ggtheme

    p = p + theme(
        axis_text_x = element_text(angle=tl_srt,va="center",size=tl_cex,ha="center",color=tl_color), 
        axis_text_y = element_text(size=tl_cex)
    ) + coord_fixed()

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #correlation label
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    corr_label = corr["value"].round(digits)
    if p_mat is not None and insig == "blank":
        ns = corr["pvalue"] > sig_level
        if sum(ns) > 0:
            corr_label[ns] = " "
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #matrix cell labels
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if label:
        p = p + geom_text(mapping=aes(x="Var1",y="Var2"),label = corr_label,color = label_color,size=lab_size)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #matrix cell
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if p_mat is not None and insig == "pch":
        p = p + geom_point(data = p_mat,mapping = aes(x = "Var1", y = "Var2"),shape = pch,size=pch_cex,color= pch_color)
    
    if title is not None:
        p = p + ggtitle(title=title)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #removing legend
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not show_legend:
        p =p+theme(legend_position=None)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #removing panel
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    p = p + no_panel()

    if xtickslab_rotation > 5:
        ha = "right"
    if xtickslab_rotation == 90:
        ha = "center"

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #rotation
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    p = p + theme(axis_text_x = element_text(rotation = xtickslab_rotation,ha=ha))

    return p