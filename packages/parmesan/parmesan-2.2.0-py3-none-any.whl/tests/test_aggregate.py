# system modules
import unittest

# internal modules
from parmesan.accessor import PARMESAN_ACCESSOR_NAME
from parmesan.aggregate import temporal_cycle

# external modules
import numpy as np
import pandas as pd


class TemporalCycleTest(unittest.TestCase):
    testcases = (
        (
            {
                # increasing integers for three days in hourly resolution
                "times": np.array(np.arange(0, 24 * 3), dtype="datetime64[h]"),
                "x": np.arange(0, 24 * 3),
                # calculate diurnal cycle
                "interval": "D",
                "resolution": "h",
            },
            {
                # resulting index should just be all hours 0...23
                "index": np.arange(0, 24),  # (the 24 is exclusive)
                "groupby": {
                    # this averaging should happen under the hood
                    "mean": np.mean(
                        np.vstack(
                            np.split(
                                np.arange(0, 24 * 3),
                                np.arange(24, 24 * 3 - 1, 24),
                            )
                        ),
                        axis=0,
                    ),
                },
            },
        ),
    )

    def run_tests(
        self,
        pandas_input=None,
        pandas_type=None,
        times_as_index=None,
        times_as_arg=None,
        times_as_colname=None,
        times_as_col=None,
        extra_random_datetime_col=None,
    ):
        for kwargs_template, shouldbe in self.testcases:
            kwargs = kwargs_template.copy()
            if pandas_input:
                if pandas_type is pd.Series:
                    x = pd.Series(kwargs_template["x"])
                elif pandas_type is pd.DataFrame:
                    x = pd.DataFrame({"x": kwargs_template["x"]})
                    if times_as_col:
                        x["times"] = kwargs_template["times"]
                    if extra_random_datetime_col:
                        x["extra_time"] = np.array(
                            np.random.randint(len(x.index)) * 1000000,
                            dtype="datetime64[s]",
                        )
                else:
                    raise ValueError("Either DataFrame or Series!")
                if times_as_index:
                    x.index = kwargs_template["times"]
                kwargs["x"] = x
            if times_as_arg:
                if times_as_colname:
                    kwargs["times"] = (
                        times_as_colname
                        if isinstance(times_as_colname, str)
                        else "times"
                    )
            else:
                kwargs.pop("times", None)

            def check_result(groupby):
                for method, result in shouldbe["groupby"].items():
                    calculated = getattr(groupby, method)()
                    self.assertTrue(
                        np.allclose(
                            calculated["x"]
                            if isinstance(calculated, pd.DataFrame)
                            else calculated,
                            result,
                        ),
                        msg="Resulting {}() is wrong. "
                        "Should be:\n\n{},\n\n... "
                        "but is actually\n\n{}".format(
                            method, result, calculated
                        ),
                    )
                    self.assertTrue(
                        np.allclose(calculated.index, shouldbe["index"]),
                        msg="Resulting index is wrong. "
                        "Should be:\n\n{},\n\n... "
                        "but is actually\n\n{}".format(
                            shouldbe["index"], calculated.index
                        ),
                    )

            # direct invocation
            check_result(temporal_cycle(**kwargs))
            if pandas_input:
                x = kwargs.pop("x")
                check_result(
                    getattr(x, PARMESAN_ACCESSOR_NAME).temporal_cycle(**kwargs)
                )

    def test_ndarray(self):
        self.run_tests(
            pandas_input=False,
            times_as_arg=True,
        )

    def test_ndarray_no_times_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=False,
                times_as_arg=False,
            )

    def test_ndarray_times_as_colname_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=False,
                times_as_arg=True,
                times_as_colname=True,
            )

    def test_series_with_time_index(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.Series,
            times_as_index=True,
            times_as_arg=False,
        )

    def test_series_no_index_with_times_argument(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.Series,
            times_as_index=False,
            times_as_arg=True,
        )

    def test_dataframe_no_index_with_times_argument(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.DataFrame,
            times_as_index=False,
            times_as_arg=True,
        )

    def test_dataframe_with_times_index(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.DataFrame,
            times_as_index=True,
            times_as_arg=False,
        )

    def test_dataframe_with_times_index_and_extra_time_column(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.DataFrame,
            times_as_index=True,
            times_as_arg=False,
            extra_random_datetime_col=True,
        )

    def test_dataframe_times_as_col(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.DataFrame,
            times_as_index=False,
            times_as_arg=False,
            times_as_col=True,
            extra_random_datetime_col=False,
        )

    def test_dataframe_times_as_col_specified_by_arg(self):
        self.run_tests(
            pandas_input=True,
            pandas_type=pd.DataFrame,
            times_as_index=False,
            times_as_arg=True,
            times_as_col=True,
            times_as_colname=True,
            extra_random_datetime_col=True,
        )

    def test_dataframe_no_time_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=True,
                pandas_type=pd.DataFrame,
                times_as_index=False,
                times_as_arg=False,
                extra_random_datetime_col=False,
            )

    def test_dataframe_nonexistant_time_column_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=True,
                pandas_type=pd.DataFrame,
                times_as_index=False,
                times_as_arg=True,
                times_as_colname="doesntexist",
                extra_random_datetime_col=False,
            )

    def test_dataframe_wrong_time_column_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=True,
                pandas_type=pd.DataFrame,
                times_as_index=False,
                times_as_arg=True,
                times_as_colname="x",
                extra_random_datetime_col=False,
            )

    def test_dataframe_no_index_multiple_timecols_raises_error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=True,
                pandas_type=pd.DataFrame,
                times_as_index=False,
                times_as_col=True,
                times_as_arg=False,
                extra_random_datetime_col=True,
            )

    def test_series_no_time_index_raises_Error(self):
        with self.assertRaises(ValueError):
            self.run_tests(
                pandas_input=True,
                pandas_type=pd.Series,
                times_as_index=False,
                times_as_arg=False,
            )
