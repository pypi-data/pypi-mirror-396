# system modules
import unittest
import operator
import textwrap

# internal modules
from parmesan import utils

# external modules


class StringUtilsTest(unittest.TestCase):
    def test_find_indentation(self):
        for string, indentation in {
            "\n my\n  line  \n indented \n\n \twith one space": " ",
            "   now\n\n   with\n    at least\n   three": "   ",
            "\tone\n\t \ttab": "\t",
        }.items():
            indent = utils.string.find_indentation(string)
            self.assertEqual(
                indent,
                indentation,
                msg="\n=========\n{}\n========\n\nhas indent {} "
                "but find_indentation() says {}".format(
                    string, repr(indentation), repr(indent)
                ),
            )
            self.assertEqual(
                textwrap.indent(textwrap.dedent(string), indent),
                string,
                msg="textwrap.dedent(string) is "
                "\n================\n{}\n===============\n, "
                "re-indented with {} as determined by find_indentation():"
                "\n================\n{}\n===============\n, not "
                "\n================\n{}\n===============\n".format(
                    textwrap.dedent(string),
                    repr(indent),
                    textwrap.indent(textwrap.dedent(string), indent),
                    string,
                ),
            )


class FunctionCollectionTest(unittest.TestCase):
    def test_register(self):
        collection = utils.function.FunctionCollection()

        @collection.register
        def f1(a, b):
            return a + b

        def f2(b, c):
            return b - c

        collection.register(f2)

        with self.assertRaises(TypeError):
            collection(1, 2)

        with self.assertRaises(TypeError):
            collection(b=2)

        self.assertEqual(collection(1, b=2), 3)
        self.assertEqual(collection(a=1, b=2), 3)
        self.assertEqual(collection(b=2, c=1), 1)
