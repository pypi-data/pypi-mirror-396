from collections import Counter, defaultdict
import fnmatch
import logging
import operator
import random

from caseconverter import snakecase
import pandas
import numpy as np
import pandas as pd
from slugify import slugify
from tqdm import tqdm
import natsort

from . import xsettings
from . import xagg
from . import xparallel


def x_array_col_to_2d(sa):
    return np.concatenate([np.array(a).reshape(1, -1) for a in sa], axis=0)


def x_gen_grouped_counter(df, group_on=None, sort_on=None, start=0):
    """
    Another way to generate top-k values per group
    """

    if sort_on:
        df = df.sort_values(sort_on)

    return df.groupby(group_on).cumcount() + start


def x_filter_by_keys(df, key_values):
    df2 = df.copy()
    for k, v in key_values.items():
        if k in df2.columns:
            df2 = df2[df2[k] == v].copy()

    return df2


def x_natsort_values(df, on, ascending=True):
    if isinstance(on, str):
        on = [on]

    df2 = df[on].astype(str)
    sa = df2.apply(lambda row: ' - '.join(row), axis=1)
    new_indexes = natsort.index_natsorted(sa, reverse=not ascending)
    df = df.iloc[new_indexes]
    df = df.reset_index(drop=True)
    return df


def x_iter_groups(df, on, dropna=True, df_only=False, with_tqdm=False, yield_total=False, sort_on=None):
    if not on:
        yield df, dict(), ""
        return

    # make sure is a list (so next check won't fail)
    if isinstance(on, str):
        on = [on]

    elif isinstance(on, tuple):
        on = list(on)

    use_natsort = False
    if pd.api.types.is_string_dtype(df[on[0]]):
        use_natsort = True

    # if it's a list of length 1, pandas want it to be a string... (FutureWarning...)
    if len(on) == 1:
        on = on[0]

    if use_natsort:
        df = x_natsort_values(df, on)
    else:
        df = df.sort_values(on)

    groups = df.groupby(on, dropna=dropna, sort=False)
    total = len(groups) if with_tqdm or yield_total else None
    if with_tqdm and isinstance(with_tqdm, str):
        desc = with_tqdm
    else:
        desc = None

    if yield_total:
        yield total

    for group_keys, df_group in tqdm(groups, total=total, disable=not with_tqdm, desc=desc):
        if not isinstance(group_keys, list) and not isinstance(group_keys, tuple):
            group_keys = [group_keys]

        if isinstance(on, str):
            on = [on]

        group_title = ", ".join([f"{k}={v}" for k,v in zip(on, group_keys)])
        series_group_keys = pd.Series(data=group_keys, index=on)

        if len(df_group):
            if sort_on:
                df_group = df_group.sort_values(sort_on).reset_index(drop=True)

            if df_only:
                yield df_group

            else:
                yield df_group, series_group_keys, group_title


def x_sample_groups(df, group_col, stratify_col=None, n_rows=None, n_groups=None, random_state=None):
    """
    Randomly samples groups
    :param n_rows: number of rows
    :param n_groups: numer of groups
    """

    assert int(bool(n_rows)) + int(bool(n_groups)) == 1, "one of n_rows or n_groups must be set"

    if random_state:
        df = df.sample(frac=1., random_state=random_state)

    stratify_groups = defaultdict(list)
    if stratify_col:
        for dfs, keys, _ in x_iter_groups(df, stratify_col):
            for dfg in x_iter_groups(dfs, group_col, df_only=True):
                stratify_groups[tuple(keys)].append(dfg)
    else:
        for dfg in x_iter_groups(df, group_col, df_only=True):
            stratify_groups[(1,)].append(dfg)

    all_res = []
    count = 0
    done = False
    while True:
        keys = list(stratify_groups.keys())
        random.shuffle(keys)
        got_hit = False
        for key in keys:
            glist = stratify_groups[key]
            if not len(glist):
                continue

            got_hit = True
            index = random.randrange(len(glist))
            dfg = glist.pop(index)

            all_res.append(dfg)

            if n_rows:
                count += len(dfg)
                if count >= n_rows:
                    done = True
                    break

            elif n_groups:
                count += 1
                if count >= n_groups:
                    done = True
                    break

        if done or not got_hit:
            break

    df_all = pd.concat(all_res, ignore_index=True)
    if n_rows:
        df_all = df_all[:n_rows].reset_index(drop=True)

    return df_all


