import unittest
import numpy as np
import pandas as pd

from ..xagg import *
from ..xchecks import *



class TestXAgg(unittest.TestCase):
    def test_Count(self):
        self.assertEqual(Count()._test(np.array([2, 4, 6])), 3)
        self.assertEqual(Count()._test(np.array([2, np.NaN, 6])), 2)
        self.assertEqual(Count()._test(np.array([np.NaN])), 0)

    def test_Min(self):
        self.assertEqual(2, Min('x')._test(np.array([2, 4, 6])))
        self.assertEqual(2, Min('x')._test(np.array([2, np.NaN, 6])))
        self.assertTrue(np.isnan(Min('x')._test(np.array([np.NaN]))))

    def test_Max(self):
        self.assertEqual(6, Max('x')._test(np.array([2, 4, 6])))
        self.assertEqual(6, Max('x')._test(np.array([2, np.NaN, 6])))
        self.assertTrue(np.isnan(Max('x')._test(np.array([np.NaN]))))

    def test_Mean(self):
        self.assertEqual(4, Mean('x')._test(np.array([2, 4, 6])))
        self.assertEqual(4, Mean('x')._test(np.array([2, np.NaN, 6])))
        self.assertTrue(np.isnan(Mean('x')._test(np.array([np.NaN]))))

    def test_Std(self):
        self.assertAlmostEqual(0.9428090415, Std('x')._test(np.array([2, 4, 4])))
        self.assertEqual(2, Std('x')._test(np.array([2, np.NaN, 6])))
        self.assertTrue(np.isnan(Std('x')._test(np.array([np.NaN]))))

    def test_Sum(self):
        self.assertEqual(12, Sum('x')._test(np.array([2, 4, 6])))
        self.assertEqual(8, Sum('x')._test(np.array([2, np.NaN, 6])))
        self.assertTrue(np.isnan(Sum('x')._test(np.array([np.NaN]))))

    def test_Any(self):
        self.assertEqual(2, Any('x')._test(np.array([2, 4, 6])))
        self.assertEqual(2, Any('x')._test(np.array([np.NaN, 2, 6])))
        self.assertTrue(np.isnan(Any('x')._test(np.array([np.NaN]))))

    def test_UniqueVals(self):
        self.assertListEqual([2, 4, 6], UniqueVals('x')._test(np.array([2, 4, 6])))
        self.assertListEqual([2, 6], UniqueVals('x')._test(np.array([np.NaN, 2, 6])))
        self.assertListEqual([], UniqueVals('x')._test(np.array([np.NaN])))

    def test_WMean(self):
        df = pd.DataFrame({'a': [2, 3, 5], 'w': [1, 2, 2]})
        self.assertEqual(3.6, WMean('a', weight_col='w').calc_func(df))

        df = pd.DataFrame({'a': [2, 3, np.NaN], 'w': [1, np.NaN, 2]})
        self.assertEqual(2, WMean('a', weight_col='w').calc_func(df))

        df = pd.DataFrame({'a': [np.NaN, 3, np.NaN], 'w': [1, np.NaN, 2]})
        self.assertTrue(np.isnan(WMean('a', weight_col='w').calc_func(df)))

        df = pd.DataFrame({'a': [np.NaN], 'w': [np.NaN]})
        self.assertTrue(np.isnan(WMean('a', weight_col='w').calc_func(df)))