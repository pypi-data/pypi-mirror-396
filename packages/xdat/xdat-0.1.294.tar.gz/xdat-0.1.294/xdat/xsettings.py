import os
import tempfile
import warnings
from collections import defaultdict

import matplotlib.colors as mcolors
import numpy as np
from scriptine import path
from slugify import slugify


PROJECT_NAME = 'xdat'
PROJECT_NAME_PRETTY = 'xDat'
IGNORE_INDEX = True                 # useful when dataframes don't have a meaningful index
SANITY_CHECKS = False               # False, "warn", "error"
NAN_TEXTS = ['', '-', '.', '--', 'X', 'x', '#DIV/0!', '#VALUE!', 'NA', 'NAN', '0R', 'NR', 'NULL', 'None']
ACCU_METHOD = 'fsum'                # method to perform accurate math

FIGSIZE = (10, 10)

# see: https://xkcd.com/color/rgb/
COL_DESC = dict()                   # column name --> column description
DEFAULT_COLORS = mcolors.TABLEAU_COLORS.keys()
HARD_CODED_COLORS = {
    0: 'xkcd:sea blue',
    1: 'xkcd:crimson',
    np.nan: 'xkcd:gray',
    None: 'xkcd:gray',
}

COLOR_LIST = list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.XKCD_COLORS)
COLOR_ID = defaultdict(int)
COLOR_LOOKUP = defaultdict(dict)

DEFAULT_MARKERS = 'o^sP*DXp<>v'
HARD_CODED_MARKERS = {
    0: 'o',
    1: 'X',
    np.nan: '^',
    None: '^',
}

PREFERRED_FONTS = ['DejaVu Sans', 'Liberation Sans', 'Nimbus Sans']

OUTPUT_PATH = None              # can leave None, typically in temporary folder
STATIC_OUTPUT_PATH = None       # should set to a specific folder

CACHE_PATH = None
STATIC_CACHE_PATH = None
DISABLE_CACHE = False
XDAT_ROOT = path(__file__).parent.abspath()


def x_add_desc(from_name, to_name):
    if from_name == to_name:
        return

    COL_DESC[from_name] = to_name


def x_get_desc(key):
    for _ in range(100):
        if key not in COL_DESC:
            return key

        assert COL_DESC[key] != key
        key = COL_DESC[key]

    raise ValueError(f"Looks like some sort of endless loop for '{key}'")


def x_add_color(key, color):
    HARD_CODED_COLORS[key] = color


def x_get_color(color_val, color_class=''):
    global COLOR_ID, COLOR_LIST, COLOR_LOOKUP
    if color_class not in COLOR_LOOKUP:
        COLOR_LOOKUP[color_class] = HARD_CODED_COLORS.copy()

    color_lookup = COLOR_LOOKUP[color_class]

    if color_val not in color_lookup:
        color_id = COLOR_ID[color_class]
        color_lookup[color_val] = COLOR_LIST[color_id % len(COLOR_LIST)]
        COLOR_ID[color_class] = color_id + 1

    color = color_lookup[color_val]
    assert isinstance(color, str) and len(color) > 0, color
    return color


def x_reset_colors(color_class=''):
    global COLOR_ID
    COLOR_ID[color_class] = 0


def updated_config(project_name=None, verbose=True):
    global OUTPUT_PATH, CACHE_PATH, PROJECT_NAME, PROJECT_NAME_PRETTY, STATIC_OUTPUT_PATH, STATIC_CACHE_PATH

    PROJECT_NAME_PRETTY = project_name or PROJECT_NAME_PRETTY
    assert PROJECT_NAME_PRETTY, "need to set PROJECT_NAME"

    PROJECT_NAME = slugify(PROJECT_NAME_PRETTY.lower(), separator='_')

    if not OUTPUT_PATH:
        base_path = os.environ.get('XDAT_OUTPUT_PATH')
        if base_path is None:
            base_path = tempfile.gettempdir()
            base_path = path(base_path).joinpath('xdat')

        OUTPUT_PATH = path(base_path).joinpath(PROJECT_NAME)

    else:
        OUTPUT_PATH = path(OUTPUT_PATH)

    CACHE_PATH = OUTPUT_PATH.joinpath('cache')
    OUTPUT_PATH.ensure_dir()

    xpptx_path = CACHE_PATH.joinpath('xpptx')
    if xpptx_path.exists():
        xpptx_path.rmtree(xpptx_path)

    if STATIC_OUTPUT_PATH:
        STATIC_OUTPUT_PATH = path(STATIC_OUTPUT_PATH)
        STATIC_CACHE_PATH = STATIC_OUTPUT_PATH.joinpath("cache")
        STATIC_CACHE_PATH.ensure_dir()

    if verbose:
        print(f"OUTPUT_PATH set to '{OUTPUT_PATH}'")

    return OUTPUT_PATH
x_update_config = updated_config


def get_default(default, override, possible_values=None):
    if override is None:
        if possible_values:
            assert default in possible_values, default

        return default

    if possible_values:
        assert override in possible_values, override

    return override


# updated_config(verbose=False)

warnings.filterwarnings('ignore', 'X does not have valid feature names, but StandardScaler was fitted with feature names')
warnings.filterwarnings('ignore', 'X has feature names, but LinearRegression was fitted without feature names')
warnings.filterwarnings("ignore", message="X has feature names, but DecisionTreeRegressor was fitted without feature names")

warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=RuntimeWarning)
