import unittest
import pandas as pd
import numpy as np
import tulipy as ti

from backtesting.lib import *

OHLCV = pd.DataFrame([
    ['2005-11-01', 43.9687, 43.9687, 43.75, 43.9375, 1003200],
    ['2005-11-02', 43.9687, 44.25, 43.9687, 44.25, 480500],
    ['2005-11-03', 44.2187, 44.375, 44.125, 44.3437, 201300],
    ['2005-11-04', 44.4062, 44.8437, 44.375, 44.8125, 529400]
         ], columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
OHLCV.set_index('Time', inplace=True)

FRAC_CHANGE = [0.711238, 0.211752, 1.0572]

SQN_val = 3.2943

SQN_arr = [np.nan, np.nan, 2.6133, 2.1226]

class MyLibTests(unittest.TestCase):

    def test_fractional_change_len(self):
        data = OHLCV.Close
        self.assertEqual(len(fractional_change(data)), len(data) - 1)

    def test_fractional_change_values(self):
        data = OHLCV.Close
        np.testing.assert_almost_equal(fractional_change(data), FRAC_CHANGE, 4)

    def test_sqn(self):
        data = OHLCV.Close
        self.assertAlmostEqual(sqn(data), SQN_val, 4)

    def test_SQN(self):
        data = OHLCV.Close
        np.testing.assert_almost_equal(SQN(data, 3), SQN_arr, 4)
        

if __name__ == '__main__':
    unittest.main()
