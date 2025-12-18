# system modules
import unittest
import itertools

# internal modules
from parmesan.errors import ParmesanWarning
from parmesan.analysis import (
    evenly_spaced_interval,
    significant_digits,
    autocorrelation_function,
)


# external modules
import numpy as np
import pandas as pd
import scipy.signal
from rich.console import Console

console = Console()


class EvenlySpacedTest(unittest.TestCase):
    def test_significant_digits(self):
        for digits in range(-4, 10):
            with self.subTest(digits=digits):
                d = np.power(10.0, -digits)
                self.assertEqual(
                    significant_digits(np.arange(0, 100 * d, d)),
                    np.clip(digits, 0, None),
                )

    def test_evenly_spaced(self):
        for dt in np.power(10.0, np.arange(-10, 10, 1)):
            with self.subTest(arange=dt):
                self.assertEqual(
                    evenly_spaced_interval(np.arange(0, dt * 100, dt)), dt
                )
            with self.subTest(linspace=dt):
                self.assertEqual(
                    evenly_spaced_interval(np.linspace(0, dt * 100, 100 + 1)),
                    dt,
                )

    def test_evenly_spaced_misc(self):
        with self.assertWarns(ParmesanWarning):
            self.assertLess(evenly_spaced_interval([1, 1, 0]), 0)
            self.assertLess(evenly_spaced_interval([1.1, 1.1, 1.0]), 0)
            self.assertEqual(evenly_spaced_interval([1, 2, 3.1]), 1)
        self.assertEqual(evenly_spaced_interval([1, 2, 3, 4.001]), 1)
        self.assertEqual(evenly_spaced_interval([1, 2, 3.001, 4.002]), 1)


class AutocorrelationTest(unittest.TestCase):
    def assertRelativelyEqual(self, x, expected, fraction, msg=None):
        self.assertLessEqual(
            (f := abs((x - expected) / expected)),
            fraction,
            msg=(
                f"{x} is more than {fraction * 100}% ({f*100}%) away from {expected}\n{msg}"
                if msg
                else None
            ),
        )

    def test_sin_autocorrelation(self):
        # 3 Minutes of 10Hz data
        ts = pd.date_range(
            "2023-01-01T00:00:00", "2023-01-01T00:03:00", freq="100ms"
        )
        for period, phase in itertools.product((10, 30, 40), (0, 1, 2)):
            with self.subTest(period=period, phase=phase):
                x = pd.Series(
                    np.sin(
                        (t := (ts - ts.min()).total_seconds())
                        / period
                        * (2 * np.pi)
                        + phase
                    ),
                    index=ts,
                )
                for only_overlap in itertools.product((True, False)):
                    with self.subTest(only_overlap=only_overlap):
                        acf = x.parmesan.autocorrelation(
                            only_overlap=only_overlap
                        )
                        if not only_overlap:
                            self.assertTrue(
                                (
                                    within := (-1.00001 <= acf)
                                    & (acf <= 1.00001)
                                ).all(),
                                msg=f"acf is not within [-1;1]:\n{acf[~within] = }",
                            )
                        self.assertAlmostEqual(
                            acf.loc[0],
                            1,
                            places=4,
                            msg="acf is not 1 at lag 0",
                        )
                        # acf ridges
                        for i, peak in enumerate(
                            # only first peaks, rest is wiggly
                            scipy.signal.find_peaks(acf)[0][:3],
                            start=1,
                        ):
                            self.assertRelativelyEqual(
                                acf.index[peak],
                                i * period,
                                fraction=0.01,
                                msg=f"Peak #{i} is not at a full period",
                            )
                            self.assertGreaterEqual(
                                acf.loc[acf.index[peak]],
                                0,
                                msg=f"Peak #{i} has negative acf",
                            )
                        # acf valleys
                        for i, valley in enumerate(
                            # only first valleys, rest is wiggly
                            scipy.signal.find_peaks(-acf)[0][:3],
                            start=1,
                        ):
                            self.assertRelativelyEqual(
                                acf.index[valley],
                                period * (i - 1 + 0.5),
                                fraction=0.01,
                                msg=f"valley #{i} is not at a half period",
                            )
                            self.assertLessEqual(
                                acf.loc[acf.index[valley]],
                                0,
                                msg=f"valley #{i} has positive acf",
                            )

    def test_autocorrelation_output_interval(self):
        x = np.sin(t := np.linspace(0, 2 * np.pi, 10))
        lags, acf = autocorrelation_function(
            times=t, signal=x, only_overlap=False
        )
        self.assertTrue(
            np.all((-1 <= acf) & (acf <= 1)), "acf not within [-1;1]"
        )