def x_isin_multi(df, df_other, cols):
    """
    Returns a filter for df so that it only contains values in df_other
    Credit: https://stackoverflow.com/questions/45198786/how-to-use-pandas-isin-for-multiple-columns
    """
    if isinstance(cols, str):
        cols = [cols]

    df_other = df_other[cols].drop_duplicates()
    index1 = pd.MultiIndex.from_arrays([df[col] for col in cols])
    index2 = pd.MultiIndex.from_arrays([df_other[col] for col in cols])
    res = index1.isin(index2)
    return res


def x_merge(df_self, right, x_drop_dup_cols=True, drop_diff_cols=False, log=None, **kwargs):
    """
    A wrapper around pd.merge().
    Gets rid of as many duplicate columns ('_x', '_y') as possible after the merge.
    """
    #
    # a few pre-merge checks:
    #
    if hasattr(pandas.DataFrame, "_orig__merge"):
        orig_merge = pandas.DataFrame._orig__merge
    else:
        orig_merge = pandas.DataFrame.merge

    if len(df_self) == 0:
        logging.warning("left side is an empty dataframe")

    if len(right) == 0:
        logging.warning("right side is an empty dataframe")

    how = kwargs.get('how', 'inner')
    on = kwargs['on']
    if isinstance(on, str):
        on = [on]

    # check left side for uniqueness
    unique_checks = []
    if how in ['inner', 'left']:
        unique_checks.append(('right', right, df_self))
    if how in ['inner', 'right']:
        unique_checks.append(('left', df_self, right))

    num_err = 0
    for (which, df, df_other) in unique_checks:
        df = df[x_isin_multi(df, df_other, on)]  # no need to check values that are not on the other side, could be a placeholder / null / something like that
        if len(df[on].drop_duplicates()) != len(df):
            num_err += 1
            if how == 'inner' and num_err == 1:  # we need both sides to be a problem for this to be a problem
                continue

            counts = df.value_counts(on)
            counts = counts[counts > 1]
            logging.warning(f"{which} is not unique on {on}\n{counts[:10].to_string()}")
            raise ValueError(f"{which} is not unique on {on}")
    #
    # the actual merge:
    #
    df = orig_merge(df_self, right, **kwargs)
    if len(df) == 0:
        logging.warning("merge outcome is an empty dataframe")

    if log:
        kleft = df_self[on].drop_duplicates()
        kright = right[on].drop_duplicates()
        kleft['xleft'] = 1
        kright['xright'] = 1

        both = orig_merge(kleft, kright, on=on, how='outer')
        both[['xleft', 'xright']] = both[['xleft', 'xright']].fillna(0)
        both = both.sort_values(on)
        left_only = both[(both.xleft == 1) & (both.xright == 0)]
        if len(left_only):
            left_only.to_csv(xsettings.OUTPUT_PATH.joinpath(f"{log}-left_only.csv"), index=False)
        right_only = both[(both.xleft == 0) & (both.xright == 1)]
        if len(right_only):
            right_only.to_csv(xsettings.OUTPUT_PATH.joinpath(f"{log}-right_only.csv"), index=False)

    if not x_drop_dup_cols:
        return df

    suffixes = kwargs.get('suffixes', ('_x', '_y'))
    s1, s2 = suffixes
    for col1 in sorted(df.columns):
        if col1.endswith(s1):
            col_new = col1[:-1*len(s1)]
            col2 = col_new + s2

            if col_new in df.columns:
                continue

            if col2 not in df.columns:
                continue

            c1 = df[col1]
            c2 = df[col2]

            # remove if columns are exact duplicates
            if (c1 != c2).sum() == 0:
                df.rename(columns={col1: col_new}, inplace=True)
                del df[col2]
                continue

            # see if the differences are when one column is NA and the other is not
            # (can happen on a left-join, for example)
            c1b = np.where(c1.isna(), c2, c1)
            c2b = np.where(c2.isna(), c1, c2)

            if (c1b != c2b).sum() == 0:
                del df[col1]
                del df[col2]
                df[col_new] = c1b
                continue

            if drop_diff_cols:
                del df[col1]
                del df[col2]
                continue

    return df


