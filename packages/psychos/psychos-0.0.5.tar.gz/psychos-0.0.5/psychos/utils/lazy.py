"""
Lazy loader for Python packages.

This code have been extracted from lazy-loader package (v0.4).
Credits to the original authors:

Copyright (c) 2022--2023, Scientific Python project All rights reserved.

You can find the original code at:
https://github.com/scientific-python/lazy-loader/tree/v0.4

And a copy of the license (BSD 3-Clause) at:
https://github.com/scientific-python/lazy-loader/blob/v0.4/LICENSE.md
"""

import importlib
import importlib.util
import sys

__version__ = "0.4"
__all__ = ["attach"]


def attach(package_name, submodules=None, submod_attrs=None):
    """Attach lazily loaded submodules, functions, or other attributes.

    Typically, modules import submodules and attributes as follows::

      import mysubmodule
      import anothersubmodule

      from .foo import someattr

    The idea is to replace a package's `__getattr__`, `__dir__`, and
    `__all__`, such that all imports work exactly the way they would
    with normal imports, except that the import occurs upon first use.

    The typical way to call this function, replacing the above imports, is::

      __getattr__, __dir__, __all__ = lazy.attach(
        __name__,
        ['mysubmodule', 'anothersubmodule'],
        {'foo': ['someattr']}
      )

    This functionality requires Python 3.7 or higher.

    Parameters
    ----------
    package_name : str
        Typically use ``__name__``.
    submodules : set
        List of submodules to attach.
    submod_attrs : dict
        Dictionary of submodule -> list of attributes / functions.
        These attributes are imported as they are used.

    Returns
    -------
    __getattr__, __dir__, __all__

    Notes
    -----

    This function has been extracted from the lazy-loader package
    (v0.4). The original code can be found at:

    https://github.com/scientific-python/lazy-loader/tree/v0.4

    Copyright (c) 2022--2023, Scientific Python project All rights reserved.

    """
    if submod_attrs is None:
        submod_attrs = {}

    if submodules is None:
        submodules = set()
    else:
        submodules = set(submodules)

    attr_to_modules = {
        attr: mod for mod, attrs in submod_attrs.items() for attr in attrs
    }

    __all__ = sorted(  # pylint: disable=redefined-outer-name
        submodules | attr_to_modules.keys()
    )

    def __getattr__(name):
        if name in submodules:
            return importlib.import_module(f"{package_name}.{name}")
        if name in attr_to_modules:
            submod_path = f"{package_name}.{attr_to_modules[name]}"
            submod = importlib.import_module(submod_path)
            attr = getattr(submod, name)

            # If the attribute lives in a file (module) with the same
            # name as the attribute, ensure that the attribute and *not*
            # the module is accessible on the package.
            if name == attr_to_modules[name]:
                pkg = sys.modules[package_name]
                pkg.__dict__[name] = attr

            return attr

        raise AttributeError(f"No {package_name} attribute {name}")

    def __dir__():
        return __all__

    return __getattr__, __dir__, list(__all__)
