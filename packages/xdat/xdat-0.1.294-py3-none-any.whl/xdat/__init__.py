"""

"""
import pathlib

__version__ = (pathlib.Path(__file__).parent.resolve() / 'VERSION').read_text(encoding='utf-8').strip()
__author__ = 'Ido Carmi'
__credits__ = 'hermetric.com'


# import pandas_sets
from . import xagg, xcache, xchecks, xmunge, xnp, xpd, xplt, utilities


def monkey_patch():
    xpd.monkey_patch()
    xnp.monkey_patch()

