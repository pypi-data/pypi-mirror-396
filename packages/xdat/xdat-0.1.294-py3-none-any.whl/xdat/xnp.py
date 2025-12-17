import numpy
import numpy as np
import pandas as pd
try:
    import accupy
except (ImportError, ModuleNotFoundError):
    pass

from . import xsettings


def x_sum(a, accu_method=None):
    """
    A much slower, but more accurate sum routine
    (see https://github.com/nschloe/accupy)
    """

    accu_method = xsettings.get_default(xsettings.ACCU_METHOD, accu_method)

    if accu_method == 'fsum':
        aa = accupy.fsum(a)
    elif accu_method == 'ksum':
        aa = accupy.ksum(a)
    elif accu_method == 'kahan_sum':
        aa = accupy.kahan_sum(a)
    else:
        raise ValueError(accu_method)

    return aa


def x_dot(a1, a2):
    """
    A much slower, but more accurate dot product
    (see https://github.com/nschloe/accupy)
    """
    a1 = a1.astype(float)
    a2 = a2.astype(float)
    return accupy.fdot(a1, a2)


def x_mean_date(list_of_dates):
    """
    Given list of dates, calculates the mean.
    Credit: https://stackoverflow.com/questions/50358564/computing-the-mean-for-python-datetime
    """

    a = numpy.array(list_of_dates)
    a = a[~numpy.isnan(a)]
    mean_date = pd.to_datetime(a.astype(numpy.int64).mean()).to_numpy()
    return mean_date


def x_median_date(list_of_dates):
    """
    Given list of dates, calculates the median.
    """

    a = numpy.array(list_of_dates)
    a = a[~numpy.isnan(a)]
    mean_date = pd.to_datetime(np.median(a.astype(numpy.int64))).to_numpy()
    return mean_date


def x_consec_repeat_starts_with_overlap(a, consec_exact_len):
    """
    Credits: https://stackoverflow.com/questions/59662725/find-consecutive-repeats-of-specific-length-in-numpy
    Given array (a) & exact consecutive len, return indexes where such consecutive vals appear, but WITH OVERLAP
    """

    N = consec_exact_len - 1
    m = a[:-1]==a[1:]
    return np.flatnonzero(np.convolve(m, np.ones(N, dtype=int))==N)-N+1


def x_consec_repeat_starts(arr, consec_min_len):
    res = np.ones_like(arr)
    np.bitwise_xor(arr[:-1], arr[1:], out=res[1:])  # set equal, consecutive elements to 0
    # use this for np.floats instead
    # arr = np.array([0, 3, 0, 1, 0, 1, 2, 1, 2.4, 2.4, 2.4, 2, 1, 3, 4, 4, 4, 5])
    # res = np.hstack([True, ~np.isclose(arr[:-1], arr[1:])])
    idxs = np.flatnonzero(res)  # get indices of non zero elements
    values = arr[idxs]
    counts = np.diff(idxs, append=len(arr))  # difference between consecutive indices are the length

    cond = counts >= consec_min_len
    df = pd.DataFrame({'value': values[cond], 'num_consec': counts[cond], 'index_start': idxs[cond]})
    return df


def x_rmse(a1, a2):
    return np.sqrt(np.mean((a1 - a2)**2))


def monkey_patch():
    numpy.x_sum = x_sum
    numpy.x_dot = x_dot
    numpy.x_mean_date = x_mean_date
