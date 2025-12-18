# system modules
import unittest

# internal modules
from parmesan import errors
from parmesan import bounds

# external modules


class BoundsTest(unittest.TestCase):
    def test_bounds_decorator(self):
        @bounds.ensure((-10, 10), a=(0, 5), c=lambda x, *a, **kw: x > 5)
        def func(a, b, c=1):
            return a + b + c

        with bounds.mode(None):
            self.assertEqual(func(1, 2, 3), 6)

        with bounds.mode("warning"):
            with self.assertWarns(errors.OutOfBoundsWarning):
                self.assertEqual(func(10, 0, 0), 10)

        with bounds.mode("strict"):
            with self.assertRaises(errors.OutOfBoundsError):
                func(10, 0, 0)