def x_drop_cols(df, match, unmatch=None, fake=False):
    cols = df.columns
    matches = x_match(cols, match)
    if unmatch:
        unmatch = x_match(cols, unmatch)
        matches = matches & ~unmatch

    if fake:
        print(f'matched:', cols[matches])
        return

    matched_cols = cols[matches]
    if len(matched_cols) > 0:
        df.drop(columns=matched_cols, inplace=True)


def x_match(self, values, exclude=False, do_fnmatch=True):
    """
    Filter DataFrame by column values

    Examples:
    >> df['animal'].x_match(['cat', 'dog', '*ouse'], exclude=True)
    """

    possible_values = self.unique()

    if isinstance(values, str):
        values = [values]

    keep_exact = []
    for keep_pattern in values:
        if do_fnmatch and isinstance(keep_pattern, str):
            vals = [v for v in possible_values if fnmatch.fnmatch(v, keep_pattern)]
            keep_exact.extend(vals)

        else:
            keep_exact.append(keep_pattern)

    idxs = self.isin(keep_exact)
    if exclude:
        idxs = ~idxs

    return idxs


def x_filter_by(self, values, col_name, exclude=False, dropna=True, ignore_index=None, sanity_checks=None, do_fnmatch=True):
    """
    Filter DataFrame by column values

    Examples:
    >> df.x_filter_by(['cat', 'dog', '*ouse'], 'animal', exclude=True)
    """

    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)
    sanity_checks = xsettings.get_default(xsettings.SANITY_CHECKS, sanity_checks)

    if dropna:
        self = self.dropna(subset=[col_name])

    idxs = x_match(self[col_name], values, exclude=exclude, do_fnmatch=do_fnmatch)

    df_filtered = self[idxs]

    if ignore_index:
        df_filtered = df_filtered.reset_index(drop=True)

    if sanity_checks:
        assert len(df_filtered) > 0, f"attr_name={col_name}, keep_values={values}, exclude={exclude}"

    return df_filtered


def x_split_on(self, values, col_name, ignore_index=None, drop_key_col=False):
    """
    Filters & splits dataframe by values

    >> df_cats, df_dogs = df.x_split_on(['cat', 'dog'], 'animal')
    """
    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)

    res = []
    for value in values:
        df_value = x_filter_by(self, [value], col_name, ignore_index=ignore_index)
        if drop_key_col:
            del df_value[col_name]

        res.append(df_value)

    return tuple(res)


def x_append(self, other, ignore_index=None, verify_integrity=False, sort=False):
    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)

    if self is None:
        return other

    if other is None:
        return self

    return self.append(other, ignore_index=ignore_index, verify_integrity=verify_integrity, sort=sort)


def x_replace(self, valid_vals='all', replace_vals=None, default=None):
    replace_vals = replace_vals or dict()
    if valid_vals != 'all':
        if valid_vals is None:
            valid_vals = tuple()

        valid_vals = tuple(set(valid_vals) | set(replace_vals.keys()) | set(replace_vals.values()))

    def do(x):
        if isinstance(valid_vals, tuple):
            if pd.isna(x):
                return default

            try:
                if np.isnan(x):
                    return default
            except TypeError:
                pass

            if x not in valid_vals:
                return default

        return replace_vals.get(x, x)

    sa_replaced = self.apply(do)
    return sa_replaced


def x_label_bins(sa, breaks, labels, kind='lt'):
    """
    Generates category names out of numbers
    """

    op = {'lt': operator.lt, 'lte': operator.le, 'gt': operator.gt, 'gte': operator.ge}[kind]
    def get_label(x):
        for b, l in zip(breaks, labels):
            if op(x, b):
                return l
        return labels[-1]

    return sa.apply(get_label)

def x_clean_text(self):
    return self.apply(lambda x: slugify(x, separator="_"))


def x_as_float(self, nan_texts=None, on_error='ignore'):
    nan_texts = xsettings.get_default(xsettings.NAN_TEXTS, nan_texts)

    def conv(x):
        try:
            return float(x)
        except ValueError:
            if x.strip() in nan_texts:
                return np.nan
            if on_error == 'ignore':
                return np.nan
            raise ValueError(x)

    return self.apply(conv)


