"""Manage I/O for connectivity functions."""
import numpy as np
import xarray as xr


from frites.io import set_log_level, logger


def conn_io(da, roi=None, times=None, verbose=None):
    """I/O conversion for connectivity functions.

    Parameters
    ----------
    da : array_like
        Array of electrophysiological data of shape (n_trials, n_roi, n_times)
    roi : array_like | None
        List of roi names or string corresponding to the dimension name in a
        DataArray
    times : array_like | None
        Time vector or string corresponding to the dimension name in a
        DataArray
    """
    set_log_level(verbose)
    assert isinstance(da, np.ndarray) or isinstance(da, xr.DataArray)
    assert da.ndim == 3
    n_trials, n_roi, n_times = da.shape
    logger.info(f"Inputs conversion (n_trials={n_trials}, n_roi={n_roi}, "
                "n_times={n_times})")

    # _____________________________ Empty inputs ______________________________
    if roi is None:
        roi = [f"roi_{k}" for k in range(n_roi)]
    if times is None:
        times = np.arange(n_times)

    # _______________________________ Xarray case _____________________________
    if isinstance(da, xr.DataArray):
        # get roi and times
        if isinstance(roi, str):
            roi = da[roi].data
        if isinstance(times, str):
            times = da[times].data
        da = da.data

    # _______________________________ Final check _____________________________
    assert isinstance(da, np.ndarray)
    assert da.shape == (n_trials, len(roi), len(times))

    return da, roi, times
