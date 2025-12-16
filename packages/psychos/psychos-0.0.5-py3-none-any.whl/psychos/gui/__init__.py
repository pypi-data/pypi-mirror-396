"""psychos.gui: Module for creating simple dialogs using Tkinter."""

from typing import TYPE_CHECKING

from ..utils.lazy import attach

submod_attrs = {"dialog": ["Dialog"]}

__getattr__, __dir__, __all__ = attach(__name__, submod_attrs=submod_attrs)

if TYPE_CHECKING:
    __all__ = ["Dialog"]

    from .dialog import Dialog
