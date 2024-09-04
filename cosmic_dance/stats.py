import numpy as np
import pandas as pd


def get_CDF(data: pd.Series) -> tuple[np.array, np.array]:
    '''Get X and Y axis values for Cumulative distribution function

    Params
    ------
    data: pd.Series
        List of data points

    Returns
    -------
    tuple[np.array, np.array] X and Y axis values
    '''

    x = np.sort(data)
    y = np.arange(len(data)) / float(len(data))
    return x, y


def percentile(df: pd.Series, percentiles: list[float]) -> list[float]:
    '''Get list of percentiles of given list of numbers (intensities)

    Params
    ------
    df: pd.Series
        List of data points
    percentiles: list[float]
        List of percentiles

    Returns
    -------
    list[float]: Corresponding value of list[float] 
    '''

    return np.percentile(df, percentiles)
