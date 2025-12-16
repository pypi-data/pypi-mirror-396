import numpy as np
from .core import to_numpy

def detect_iqr(data, factor=1.5, return_index=False):
    """
    Detect outliers using Interquartile Range (IQR).

    Parameters:
        data : array-like
        factor : float (default=1.5)
        return_index : bool

    Returns:
        outliers or (outliers, indices)
    """
    arr = to_numpy(data)

    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1

    lower = q1 - factor * iqr
    upper = q3 + factor * iqr

    mask = (arr < lower) | (arr > upper)

    if return_index:
        return arr[mask], np.where(mask)[0]

    return arr[mask]
