"""psychos.utils: Module for utility functions and classes."""
from typing import TYPE_CHECKING

from .lazy import attach

submod_attrs = {
    "colors": ["Color"],
    "decorators": ["docstring", "register"],
    "screens": ["get_screens"],
}

__getattr__, __dir__, __all__ = attach(__name__, submod_attrs=submod_attrs)

if TYPE_CHECKING:
    __all__ = [
        "Color",
        "docstring",
        "register",
        "get_screens",
    ]

    from .colors import Color
    from .decorators import docstring, register
    from .screens import get_screens