def x_long_to_wide(df, key_cols, widen_on, value_cols, include_other_cols=True, sep='_'):
    df_res = pd.pivot(df, index=key_cols, columns=widen_on, values=value_cols)
    new_cols = [sep.join([str(a) for a in i]) for i in df_res.columns.to_flat_index()]
    df_res.columns = new_cols
    df_res.reset_index(inplace=True)

    if include_other_cols:
        df2 = df.drop_duplicates(key_cols)
        df_res = df_res.merge(df2, on=key_cols, how='left')
        col_diff = set(df_res.columns) - set(df.columns)
        cols = df.columns.to_list() + [c for c in df_res.columns if c in col_diff]
        df_res = df_res[cols].copy()

    return df_res


def x_apply_on_group(df, by, func, include_other_cols=True):
    """
    apply a function to groups in dataframe
    :param df: input df
    :param by: columns to group on
    :param func: accepts df, can return dict (multiple columns)
    :param include_other_cols: if True, will include other cols in df, not just those specified in 'by'
           (TODO: add check (is_unique) to make sure only add columns with unique values per group)
    :return: a dataframe, where each row has unique 'by' + extra cols

    >>> x_apply_on_group(df, ['animal', 'style'], lambda dfx: return {'max_height': dfx.height.max()})
    """

    def wrapper(dfx):
        res = func(dfx)
        if isinstance(res, dict):
            res = pd.Series(res)

        return res

    g = df.groupby(by)
    df_res = g.apply(wrapper)
    df_res = df_res.reset_index()

    if include_other_cols:
        df2 = df.drop_duplicates(by)
        df_res = df_res.merge(df2, on=by, how='left')
        cols = df.columns.to_list() + sorted(set(df_res.columns) - set(df.columns))
        df_res = df_res[cols].copy()

    return df_res


def x_groupby(self, by, aggs, ignore_index=None, check_lost_keys=True, **kwargs):
    """
    A simpler groupby interface
    (inspired by Turicreate)

    >> df.x_groupby('a', {'min_b': xagg.Min('b'), 'max_c': xagg.Max('c'), 'n': xagg.Count()})
    """

    ignore_index = xsettings.get_default(xsettings.IGNORE_INDEX, ignore_index)
    if isinstance(by, str):
        by = [by]

    all_dfs = []

    #
    # do single-col _Agg
    #

    d = dict()
    for k, v in aggs.items():
        if isinstance(v, xagg._Agg):
            tup = v.as_tuple()
            if tup[0] is None:
                tup = tuple([self.columns[0], tup[1]])

            d[k] = tup

        elif isinstance(v, xagg._AggMultiCol):
            continue

        elif isinstance(v, tuple):
            d[k] = v

        else:
            raise ValueError(f"{k}: {v}")

    if d:
        g = self.groupby(by=by, **kwargs)
        dfg = g.agg(**d)
        all_dfs.append(dfg)

    #
    # now do multi-col _AggMultiCol
    #

    multi_cols = [(k, v) for k, v in aggs.items() if isinstance(v, xagg._AggMultiCol)]
    if multi_cols:
        def calc(i):
            k, v = i
            if v.col_names:
                df2 = self[by + v.col_names]
            else:
                df2 = self
            g = df2.groupby(by=by, **kwargs)
            dfg = g.apply(lambda dfx: v.calc_func(dfx, **v.kwargs))
            dfg = dfg.rename(k)
            return dfg

        all_dfs_multi = xparallel.x_on_iter(multi_cols, calc)
        all_dfs.extend(all_dfs_multi)

    assert len(all_dfs) > 0, "Nothing happened?"

    #
    # Combine results
    #
    def check_lost_cols(df):
        if not check_lost_keys:
            return

        for col in by:
            if len(self[col].unique()) != len(df[col].unique()):
                assert False, f"{col}: {len(self[col].unique())} != {len(df[col].unique())} (might have had a few NAs in {col})"

    if len(all_dfs) == 1:
        dfg = all_dfs[0]
        if ignore_index:
            dfg = dfg.reset_index()

        check_lost_cols(dfg)
        return dfg

    else:
        dfg = pd.concat(all_dfs, axis=1)
        if ignore_index:
            dfg = dfg.reset_index()

        check_lost_cols(dfg)
        return dfg


