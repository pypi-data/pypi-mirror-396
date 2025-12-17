# -*- coding: utf-8 -*-
from pandas import DataFrame

def check_is_dataframe(
        X
):
    """
    Performs is_dataframe validation

    Check if X is an instance of class pd.DataFrame

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_columns)
        Input data for which check should be done
    """
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #check if X is an instance of class pd.DataFrame
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if not isinstance(X,DataFrame):
        raise TypeError(f"{type(X)} is not supported. Please convert to a DataFrame with pd.DataFrame. For more information see: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    else:
        pass