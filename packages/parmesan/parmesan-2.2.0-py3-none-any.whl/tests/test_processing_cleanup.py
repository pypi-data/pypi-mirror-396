# system modules
import unittest

# internal modules
from parmesan.processing.cleanup import find_conspicuous_values

# external modules
import numpy as np


class FindConspicuousValuesTest(unittest.TestCase):
    def test_small_simple_list_one_strange_value(self):
        array = np.array([1, 1, 1, 3, 1, 1, 1, 2])
        conspicuous_values, count = find_conspicuous_values(array)
        self.assertSequenceEqual(list(conspicuous_values), [1])
        self.assertSequenceEqual(list(count), [6])

    def test_outlier_scattered_among_uniform_ints(self):
        array = np.random.randint(-10, 10, 1000)
        outlier_positions = np.unique(
            np.random.randint(0, array.size, size=500)
        )
        array[outlier_positions] = -3
        conspicuous_values, count = find_conspicuous_values(
            array, rel_prominence=0.5
        )
        self.assertEqual(len(conspicuous_values), 1)
        self.assertSetEqual(
            set(conspicuous_values), set(array[outlier_positions])
        )
        self.assertEqual(len(count), 1)
        self.assertGreaterEqual(next(iter(count)), outlier_positions.size)
