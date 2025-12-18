# system modules
import unittest

# internal modules
from parmesan.accessor import ParmesanAccessor

# external modules
import pandas as pd


class ParmesanAccessorTest(unittest.TestCase):
    def setUp(self):
        self.assertFalse(
            hasattr(ParmesanAccessor, "mymethod"),
            "ParmesanAccessor shouldn't have a mymethod prior before any test",
        )

    def tearDown(self):
        if hasattr(ParmesanAccessor, "mymethod"):
            delattr(ParmesanAccessor, "mymethod")

    def test_register_by_method(self):
        df = pd.DataFrame({"a": [1, 3], "b": [3, 5]})

        def mymethod(x):
            return x.mean()

        ParmesanAccessor.register(mymethod)
        self.assertTrue(
            hasattr(ParmesanAccessor, "mymethod"),
            "ParmesanAccessor should have a mymethod after registration",
        )
        self.assertTrue(
            all(df.parmesan.mymethod() == pd.DataFrame({"a": [2], "b": [4]}))
        )
        self.assertEqual(df.a.parmesan.mymethod(), 2)
        self.assertEqual(df.b.parmesan.mymethod(), 4)

    def test_register_by_decorator(self):
        df = pd.DataFrame({"a": [1, 3], "b": [3, 5]})

        @ParmesanAccessor.register
        def mymethod(x):
            return x.mean()

        self.assertTrue(
            hasattr(ParmesanAccessor, "mymethod"),
            "ParmesanAccessor should have a mymethod after registration",
        )
        self.assertTrue(
            all(df.parmesan.mymethod() == pd.DataFrame({"a": [2], "b": [4]}))
        )
        self.assertEqual(df.a.parmesan.mymethod(), 2)
        self.assertEqual(df.b.parmesan.mymethod(), 4)
