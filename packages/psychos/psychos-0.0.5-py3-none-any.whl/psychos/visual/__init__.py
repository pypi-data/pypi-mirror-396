"""psychos.visual: Module for creating visual elements in a Pyglet window."""

from typing import TYPE_CHECKING

from ..utils.lazy import attach

submod_attrs = {
    "window": ["Window", "get_window"],
    "text": ["Text"],
    "image": ["Image"],
    "slider": ["Slider"],
    "units": ["Unit"],
    "rectangle": ["Rectangle"],
    "bordered_rectangle": ["BorderedRectangle"],
    "gabor": ["Gabor"],
    "raw_image": ["RawImage"],
    "circle": ["Circle"],
    
}

__getattr__, __dir__, __all__ = attach(__name__, submod_attrs=submod_attrs)

if TYPE_CHECKING:
    __all__ = [
        "Window",
        "get_window",
        "Image",
        "Text",
        "Unit",
        "Rectangle",
        "BorderedRectangle",
        "Gabor",
        "RawImage",
        "Circle",
        "Slider",
    ]

    from .window import Window, get_window
    from .text import Text
    from .image import Image
    from .units import Unit
    from .rectangle import Rectangle
    from .bordered_rectangle import BorderedRectangle
    from .gabor import Gabor
    from .raw_image import RawImage
    from .circle import Circle
    from .slider import Slider
