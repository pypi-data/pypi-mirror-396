import numpy as np
import pandas as pd

def to_numpy(data):
    """
    Converts input data to numpy array.
    Supports list, tuple, numpy array, pandas Series.
    """
    if isinstance(data, (list, tuple)):
        return np.array(data, dtype=float)
    if isinstance(data, pd.Series):
        return data.values.astype(float)
    if isinstance(data, np.ndarray):
        return data.astype(float)

    raise TypeError(
        "Data must be list, tuple, numpy array, or pandas Series"
    )
