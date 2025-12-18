# system modules
import itertools
import math
import unittest
import warnings

import numpy as np
import pandas as pd

# external modules
import scipy.signal

from parmesan import utils
from parmesan.analysis import spectrum, variance_spectrum

# internal modules
from parmesan.errors import ParmesanWarning
from parmesan.utils import all_argument_combinations, out_warnings


class SpectrumTest(unittest.TestCase):
    @staticmethod
    def generate_oscillation(
        waves,
        linear_trend=None,
        noise=None,
    ):
        def func(t):
            t = np.asanyarray(t).reshape(-1)
            parts = (
                tuple(
                    ampl * np.sin(2 * np.pi * freq * t - phase)
                    for freq, ampl, phase in waves
                )
                + ((noise(t),) if noise else tuple())
                + ((linear_trend(t),) if linear_trend else tuple())
            )
            return np.sum(np.vstack(parts), axis=0)

        return func

    def test_frequency_detection(self):
        """
        Frequency Detection

        This test creates a bunch of different timeseries with different
        frequencies, linear trends and random noise, runs the variance_spectrum()
        function on it and asserts that the correct frequencies are among the
        peaks in the returned power spectrum
        """
        for kwargs in all_argument_combinations(
            {
                "waves": [[[i] * 3 for i in range(1, 10)]],
                "noise": (
                    None,
                    (lambda t: 5 * np.random.random(size=t.size)),
                    (lambda t: 3 * np.random.exponential(size=t.size)),
                ),
                "linear_trend": (
                    None,
                    lambda t: t,
                    lambda t: -2 * t - 3,
                ),
            }
        ):
            with self.subTest(kwargs=kwargs):
                # First column is the actual frequencies in the signal
                actual_freqs = np.vstack(kwargs["waves"])[:, 0]
                # determine the maximum frequency for the waves
                max_freq = np.max(actual_freqs)
                # choose a small enough timestep
                timestep = 1 / max_freq / 10
                signal_generator = self.generate_oscillation(**kwargs)
                s = itertools.count(step=timestep)
                t = np.array([next(s) for i in range(1000)])
                signal = signal_generator(t)
                freq, power = variance_spectrum(t, signal)
                peak_pos, preak_props = scipy.signal.find_peaks(
                    power.m, prominence=power.m * 0.5
                )
                # import matplotlib.pyplot as plt

                # fig, (ax1, ax2) = plt.subplots(ncols=2)
                # pd.Series(signal, index=t).plot(ax=ax1)
                # pd.Series(power, index=freq).plot(ax=ax2)
                # for f in freq[peak_pos]:
                #     ax2.axvline(f, color="red", linestyle=":")
                # for f in actual_freqs:
                #     ax2.axvline(f, color="green", linestyle="--")
                # ax2.set_xscale("log")
                # ax2.set_yscale("log")

                # plt.show()
                self.assertGreaterEqual(
                    set(round(float(f), 1) for f in freq[peak_pos]),
                    set(round(float(f), 1) for f in actual_freqs),
                    msg="Wrong frequencies detected. Signal contains {} "
                    "but {} were detected".format(
                        sorted(actual_freqs), sorted(freq[peak_pos])
                    ),
                )

    def test_parseval_theorem(self):
        """
        Parseval Theorem
        """
        signal_generator = self.generate_oscillation(
            waves=[(0.1, 1, 1), (2, 3, 4), (0.1, 1, 4)],
        )
        for n_samples, kwargs in itertools.product(
            (10, 11),  # even and odd number of samples
            all_argument_combinations(
                {
                    "window": ("hann", "tukey", False),
                    "blocks": (1,),
                    "overlap": (False,),
                    "detrend": ("linear", "constant", False),
                    "interpolation": (None,),
                }
            ),
        ):
            with self.subTest(n_samples=n_samples, **kwargs):
                t = np.linspace(0, 10, n_samples)
                signal = signal_generator(t)
                freq, power, blocks = variance_spectrum(
                    t,
                    signal,
                    returnvalue=("frequency", "power", "blocks"),
                    **kwargs,
                )
                # get the conditioned signal (possibly detrended)
                conditioned_signal = blocks[0]
                # variance of the conditioned signal
                variance = conditioned_signal.var()
                # energy in the frequency domain (integral over the power
                # spectrum) times 2 not necessary because double=True
                # for negative frequencies is the default
                power_sum = np.sum(power[1:])
                #
                # cf. Stull (1988) chapter 8 eq. 8.5a and 8.6.1b:
                #  variance of FFT'd signal equals sum of powers
                #
                # TODO: I don't know why the precision (places=0) is only so
                # bad here.
                self.assertAlmostEqual(variance, power_sum, places=0)

    def test_blocks_decrease_lower_frequency_resolution(self):
        s = pd.Series(
            np.random.random(60),
            index=np.array(np.arange(0, 60, 1), dtype="datetime64[s]"),
        )
        # first column: lowest frequency (should be 0)
        # second column: next frequency (should increase with blocks)
        # third column: highest frequency (should be constant)
        with out_warnings(ParmesanWarning):
            d = np.array(
                [
                    s.parmesan.spectrum(blocks=n).index[[0, 1, -1]]
                    for n in range(1, 60, 1)
                    if (  # only use number of blocks that fit nicely
                        # s.index.size % n == 0
                        s.index.size % math.ceil(n / 2)
                        == 0
                    )
                ]
            )
        self.assertTrue(
            np.allclose(d[:, 0], 0),
            msg="Changing the amount of blocks"
            "changes the lowest frequency and it's not 0, but {}".format(
                d[:, 0]
            ),
        )
        self.assertTrue(
            (np.diff(d[:, 1]) >= 0).all(),
            msg="Increasing the number of blocks "
            "doesn't always increase the lowest frequency!",
        )

    def test_detrend_makes_zero_frequency_coefficient_zero(self):
        for linear_trend, kwargs in itertools.product(
            (True, False),
            all_argument_combinations(
                {
                    "window": ("hann", "tukey", False),
                    "blocks": (1, 3, 10),
                    "overlap": (False, True),
                    "detrend": ("linear", "constant", False),
                    "interpolation": (None, "linear"),
                }
            ),
        ):
            with out_warnings(ParmesanWarning):
                with self.subTest(**kwargs):
                    signal_generator = self.generate_oscillation(
                        waves=[(1, 1, 1), (3, 3, 3), (4, 4, 4)],
                        linear_trend=(lambda x: 3 * x + 4)
                        if linear_trend
                        else lambda x: x,
                    )
                    t = np.linspace(0, 30, 1000)
                    signal = signal_generator(t)
                    freq, power = variance_spectrum(t, signal, **kwargs)
                    if kwargs["detrend"] and not kwargs["window"]:
                        self.assertLess(
                            power[0],
                            10e-5,
                            msg="zero frequency power should "
                            "be 0 when detrending"
                            "and not applying a window, "
                            "but it's {}".format(power[0]),
                        )