def x_add_missing_rows(df, key, subkey):
    """
    Given key & subkey, for each key, add rows with missing subkey
    > x_add_missing_rows(df, 'person', ['day', 'hour'])
      (if a person had a missing <day,hour>, then a row will be added)
    """

    if isinstance(key, str):
        key = [key]

    if isinstance(subkey, str):
        subkey = [subkey]

    df_values = df[subkey].drop_duplicates().reset_index(drop=True)

    all_dfs = []
    for dfg, vals, _ in x_iter_groups(df, key):
        index1 = pd.MultiIndex.from_arrays([dfg[col] for col in subkey])
        index2 = pd.MultiIndex.from_arrays([df_values[col] for col in subkey])
        missing = ~index2.isin(index1)
        if missing.sum() > 0:
            df_missing = df_values[missing].copy()
            for k in key:
                df_missing[k] = vals[k]
            dfg = pd.concat([dfg, df_missing], ignore_index=True)

        all_dfs.append(dfg)

    df_all = pd.concat(all_dfs, ignore_index=True)
    return df_all


def x_calc_rank_num_series(sa, ascending=True):
    """
    calculates the rank, but with a few features:
    - handles nulls properly (they don't get a rank)
    - same values get the same rank
    - resulting ranks are consecutive (1, 2, ...)
    - Got some help with ChatGPT on this... :)
    """
    # Use pandas groupby and ngroup to handle ties and get consecutive ranks
    ranks = sa.groupby(sa, sort=True).ngroup() + 1

    if not ascending:
        ranks = ranks.max() - ranks + 1

    ranks[sa.isnull()] = np.nan
    return ranks


def x_calc_rank_num(self, key_col_name, score_col_name, ascending=True):
    """
    creates a series ranking each group of key_col_name by score_col_name

    >> df.x_calc_rank_num('user_id', 'product_score', ascending=False)
    """
    self = self.reset_index(drop=True)
    if isinstance(key_col_name, str):
        key_col_name = [key_col_name]

    sa_ranks = self.groupby(key_col_name)[score_col_name].apply(lambda sa: x_calc_rank_num_series(sa, ascending=ascending))
    try:
        sa_ranks = sa_ranks.astype(int)
    except pandas.errors.IntCastingNaNError:
        pass

    df_idx = self.reset_index()[['index']]
    assert len(df_idx) == len(df_idx.drop_duplicates(subset=['index']))
    df_ranks = sa_ranks.reset_index()

    level_num = len(key_col_name)
    col_name = f'level_{level_num}'
    df_ranks = df_ranks.sort_values(col_name)
    ranks = df_ranks[score_col_name].values
    return ranks


def x_add_history(self, key, value):
    if not hasattr(self, '_x_history'):
        self._metadata.append('_x_history')
        self._x_history = []

    self._x_history.append((key, value))


def x_get_history(self):
    if not hasattr(self, '_x_history'):
        return []

    return self._x_history


def x_set_data_type(self, data_type):
    """
    sets logical data type: binary, nominal, ordinal, interval, ratio, temporal, geojson
    (inspired by altair, etc.)
    what about cyclical? (can be either ordinal [day of week] or interval [hour of day]
    """

    if not hasattr(self, '_x_data_type'):
        self._metadata.append('_x_data_type')

    data_type = data_type.lower()[0]
    data_type = {
        'b': 'binary',
        'n': 'nominal',
        'o': 'ordinal',
        'i': 'interval',
        'r': 'ratio',
        'q': 'ratio',
        't': 'temporal',
        'g': 'geojson'
    }[data_type]

    self._x_data_type = data_type


def x_get_data_type(self):
    if not hasattr(self, '_x_data_type'):
        return None

    return self._x_data_type


def x_set_column_type(self, column_type):
    """
    sets logical column type: target, feature, meta, key
    - a target variable
    - a feature (can be used for training)
    - meta data (not to use as a training feature, but might be confounding)
    - a sample key (should be unique)
    """

    if not hasattr(self, '_x_column_type'):
        self._metadata.append('_x_column_type')

    column_type = column_type.lower()[0]
    column_type = {
        't': 'target',
        'f': 'feature',
        'm': 'meta',
        'k': 'key'
    }[column_type]

    self._x_column_type = column_type


