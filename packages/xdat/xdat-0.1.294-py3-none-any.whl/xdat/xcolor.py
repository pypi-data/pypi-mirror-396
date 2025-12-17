import numpy as np
import colour
from munch import Munch
import matplotlib.colors as mcolors

# sRGB ↔ OKLab conversions
def srgb_to_oklab(rgb):
    return colour.convert(rgb, 'sRGB', 'OKLab')

def oklab_to_srgb(ok):
    rgb = colour.convert(ok, 'OKLab', 'sRGB')
    return np.clip(rgb, 0, 1)

# sRGB ↔ CIE Lab conversions
def srgb_to_lab(rgb):
    return colour.convert(rgb, 'sRGB', 'CIE Lab')

def lab_to_srgb(lab):
    rgb = colour.convert(lab, 'CIE Lab', 'sRGB')
    return np.clip(rgb, 0, 1)

# Linear ↔ gamma-corrected sRGB conversions
def srgb_to_linear(c):
    c = np.asarray(c)
    mask = c <= 0.04045
    return np.where(mask, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def linear_to_srgb(l):
    l = np.asarray(l)
    mask = l <= 0.0031308
    return np.where(mask, 12.92 * l, 1.055 * (l ** (1/2.4)) - 0.055)

# Constants
CORNERS_SRGB = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
CORNERS_OKLAB = np.array([srgb_to_oklab(c) for c in CORNERS_SRGB]).T

# Lightness blend parameters
L_MIN, L_MAX = 0.1, 0.9
GAMMA = 0.5
TINY_MAG_RATIO = 0.01 / 3.0


def triple_to_colour(triplet, space='oklab', l_min=L_MIN, l_max=L_MAX, stretch=False):
    """
    Convert a normalized RGB/OKLab triplet to a fill color, edge color, and magnitude.

    Args:
        triplet (array-like): 3 values in [0,1]
        space (str): 'oklab' or 'rgb'
        l_min (float): minimum lightness (0.0 - 1.0)
        l_max (float): maximum lightness (0.0 - 1.0)
        stretch (bool): apply gamma stretching to lightness if True

    Returns:
        Munch: {'color': hex, 'edge_color': hex, 'magnitude': float}
    """
    triplet = np.asarray(triplet, dtype=float)
    if triplet.min() < 0 or triplet.max() > 1:
        raise ValueError("Triplet values must be in [0,1].")

    m_raw = triplet.sum()
    magnitude = m_raw / 3.0

    # Black for zero input
    if m_raw == 0:
        return Munch({
            'color': mcolors.to_hex((0.0, 0.0, 0.0)),
            'edge_color': mcolors.to_hex((0.0, 0.0, 0.0)),
            'magnitude': 0.0,
        })

    weights = triplet / m_raw
    space = space.lower()

    # Compute lightness values before stretching
    L_fill = l_min + (l_max - l_min) * magnitude
    L_border = l_min + (l_max - l_min) * TINY_MAG_RATIO

    if stretch:
        L_fill = np.clip(L_fill ** GAMMA, 0, 1)
        L_border = np.clip(L_border ** GAMMA, 0, 1)

    if space == 'oklab':
        base = CORNERS_OKLAB @ weights
        fill_ok = np.array([L_fill, base[1], base[2]])
        border_ok = np.array([L_border, base[1], base[2]])
        fill_rgb = oklab_to_srgb(fill_ok)
        edge_rgb = oklab_to_srgb(border_ok)

    elif space in ('rgb', 'srgb'):
        triplet_lin = srgb_to_linear(triplet)
        fill_lin = triplet_lin * L_fill
        border_lin = triplet_lin * L_border
        fill_rgb = linear_to_srgb(fill_lin)
        edge_rgb = linear_to_srgb(border_lin)

    else:
        raise ValueError("space must be 'oklab' or 'rgb'.")

    return Munch({
        'color': mcolors.to_hex(fill_rgb),
        'edge_color': mcolors.to_hex(edge_rgb),
        'magnitude': magnitude,
    })
