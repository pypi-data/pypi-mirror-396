# system modules
import unittest

# internal modules
from parmesan import stats

# external modules
import numpy as np


class StatsTest(unittest.TestCase):
    def test_rmse(self):
        self.assertAlmostEqual(
            stats.rmse(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4])), 0
        )
        self.assertAlmostEqual(
            stats.rmse(np.array([1, 2, 3, 4]), np.array([2, 3, 4, 5])), 1
        )
        self.assertAlmostEqual(
            stats.rmse(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 6])), 1
        )
        # with median
        self.assertAlmostEqual(
            stats.rmse(
                np.array([1, 2, 3, 4]),
                np.array([2, 3, 4, 5]),
                average=np.median,
            ),
            1,
        )

    def test_mae(self):
        self.assertAlmostEqual(
            stats.mae(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4])), 0
        )
        self.assertAlmostEqual(
            stats.mae(np.array([1, 2, 3, 4]), np.array([2, 3, 4, 5])), 1
        )
        self.assertAlmostEqual(
            stats.mae(np.array([1, 2, 3, 4]), np.array([2, 4, 6, 8])), 2.5
        )

    def test_geothmetic_meandian(self):
        # the original data from https://xkcd.com/2435/
        self.assertAlmostEqual(
            stats.geothmetic_meandian(np.array([1, 1, 2, 3, 5])), 2.089, 3
        )
