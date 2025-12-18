# system modules
import inspect
import itertools
import difflib
from inspect import Parameter
import textwrap

# internal modules
from parmesan import utils

# external modules


class FunctionCollection:
    """
    Collection of functions returning the same thing
    """

    @property
    def registered_functions(self):
        try:
            return self._registered_functions
        except AttributeError:
            self._registered_functions = set()
        return self._registered_functions

    def register(self, func):
        """
        Register a callable to this collection

        .. note::

            This can be used as a decorator:

            .. code-block:: python

                collection = FunctionCollection()

                @collection.register
                def myfunc(a,b):
                    return a+b

                # now myfunc is registered in collection
        """
        if func in self.registered_functions:
            return func
        package_name = next(iter(__name__.split(".")), "")
        self_module, self_name = next(
            (
                (m, n)
                for m, n in utils.find_object(self)
                if m.startswith(package_name)
            ),
            (None, None),
        )
        func.__doc__ = utils.string.add_to_docstring(
            getattr(func, "__doc__", "") or "",
            textwrap.dedent(
                """
            .. hint::

                This function is :any:`FunctionCollection.register` ed to
                :any:`{collection_module}.{collection_name}`,
                meaning you can *also* use it like this:

                .. code-block:: python

                    {collection_module}.{collection_name}({args})
            """.format(
                    collection_name=self_name,
                    collection_module=self_module,
                    func=func,
                    args=", ".join(
                        {
                            Parameter.VAR_POSITIONAL: "...".format,
                            Parameter.VAR_KEYWORD: "...".format,
                            Parameter.POSITIONAL_OR_KEYWORD: "{}=...".format,
                            Parameter.POSITIONAL_ONLY: "{}".format,
                            Parameter.KEYWORD_ONLY: "{}=...".format,
                        }.get(p.kind, "{}".format)(n)
                        for n, p in inspect.signature(func).parameters.items()
                    ),
                )
            ),
        )
        self.registered_functions.add(func)
        # TODO: Would be nice to add a note to self.__doc__ that this function
        # was registered. The below is not seen by Sphinx. In IPython you can
        # see it. Don't know why.
        self.__doc__ = utils.string.add_to_docstring(
            getattr(self, "__doc__", "") or "",
            """
            :any:`{func.__module__}.{func.__name__}` was
            registered to this collection.
            """.format(
                func=func
            ),
        )
        return func

    def matching_functions(self, *args, **kwargs):
        """
        Generator yielding registered functions than can be called with the
        given keyword arguments.
        """
        for fun in self.registered_functions:
            signature = inspect.signature(fun)
            kwargs_combs = [kwargs]
            # handle @from_sympy-decorated functions that accept more than
            # the signatured arguments
            if argaliases := getattr(fun, "_arg_aliases", None):
                # aliases[givenkwarg] = {alias1,alias2,...}
                aliases = {
                    k: next((a for a in argaliases if k in a), set([k]))
                    for k in kwargs
                }
                # append all combinations of aliases
                kwargs_combs = itertools.chain(
                    kwargs_combs,
                    (
                        # we need {newkwarg:oldkwargvalue, ...}
                        {
                            n: next(
                                v
                                for k, v in kwargs.items()
                                if k in aliases.get(k, [])
                            )
                            for n in comb
                        }
                        # comb = e.g. ("T","mixing_ratio")
                        for comb in itertools.product(*aliases.values())
                    ),
                )

            def working_kwargs():
                for kw in kwargs_combs:
                    try:
                        bound_args = signature.bind(*args, **kw)
                    except TypeError as e:
                        continue
                    yield kw

            try:
                next(working_kwargs())
            except StopIteration:
                continue
            yield fun

    @staticmethod
    def signature_from_args(*args, **kwargs):
        return inspect.Signature(
            itertools.chain(
                (
                    inspect.Parameter(
                        a, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD
                    )
                    for a in args
                ),
                (
                    inspect.Parameter(a, kind=inspect.Parameter.KEYWORD_ONLY)
                    for a in kwargs
                ),
            )
        )

    def similar_functions(self, *args, **kwargs):
        """
        Generator yielding similar functions by comparing the signature strings

        Yields:
            function, divergence : the function and the divergence as amount of
            differences between the signature strings
        """
        signature = self.signature_from_args(*args, **kwargs)

        def divergence(sig1, sig2):
            return sum(
                d[0] != " " for d in difflib.ndiff(str(sig1), str(sig2))
            )

        for fun in self.registered_functions:
            yield fun, divergence(signature, inspect.signature(fun))

    def __call__(self, *args, **kwargs):
        """
        Call a registered function with a matching signature
        """
        funcs = set(self.matching_functions(*args, **kwargs))
        if not funcs:
            similar_funcs = self.similar_functions(*args, **kwargs)
            package_name = next(iter(__name__.split(".")), "")
            self_module, self_name = next(
                (
                    (m, n)
                    for m, n in utils.find_object(self)
                    if m.startswith(package_name)
                ),
                ("module", "collection"),
            )
            raise TypeError(
                "None of the {} registered "
                "functions in this collection {} can be "
                "called with the {} arguments ({}){}".format(
                    len(self.registered_functions),
                    repr(self_name),
                    len(args) + len(kwargs),
                    ", ".join(
                        itertools.chain(
                            map(repr, args),
                            map("{}=...".format, kwargs.keys()),
                        )
                    ),
                    ". Did you mean one "
                    "of the following signatures?\n\n{}".format(
                        "\n".join(
                            "{}{}".format(self_name, inspect.signature(f))
                            for f, d in sorted(
                                similar_funcs, key=lambda x: x[1]
                            )
                        )
                    )
                    if similar_funcs
                    else "",
                )
            )
        if len(funcs) > 1:
            raise TypeError(
                "{} registered functions in this collection can be "
                "called with {} arguments ({}):\n\n{}{}".format(
                    len(funcs),
                    len(args) + len(kwargs),
                    ", ".join(
                        itertools.chain(
                            map(repr, args),
                            map("{}=...".format, kwargs.keys()),
                        )
                    ),
                    "\n".join(
                        ".".join(filter(bool, [f.__module__, f.__name__]))
                        for f in funcs
                    ),
                    "\n\nMaybe try specifying the "
                    "arguments as keywords (arg=..., other=...)"
                    if args
                    else "",
                )
            )
        # at this point, there's only one function present
        func = next(iter(funcs))
        return func(*args, **kwargs)

    def __repr__(self):
        return (
            f"Collection of {len(self.registered_functions)} functions:\n"
            f"{', '.join(f.__name__ for f in self.registered_functions)}"
        )