def x_get_column_type(self):
    if not hasattr(self, '_x_column_type'):
        return None

    return self._x_column_type


def x_rename(self, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='raise'):
    if columns is not None:
        for name_from, name_to in columns.items():
            xsettings.x_add_desc(name_to, name_from)

    self_orig = self
    self = self.rename(mapper=mapper, index=index, columns=columns, axis=axis, copy=copy, inplace=inplace, level=level, errors=errors)

    self = self if self is not None else self_orig
    return self


def x_sort_on_lookup(self: pd.DataFrame, on, sa_lookup: pd.Series, ascending=True):
    """
    Given lookup Series, merge it based 'on', and then sort, and remove
    df.x_sort_on_lookup('height', df.groupby('height')['width'].mean())
    """
    df = self.copy()
    df['tmp_x_sort_on_lookup'] = df.apply(lambda r: sa_lookup[r[on]], axis=1)
    df = df.sort_values('tmp_x_sort_on_lookup', ascending=ascending)
    del df['tmp_x_sort_on_lookup']
    return df


def x_clean_column_names(self, inplace=False, remove_parens="auto"):
    """
    renames columns to pythonable names, " Hi there" --> "hi_there"
    """

    orig_columns = self.columns[:]
    orig_columns = ["/".join(c) if isinstance(c, tuple) else c for c in orig_columns]
    new_columns = orig_columns[:]

    if remove_parens:
        new_columns = [c.split('(')[0] for c in new_columns]
        new_columns = [c.split('[')[0] for c in new_columns]

    new_columns = [c.replace("/", " ") for c in new_columns]
    new_columns = np.array([snakecase(c) for c in new_columns])

    a = pd.Series(new_columns)
    counts = a.value_counts()
    counts = counts[counts > 1]
    bad_keys = counts.index.values

    new_columns = np.where(~np.isin(new_columns, bad_keys), new_columns, np.array([slugify(c, separator='_') for c in orig_columns]))

    a = pd.Series(new_columns)
    counts = a.value_counts()

    used_counts = Counter()

    def get_new_name(col):
        if counts[col] == 1:
            return col

        used_counts[col] += 1
        c = used_counts[col]
        return f"{col}_{c}"

    new2 = [get_new_name(c) for c in new_columns]
    assert len(set(new2)) == len(orig_columns), "not all column names become unique"

    if inplace is False:
        self = self.copy()

    self.columns = new2
    return self


def x_drop_by_counts(self, count_on, keep_count=None, min_count=None, max_count=None):
    """
    count number of unique values for `count_on`, and filter df by `keep_count`
    """

    def do_filter(dfx):
        if keep_count:
            return len(dfx) == keep_count
        if min_count:
            return len(dfx) >= min_count
        if max_count:
            return len(dfx) <= max_count

    df2 = self.groupby(count_on).filter(do_filter).reset_index(drop=True)
    return df2


def x_group_counts(self, group_on, count_on, include_zeros=True, how='rows'):
    assert how in ['rows', 'unique'], how
    if isinstance(group_on, str):
        group_on = [group_on]

    assert isinstance(count_on, str), "only one column is supported"

    if how == 'unique':
        self = self.drop_duplicates(group_on+[count_on])

    df_res = self.groupby(group_on + [count_on]).size().reset_index(name='count')

    if include_zeros:
        all_groups = [self[col].unique() for col in group_on]
        all_values = self[count_on].unique()
        full_index = pd.MultiIndex.from_product(all_groups + [all_values], names=group_on + [count_on])
        df_res = df_res.set_index(group_on + [count_on]).reindex(full_index, fill_value=0).reset_index()

    return df_res

def x_timedelta_as_hours(self):
    """
    Given a Series containing Timedelta, converts it to Series containing hours (float)
    """
    return self.apply(lambda d: d.days * 24 + d.seconds / (60 * 60))


def x_datetime_as_hours(self):
    """
    Given a Series containing datetimes, converts it to Series containing hours (float)
    """
    return self.apply(lambda d: d.hour + d.minute / 60 + d.second / (60*60))


