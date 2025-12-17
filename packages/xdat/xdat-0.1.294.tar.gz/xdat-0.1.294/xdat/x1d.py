import inspect
import datetime as dt
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np
from scipy.optimize import curve_fit, linear_sum_assignment
from scipy.spatial import distance
from scipy import signal
from munch import Munch as MunchDict

from . import xstats, xpd
from .xcache import x_memoize

DEFAULT_CURVE_FIT_FUNCS = [
    lambda x, a: a,
    lambda x, a, b: a + b*x,
    lambda x, a, b, c: a + b*x + c*x**2,
]

def butter_bandpass(lowcut, highcut, fs, order=5):
    return signal.butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


def butter_lowpass(cutOff, fs, order=5):
    nyq = 0.5 * fs
    normalCutoff = cutOff / nyq
    b, a = signal.butter(order, normalCutoff, btype='low', analog = True)
    return b, a

def butter_lowpass_filter(data, cutOff, fs, order=5):
    b, a = butter_lowpass(cutOff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


# def detrend_resample(y, factor, ret_trend=False):
#     trend = signal.resample_poly(y, 1, factor, padtype='reflect')
#     return trend
#     trend = signal.resample_poly(trend, factor, 1, padtype='reflect')
#     return trend
#
#     trend = signal.resample(trend, len(y))
#     if ret_trend:
#         return trend
#
#     y_de = y - trend
#     return y_de


def array_col_to_wide(df, array_col, prefix=None, n_jobs=1):
    if prefix is None:
        prefix = f"{array_col}"

    def get_row(row):
        a = row[array_col]
        del row[array_col]
        for idx, v in enumerate(a):
            row[f"{prefix}_{idx}"] = v
        return row

    all_rows = Parallel(n_jobs=n_jobs)(delayed(get_row)(r[1]) for r in tqdm(df.iterrows(), total=len(df)))
    df_all = pd.DataFrame(all_rows)
    return df_all


class CurveFit:
    def __init__(self, func, maxfev=500000):
        """
        func's params: x + params to fit
        eg: lambda x, a, b: a + b*x
        """

        self.func = func
        self.maxfev = maxfev
        self.params = list(inspect.signature(self.func).parameters)[1:]
        self.num_params = len(self.params)
        self.coefs = None
        self.cov = None
        self.x_train = None
        self.y_train = None
        self.y_pred = None
        self.stats = None

    def __str__(self):
        return f", ".join([f"{k}={round(v, 4)}" for k,v in zip(self.params, self.coefs)])

    @property
    @x_memoize
    def coefs_named(self):
        return MunchDict({k:v for k,v in zip(self.params, self.coefs)})

    def fit(self, y, x=None, sample_weight=None):
        y = np.array(y)
        if len(y) < 2:
            raise ValueError("can't fit when there isn't enough data")

        if x is None:
            x = np.arange(len(y))
        else:
            x = self.fix_x(x)

        self.x_train = x
        self.y_train = y

        sigma = None
        if sample_weight is not None:
            sigma = 1/sample_weight

        self.coefs, self.cov = curve_fit(self.func, x, y, maxfev=self.maxfev, sigma=sigma, absolute_sigma=False)
        self.y_pred = self.predict(x)
        self.stats = xstats.x_model_pred_stats(self.y_pred, y, k=self.num_params, is_classification=False)

    def predict(self, x):
        x = self.fix_x(x)
        y_pred = self.func(x, *self.coefs)
        if isinstance(y_pred, float) or len(y_pred) == 1:
            y_pred = np.ones(len(x)) * y_pred
        return y_pred

    def fit_predict(self, y, x=None):
        self.fit(y, x=x)
        return self.predict(self.x_train)

    def fix_x(self, x):
        if x is not None:
            try:
                type_x = type(x[0])
            except KeyError:
                type_x = type(x.iloc[0])

            if type_x in [pd.Timestamp, np.datetime64]:
                x = xpd.x_datetime_as_hours(x)

            x = np.array(x)

        return x


def x_best_curve_fit(y, funcs=None, x=None, maxfev=500000):
    if funcs is None:
        funcs = DEFAULT_CURVE_FIT_FUNCS[:]

    best_cf = None
    for func in funcs:
        cf = CurveFit(func, maxfev=maxfev)
        cf.fit(y, x=x)
        if best_cf is None or cf.stats.p_value < best_cf.stats.p_value:
            best_cf = cf

    return best_cf


def x_match_two_lists(a, b, include_no_matches=True):
    """
    Given two arrays of different lengths, finds the best matches (by value) between them.
    Returns a 2x[num matches] array of the indexes of the matches.
    If include_no_matches is True, it appends to the results the indexes that did not have a match, paired with None.
    """

    aa = np.array(a)
    bb = np.array(b)

    if str(aa.dtype).startswith('datetime'):
        aa = aa.astype(int)
        bb = bb.astype(int)

    aa = aa.reshape(-1, 1)
    bb = bb.reshape(-1, 1)

    dists = distance.cdist(aa, bb)
    a_idx, b_idx = linear_sum_assignment(dists)

    if include_no_matches:
        if len(a_idx) != len(a):
            b_idx = list(b_idx)
            a_idx = list(a_idx)
            for i in set(range(len(a))) - set(a_idx):
                a_idx.append(i)
                b_idx.append(None)

        if len(b_idx) != len(b):
            b_idx = list(b_idx)
            a_idx = list(a_idx)
            for i in set(range(len(b))) - set(b_idx):
                b_idx.append(i)
                a_idx.append(None)

    matches = np.array(list(zip(a_idx, b_idx)))
    return matches
