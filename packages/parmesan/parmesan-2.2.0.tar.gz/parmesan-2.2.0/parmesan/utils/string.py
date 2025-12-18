# system modules
import textwrap
import re

# internal modules

# external modules


def find_indentation(s):
    """
    Determine the indentation level of a string. Actually, :mod:`textwrap`
    should provide something like this and probably has it under the hood,
    but here it is...

    Args:
        s (str): the string to analyze

    Returns:
        str : the indentation whitespace
    """
    return "".join(
        next(iter(x))
        for x in map(
            set,
            zip(
                *re.findall(pattern=r"[\r\n]+(\s*)", string="\r\n" + (s or ""))
            ),
        )
        if len(x) == 1
    )


def add_to_docstring(docstring, extra_doc, prepend=False):
    """
    Add a string to a docstring while handling the indentation level

    Args:
        docstring (str): the docstring to add to
        extra_doc (str): the string to add
        prepend (bool, optional): whether to prepend instead of appending
            to the docstring.

    Returns:
        str : the docstring with the string added
    """
    indent = find_indentation(docstring)
    return (
        "{extra_doc}\n\n{old_doc}\n{indent}"
        if prepend
        else "{old_doc}\n\n{extra_doc}\n{indent}"
    ).format(
        old_doc=docstring or "",
        extra_doc=textwrap.indent(
            textwrap.dedent(extra_doc),
            prefix=indent,
        ),
        indent=indent,
    )