def x_add_uid(self, on, new_col, start_with=1, sort=True):
    """
    Given a df, convert values to unique IDs
    """
    if isinstance(on, str):
        on = [on]

    df = self.copy()
    new_col_temp = None
    if new_col in df.columns:
        new_col_temp = f"{new_col}__tmp"
        df.rename(columns={new_col: new_col_temp}, inplace=True)

        if new_col in on:
            on.remove(new_col)
            on.append(new_col_temp)

    df2 = df[on]
    df2 = df2.drop_duplicates()
    if sort:
        df2 = df2.sort_values(on)

    df2 = df2.reset_index(drop=True)
    df2 = df2.reset_index()
    df2.rename(columns={'index': new_col}, inplace=True)
    df2[new_col] = df2[new_col] + start_with
    df_new = df.merge(df2, on=on)

    if new_col_temp:
        del df_new[new_col_temp]

    return df_new


def x_drop_null_columns(df):
    df = df.copy()
    for col in df.columns:
        if df[col].isna().sum() == len(df):
            del df[col]

    return df

def x_drop_mostly_null(df, max_na_cols=0.1):
    counts = df.isna().sum()
    bad = counts[counts/len(df) > max_na_cols]
    if len(bad) > 0:
        df = df.drop(columns=bad.index.values)
    df = df.dropna()
    return df


def x_drop_null_rows(df):
    counts = (~df.isna()).sum(axis=1)
    bad_indexes = counts[counts == 0].index.values
    df = df.drop(bad_indexes).reset_index(drop=True)
    return df


def x_undo_dummies(df, prefix_sep="_"):
    """
    Given df with dummy columns (created using pd.get_dummies()), undo the dummies
    Credits: https://newbedev.com/reverse-a-get-dummies-encoding-in-pandas
    """
    cols2collapse = {
        item.split(prefix_sep)[0]: (prefix_sep in item) for item in df.columns
    }
    series_list = []
    for col, needs_to_collapse in cols2collapse.items():
        if needs_to_collapse:
            undummified = (
                df.filter(like=col)
                .idxmax(axis=1)
                .apply(lambda x: x.split(prefix_sep, maxsplit=1)[1])
                .rename(col)
            )
            series_list.append(undummified)
        else:
            series_list.append(df[col])
    undummified_df = pd.concat(series_list, axis=1)
    return undummified_df


def x_is_numeric_value(sa):
    return sa.apply(lambda x: pd.api.types.is_numeric_dtype(type(x)))


def x_drop_duplicates(df, subset=None, *, keep='first', inplace=False, ignore_index=False, n=1):
    if n == 1:
        return pd.DataFrame.drop_duplicates(df, subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    else:
        if keep == 'last':
            return df.groupby(subset, group_keys=False).tail(n)
        return df.groupby(subset, group_keys=False).head(n)


def monkey_patch(aggressive=False):
    pandas.Series.x_match = x_match
    pandas.Series.x_replace = x_replace
    pandas.Series.x_clean_text = x_clean_text
    pandas.Series.x_add_history = x_add_history
    pandas.Series.x_get_history = x_get_history
    pandas.Series.x_set_data_type = x_set_data_type
    pandas.Series.x_get_data_type = x_get_data_type
    pandas.Series.x_set_column_type = x_set_column_type
    pandas.Series.x_get_column_type = x_get_column_type
    pandas.Series.x_as_hours = x_timedelta_as_hours

    pandas.DataFrame.x_filter_by = x_filter_by
    pandas.DataFrame.x_split_on = x_split_on
    pandas.DataFrame.x_append = x_append
    pandas.DataFrame.x_groupby = x_groupby
    pandas.DataFrame.x_calc_rank_num = x_calc_rank_num
    pandas.DataFrame.x_add_history = x_add_history
    pandas.DataFrame.x_get_history = x_get_history
    pandas.DataFrame.x_clean_column_names = x_clean_column_names
    pandas.DataFrame.x_rename = x_rename
    pandas.DataFrame.x_sort_on_lookup = x_sort_on_lookup
    pandas.DataFrame.x_undo_dummies = x_undo_dummies
    pandas.DataFrame.x_merge = x_merge
    pandas.DataFrame._orig__merge = pandas.DataFrame.merge
    pandas.DataFrame.x_drop_duplicates = x_drop_duplicates

    if aggressive:
        pandas.DataFrame.merge = x_merge



