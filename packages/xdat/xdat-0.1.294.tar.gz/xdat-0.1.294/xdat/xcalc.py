import numpy as np


def x_calc_gini(a, presorted=False):
    assert sum(a<0) == 0, "can't have neg values"
    if not presorted:
        a = a[~np.isnan(a)]
        np.sort(a)

    total = 0
    for i, xi in enumerate(a[:-1], 1):
        total += np.sum(np.abs(xi - a[i:]))
    return total / (len(a)**2 * np.mean(a))

