# system modules
import unittest

# internal modules
from parmesan.symbols import *

# external modules
import pandas as pd


class ParmesanSymbolsTest(unittest.TestCase):
    def test_get_function(self):
        funs = list(get_function(result=r, generate=False))
        self.assertGreater(len(funs), 0)
        funs_with_p = set(f for f in funs if p in f.equation.free_symbols)
        funs_with_p_search = set(
            get_function(result=r, inputs=[p], generate=False)
        )
        self.assertEqual(funs_with_p, funs_with_p_search)
