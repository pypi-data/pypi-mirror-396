# system modules
import unittest

# internal modules
from parmesan.analysis import structure

# external modules
import numpy as np
import pandas as pd
import scipy.signal


class StructureFunctionTest(unittest.TestCase):
    def test_structure_function_close_to_one_minus_acf(self):
        """Test if structure function is close to (1 - ACF) for small lags"""
        for seed in range(10):
            with self.subTest(seed=seed):
                np.random.seed(seed)
                series = pd.Series(
                    scipy.signal.detrend(
                        np.cumsum(np.random.uniform(-1, 1, 100)), type="linear"
                    ),
                    index=pd.date_range(
                        "2022-01-01T12:00", freq="1s", periods=100
                    ),
                )
                sf = series.parmesan.structure()
                acf = series.parmesan.autocorrelation(only_overlap=True)
                # only consider couple small lags for comparison as the
                # equality to (1-ACF) is only an approximation for small lags
                maxlag = (
                    series.index.max() - series.index.min()
                ).total_seconds() / 5
                diff = (sf - (1 - acf)).abs()
                reldiff = (diff / sf).abs()
                reldiff = reldiff[np.isfinite(reldiff)]
                # for small lags, absolute error to (1-ACF) less than 0.1
                self.assertTrue((diff.loc[:maxlag] < 0.1).all())
                # for small lags, relative error to (1-ACF) less than 10%
                self.assertTrue((reldiff.loc[:maxlag] < 0.1).all())
