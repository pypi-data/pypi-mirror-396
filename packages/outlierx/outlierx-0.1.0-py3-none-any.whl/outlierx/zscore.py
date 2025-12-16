import numpy as np
from .core import to_numpy

def detect_zscore(data, threshold=3.0, return_index=False):
    """
    Detect outliers using Z-score.

    Parameters:
        data : array-like
        threshold : float
        return_index : bool

    Returns:
        outliers or (outliers, indices)
    """
    arr = to_numpy(data)

    mean = np.mean(arr)
    std = np.std(arr)

    if std == 0:
        return [] if not return_index else ([], [])

    z_scores = (arr - mean) / std
    mask = np.abs(z_scores) > threshold

    if return_index:
        return arr[mask], np.where(mask)[0]

    return arr[mask]
