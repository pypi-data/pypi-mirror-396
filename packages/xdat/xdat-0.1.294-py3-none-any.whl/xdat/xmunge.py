import pandas as pd
import numpy as np

from . import xpd

X_TARGET = 'target'     # a a target variable
X_META = 'meta'         # meta data (not to use as training feature)
X_KEY = 'key'           # a sample key (should be unique)
X_FEATURE = 'feature'   # a feature (can be used for training)

X_BINARY = 'binary'                # a binary feature
X_CATEGORICAL = 'categorical'      # a categorical feature
X_ORDINAL = 'ordinal'
X_INTERVAL = 'interval'
X_RATIO = 'ratio'


def safe_np_char(func, a, *args, **kwargs):
    def apply_func(i, *args, **kwargs):
        try:
            return func(i, *args, **kwargs)
        except:
            return np.nan

    return np.vectorize(apply_func)(a, *args, **kwargs)


class AutoColumnType:
    def __init__(self, sa):
        if isinstance(sa, pd.Series):
            self.do_sa = sa.name

        sa = np.array(sa)
        self.has_nulls = None

        self.do_lower = None
        self.do_strip = None
        self.do_rstrip = None
        self.do_replace = None
        self.do_astype = None

        self.col_type = self.find_real_col_dtype(sa=sa)

    @classmethod
    def type_and_transform(cls, sa):
        act = cls(sa)
        return act.col_type, act.transform(sa)

    def transform(self, sa):
        sa = np.array(sa)

        if self.do_lower:
            if self.has_nulls:
                sa = safe_np_char(np.char.lower, sa)
            else:
                sa = np.char.lower(sa)

        if self.do_strip:
            if self.has_nulls:
                sa = safe_np_char(np.char.strip, sa)
            else:
                sa = np.char.strip(sa)

        if self.do_rstrip:
            sa = np.char.rstrip(sa, self.do_rstrip)

        if self.do_replace:
            sa = xpd.x_replace(sa, replace_vals=self.do_replace)

        if self.do_astype:
            sa = sa.astype(self.do_astype)

        if self.do_sa:
            sa = pd.Series(sa, name=self.do_sa)

        return sa

    def find_real_col_dtype(self, sa=None, uvals=None):
        if uvals is None:
            try:
                uvals = pd.unique(sa)
            except TypeError:
                return type(sa[0])

        uvals_orig = uvals

        try:
            uvals = uvals[~pd.isna(uvals)]
        except:
            pass

        try:
            uvals = uvals[~np.isnan(uvals)]
        except:
            pass

        try:
            uvals = uvals[~np.isnat(uvals)]
        except:
            pass

        if len(uvals_orig) != len(uvals):
            self.has_nulls = True

        if len(uvals) == 0:
            return None

        try:
            if (uvals.astype(int) != uvals).sum() == 0:
                if len(uvals) <= 2:
                    if len(set(uvals) - {0, 1}) == 0:
                        return bool

                return int

        except ValueError:
            pass

        except AttributeError:
            pass            # strange situation

        type_first = type(uvals[0])
        if pd.api.types.is_string_dtype(uvals):
            uvals2 = np.unique(np.char.lower(uvals.astype(str)))
            uvals2 = np.unique(np.char.strip(uvals2))
            if len(uvals2) <= 2:
                if len(set(uvals2) - {'y', 'n'}) == 0:
                    self.do_lower = True
                    self.do_strip = True
                    self.do_replace = {'y': 1, 'n': 0}
                    return bool

            end_perc = np.char.endswith(uvals2, '%')
            if end_perc.sum() > 0:
                uvals2 = np.char.rstrip(uvals2, '%')
                try:
                    uvals2 = uvals2.astype(float)
                    dtype = self.find_real_col_dtype(uvals=uvals2)
                    if dtype in [int, float, bool]:
                        self.do_strip = True
                        self.do_rstrip = '%'
                        self.do_astype = float
                        return dtype

                except:
                    pass

            return str

        if pd.api.types.is_float_dtype(uvals):
            return float

        if pd.api.types.is_numeric_dtype(uvals):
            return int

        return type_first
