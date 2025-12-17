import inspect
import warnings
import re
from collections import namedtuple
import makefun
import hashlib
import cloudpickle as pickle
import pandas as pd

try:
    from tensorflow.keras.models import load_model, Model
except ImportError:
    load_model = Model = None

import numpy as np
from . import xsettings
from scriptine import path


CachePlan = namedtuple("CachePlan", ['from_cache', 'cache_folder', 'cache_hash'])
_GET_CACHE_PLAN = False


def x_cached(name='', hash_name='', hash_key=None, also_parquet=False, outer_level=1, static=False, hash_args=True, ignore_params=None, is_keras=False, get_plan=None, cache_folder=None):

    def decorator(func):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        calling_name = calframe[outer_level][3]
        if calling_name == '<module>':
            calling_name = path(calframe[outer_level][1]).namebase

        f_src = inspect.getsource(func)
        short_name = name or func.__name__
        f_name = f"{calling_name}__{func.__name__}"
        if name:
            f_name = f"{f_name}__{name}"

        get_cache_plan = _GET_CACHE_PLAN if get_plan is None else get_plan

        def get_cache_folder():
            actually_static = static
            cache_folder2 = cache_folder

            if cache_folder is None:
                if static:
                    if not xsettings.STATIC_CACHE_PATH:
                        warnings.warn('xsettings.STATIC_CACHE_PATH is not set: setting static=False')
                        actually_static = False
                    else:
                        cache_folder2 = xsettings.STATIC_CACHE_PATH

                if not actually_static:
                    assert xsettings.CACHE_PATH is not None, "must set xsettings.CACHE_PATH"
                    cache_folder2 = xsettings.CACHE_PATH

                assert cache_folder2, "Problem with cache_folder"
            else:
                cache_folder2 = cache_folder

            cache_folder2 = path(cache_folder2)
            cache_folder2 = cache_folder2.joinpath(f_name)
            return cache_folder2

        if get_plan == 'cache_folder':
            cache_folder2 = get_cache_folder()
            return CachePlan(from_cache=None, cache_folder=cache_folder2, cache_hash=None)

        @makefun.wraps(func)
        def _cached(*args, **kwargs):
            if xsettings.DISABLE_CACHE:
                return func(*args, **kwargs)

            cache_folder = get_cache_folder()

            code_text = f_src + f_name + name + str(hash_key)
            if hash_args:
                for v in args:
                    if callable(v):
                        code_text += f"; {inspect.getsource(v)}"
                    else:
                        code_text += f"; {v}"

                for k,v in kwargs.items():
                    if ignore_params and k in ignore_params:
                        continue
                    if k == 'self':
                        continue

                    if callable(v):
                        try:
                            code_text += f"; {k}={inspect.getsource(v)}"
                        except TypeError:
                            code_text += f"; {k}={v})"
                    else:
                        code_text += f"; {k}={v}"

            if re.search(r" at 0x[0-9a-f]{12}>", code_text) is not None:
                assert False, "x_cached: found a reference to memory, should probably fix (or add to ignore_params)"

            code_hash = hashlib.md5(code_text.encode('utf-8')).hexdigest()

            hash_prefix = hash_name
            if hash_prefix:
                if hash_prefix.startswith('@'):
                    hash_prefix = hash_prefix[1:]
                    hash_prefix = kwargs.get(hash_prefix, '')

            if hash_prefix:
                code_hash = f"{hash_prefix}_{code_hash}"

            cache_subfolder = cache_folder.joinpath(code_hash)
            cache_subfolder.ensure_dir()

            def create_cache_plan(from_cache=None):
                res = CachePlan(from_cache=from_cache, cache_folder=cache_folder, cache_hash=code_hash)
                return res

            cache_file = None
            file_ext = None
            for cache_file in cache_subfolder.files("data.*"):
                file_ext = cache_file.ext[1:]
                break

            if cache_file is not None:
                if get_cache_plan:
                    return create_cache_plan(from_cache=True)
                else:
                    if is_keras or file_ext == 'keras':
                        results = load_model(cache_file)
                    elif file_ext == 'npy':
                        results = np.load(cache_file)
                    else:
                        with open(cache_file, 'rb') as f:
                            results = pickle.load(f)

            else:
                if get_cache_plan:
                    return create_cache_plan(from_cache=False)
                else:
                    results = func(*args, **kwargs)

                if Model is not None and isinstance(results, Model):
                    file_ext = 'keras'
                elif isinstance(results, np.ndarray):
                    file_ext = 'npy'
                else:
                    file_ext = 'pickle'

                cache_file = cache_subfolder.joinpath(f"data.{file_ext}")
                if is_keras or file_ext == 'keras':
                    results.save(cache_file)
                elif file_ext == 'npy':
                    np.save(cache_file, results)
                else:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(results, f)

                if also_parquet:
                    assert isinstance(results, pd.DataFrame), "need DataFrame to save as parquet"
                    parquet_path = cache_subfolder.joinpath(f"{short_name}.parquet")
                    results.to_parquet(parquet_path, use_deprecated_int96_timestamps=True)

            return results
        return _cached

    return decorator


def x_cached_call(func, *args, name='', hash_key=None, hash_args=True, also_parquet=False, static=False, cached=True, get_plan=None, cache_folder=None, **kwargs):
    if cached:
        dec = x_cached(name=name, hash_key=hash_key, hash_args=hash_args, also_parquet=also_parquet, outer_level=2, static=static, get_plan=get_plan, cache_folder=cache_folder)
        if get_plan:
            plan = dec(func)
            if get_plan == 'cache_folder':
                return plan
            plan = plan(*args, **kwargs)
            return plan

        return dec(func)(*args, **kwargs)

    return func(*args, **kwargs)


def x_cached_call_list(funcs):
    global _GET_CACHE_PLAN

    first_call_idx = len(funcs) - 1
    return


def x_memoize(func):
    cache = {}

    def memoized_func(*args, **kwargs):
        key = repr(args + tuple(sorted(kwargs.items())))
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return memoized_func
