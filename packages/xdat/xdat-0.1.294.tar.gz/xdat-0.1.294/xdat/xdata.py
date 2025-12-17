import tempfile
import pandas as pd
import numpy as np
from slugify import slugify
from munch import Munch as Dict
from scriptine import path
import connectorx as cx
from . import xsettings, xpd, xcache
from munch import Munch as MunchDict


def x_fix_dtypes(df: pd.DataFrame):
    """
    Given df, fix the datatypes.
    Bad data types can happen when NaN existed in data, etc.
    """

    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    tpath = path(f.name)
    f.close()

    df.to_csv(tpath, index=False)
    df2 = pd.read_csv(tpath)
    tpath.remove()

    return df2


def drop_na_cols_df(df):
    if len(df) == 0:
        return df

    df = df.copy()
    for col_name in df.columns:
        sa = df[col_name]

        if not pd.api.types.is_numeric_dtype(sa):
            continue

        if np.isnan(sa).sum() == len(sa):
            del df[col_name]

    return df


def drop_unnamed_cols_df(df):
    for col in df.columns:
        if col.startswith('unnamed_'):
            del df[col]
    return df


def read_csv(csv_path, na_values=None, low_memory=False, drop_unnamed_cols=False, drop_na_cols=True, drop_na_rows=True, skiprows=None, skipfooter=0, dtype=None, rtl_cols=tuple(), **kwargs):
    """
    A simple wrapper for read_csv that cleans it up a bit in the process..
    """
    na_values = xsettings.get_default(xsettings.NAN_TEXTS, na_values)

    engine = 'python' if skipfooter else 'c'

    df = pd.read_csv(csv_path, keep_default_na=False, na_values=na_values, low_memory=low_memory, skiprows=skiprows, skipfooter=skipfooter, engine=engine, dtype=dtype, **kwargs)
    xpd.x_clean_column_names(df, inplace=True)

    if drop_na_cols:
        df = drop_na_cols_df(df)

    if drop_unnamed_cols:
        df = drop_unnamed_cols_df(df)

    if drop_na_rows:
        df = xpd.x_drop_null_rows(df)

    for col_name in rtl_cols:
        if col_name in df.columns:
            df[f"{col_name}_rtl"] = df[col_name].apply(lambda s: s[::-1])

    return df


def read_excel(excel_path, na_values=None, drop_na_cols=True, rtl_cols=tuple(),return_df_if_one=True, drop_unnamed_cols=False, engine=None, sheet_name=None, **kwargs):
    """
    A simple wrapper for read_excel that cleans it up a bit in the process,
      as well as returns a different dataframe for each sheet
    """
    na_values = xsettings.get_default(xsettings.NAN_TEXTS, na_values)

    try:
        res = pd.read_excel(excel_path, sheet_name=sheet_name, na_values=na_values, engine=engine, **kwargs)
    except:
        print("ERROR: can't open:", excel_path)
        raise

    if sheet_name:
        res = {sheet_name: res}

    res_new = Dict()
    for k in list(res.keys()):
        k_new = slugify(k, separator='_')
        df = res[k]
        xpd.x_clean_column_names(df, inplace=True)
        if drop_na_cols:
            df = drop_na_cols_df(df)

        if drop_unnamed_cols:
            df = drop_unnamed_cols_df(df)

        for col_name in rtl_cols:
            if col_name in df.columns:
                df[f"{col_name}_rtl"] = df[col_name].apply(lambda s: s[::-1])

        assert k_new not in res_new, k_new
        res_new[k_new] = df

    if return_df_if_one:
        if len(res_new) == 1:
            return res_new[list(res_new.keys())[0]]

    return res_new


def write_excel(excel_path, sheets):
    """
    writes an excel file with multiple sheets
    :param sheets: list of ('sheet name', df)
    """
    def excel_writer(f):
        with pd.ExcelWriter(f) as writer:
            for sheet_name, df in sheets:
                df.to_excel(writer, sheet_name=sheet_name, header=True, index=False)

    with open(excel_path, 'wb') as f:
        excel_writer(f)

@xcache.x_cached(static=True)
def read_db_table(conn_str, table_name, cols=None):
    cols_str = '*' if not cols else ",".join(cols)
    df = cx.read_sql(conn_str, f"select {cols_str} from {table_name}")
    df = xpd.x_clean_column_names(df)
    return df


@xcache.x_cached()
def read_db(conn_str, tables, prefix='df_'):
    if isinstance(tables, str):
        tables = [tables]

    data = MunchDict()
    for table in tables:
        table_slug = table
        if isinstance(table, tuple):
            table, table_slug = table

        table_slug = slugify(table_slug, separator="_")
        df = read_db_table(conn_str, table)
        data[f"{prefix}{table_slug}"] = df

    return data


def filter_all_on(*args, on=None):
    """
    Given two or more dataframes, returns them filtered as if they went through an inner-join
    """

    assert on, "must provide 'on' parameter"
    if len(args) < 2:
        return args

    set_all = args[0][on].unique()
    for df in args[1:]:
        set_curr = df[on].unique()
        set_all = np.intersect1d(set_all, set_curr)

    filtered = []
    for df in args:
        df = df[df[on].isin(set_all)]
        filtered.append(df)

    return tuple(filtered)

