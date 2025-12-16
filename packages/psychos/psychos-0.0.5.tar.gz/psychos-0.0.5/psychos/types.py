"""pychos.types: Type hints and aliases for the psychos package."""

from typing import Union, Literal, Tuple, TYPE_CHECKING, NamedTuple, Optional

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "Literal",
    "ColorType",
    "AnchorHorizontal",
    "AnchorVertical",
    "PathStr",
    "UnitType",
    "UnitTransformation",
    "KeyEvent",
    "KeyEventType",
]

PathStr = Union["str", "Path"]

ColorType = Union[
    "str",
    Tuple[int, int, int],
    Tuple[int, int, int, int],
    Tuple[float, float, float],
    Tuple[float, float, float, float],
]
ColorSpace = Literal[
    "auto",
    "rgb",
    "rgba",
    "rgb255",
    "rgba255",
    "hex",
    "hexa",
    "name",
    "hsv",
    "cmyk",
    "yiq",
    "hsl",
    None,
]

# Anchor types for alignment
AnchorHorizontal = Literal["left", "center", "right"]
AnchorVertical = Literal["top", "center", "bottom", "baseline"]

# Unit types
UnitType = Literal["px", "norm", "%", "vw", "vh", "vd", "cm", "mm", "in", "pt", "deg"]
UnitTransformation = Literal[
    "transform", "inverse_transform", "transform_size", "inverse_transform_size"
]


KeyEventType = Literal["press", "release"]


class KeyEvent(NamedTuple):
    """A named tuple representing a key event."""

    key: Optional[str]
    timestamp: float
    modifiers: Optional[str]
    event: KeyEventType


class InteractState(NamedTuple):
    """A named tuple representing the state during interaction."""

    pressed_key: Optional[str]
    pressed_modifiers: Optional[str]
    mouse_x: Optional[float]
    mouse_y: Optional[float]
    mouse_button: Optional[str]
    timestamp: float
    elapsed_time: float