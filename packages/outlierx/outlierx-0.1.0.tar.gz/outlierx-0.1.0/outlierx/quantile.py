import numpy as np
from .core import to_numpy

def detect_quantile(data, lower_q=0.01, upper_q=0.99, return_index=False):
    """
    Detect outliers using quantile thresholds.

    Parameters:
        data : array-like
        lower_q : float
        upper_q : float
        return_index : bool

    Returns:
        outliers or (outliers, indices)
    """
    arr = to_numpy(data)

    lower = np.quantile(arr, lower_q)
    upper = np.quantile(arr, upper_q)

    mask = (arr < lower) | (arr > upper)

    if return_index:
        return arr[mask], np.where(mask)[0]

    return arr[mask]
