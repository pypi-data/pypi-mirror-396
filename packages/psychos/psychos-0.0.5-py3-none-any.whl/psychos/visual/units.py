"""psychos.visual.units: Module with unit systems for converting between coordinate systems."""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Type, TYPE_CHECKING, Union, Optional
import re

from ..types import UnitTransformation, UnitType
from ..utils import register

if TYPE_CHECKING:
    from psychos.visual.window import Window

__all__ = [
    "Unit",
    "PixelUnits",
    "NormalizedUnits",
    "PercentageUnit",
    "VWUnit",
    "VHUnit",
    "CMUnit",
    "VDUnit",
    "MMUnit",
    "PTUnit",
    "DegUnit",
    "INUnit",
    "parse_width",
    "parse_height",
]

UNIT_SYSTEMS: Dict["UnitTransformation", Type["Unit"]] = {}


class Unit(ABC):
    """
    Abstract base class for different unit systems that transform
    normalized or other unit types into pixel values.
    """

    def __init__(self, window: "Window"):
        self.window = window

    @classmethod
    def from_name(cls, name: Union["UnitType", "Unit"], window: "Window") -> "Unit":
        """
        Instantiate a unit system class by name or return the instance if already provided.

        Parameters
        ----------
        name : Union[str, Unit]
            The name of the unit system or an instance of Unit.
        window : Window
            The window object, used to get the size for the transformation.

        Returns
        -------
        Unit
            An instance of the unit system class or the provided Unit instance.
        """
        if isinstance(name, Unit):
            return name  # If already an instance of Unit, return it directly

        unit_cls = UNIT_SYSTEMS.get(name)
        if unit_cls is None:
            raise ValueError(
                f"Unknown unit system: {name}. "
                f"Available systems: {list(UNIT_SYSTEMS.keys())}"
            )
        return unit_cls(window=window)

    def __call__(
        self,
        x: Union[float, int],
        y: Union[float, int],
        transformation: UnitTransformation = "transform",
    ) -> Tuple[Union[int, float], Union[int, float]]:
        """
        Call method to dynamically apply a transformation based on the specified type.

        Parameters
        ----------
        x : Union[float, int]
            The x-coordinate or width.
        y : Union[float, int]
            The y-coordinate or height.
        transformation : UnitTransformation, default="transform"
            The type of transformation to apply:
            - "transform" applies coordinate transformation from units to pixels.
            - "inverse_transform" applies coordinate transformation from pixels to units.
            - "transform_size" converts size from units to pixel values.
            - "inverse_transform_size" converts size from pixel values to units.

        Returns
        -------
        Tuple[Union[int, float], Union[int, float]]
            The transformed coordinates or size based on the chosen transformation.
        """

        if transformation == "transform":
            return self.transform(x, y)
        if transformation == "inverse_transform":
            return self.inverse_transform(x, y)
        if transformation == "transform_size":
            return self.transform_size(x, y)
        if transformation == "inverse_transform_size":
            return self.inverse_transform_size(x, y)

        raise ValueError(f"Unknown transformation type: {transformation}")

    @abstractmethod
    def transform(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert coordinates from units to pixel values.

        Parameters
        ----------
        x : float
            The x-coordinate.
        y : float
            The y-coordinate.

        Returns
        -------
        Tuple[int, int]
            The pixel coordinates.
        """

    @abstractmethod
    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        """
        Convert coordinates from pixel values to units.

        Parameters
        ----------
        x : int
            The x-coordinate in pixels.
        y : int
            The y-coordinate in pixels.

        Returns
        -------
        Tuple[float, float]
            The coordinates in the unit system.
        """

    @abstractmethod
    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        """
        Convert size from units to pixel values.

        Parameters
        ----------
        width : float
            The width in the unit system.
        height : float
            The height in the unit system.

        Returns
        -------
        Tuple[int, int]
            The width and height in pixel values.
        """

    @abstractmethod
    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        """
        Convert size from pixel values to units.

        Parameters
        ----------
        width : int
            The width in pixels.
        height : int
            The height in pixels.

        Returns
        -------
        Tuple[float, float]
            The width and height in the unit system.
        """


@register("px", UNIT_SYSTEMS)
class PixelUnits(Unit):
    """
    Pixel unit system.

    This class is a no-op, as Pyglet uses pixel units by default.
    """

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        return int(x), int(y)

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        return float(x), float(y)

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        return int(width), int(height)

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        return float(width), float(height)


@register("norm", UNIT_SYSTEMS)
class NormalizedUnits(Unit):
    """
    A unit system that normalizes coordinates and sizes with respect to the window dimensions.

    In this normalized system:
    - (1, 1) represents the top-right corner of the window.
    - (-1, -1) represents the bottom-left corner of the window.
    - (0, 0) represents the center of the window.
    - (-1, 1) represents the top-left corner of the window.
    - (1, -1) represents the bottom-right corner of the window.
    """

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int((x + 1) * self.window.width / 2)
        x_pixel = min(max(x_pixel, 0), self.window.width - 1)
        y_pixel = int((1 + y) * self.window.height / 2)
        y_pixel = min(max(y_pixel, 0), self.window.height - 1)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_unit = (x / self.window.width) * 2 - 1
        y_unit = (y / self.window.height) * 2 - 1

        return x_unit, y_unit

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(width * self.window.width / 2)
        height_pixel = int(height * self.window.height / 2)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_unit = (width / self.window.width) * 2
        height_unit = (height / self.window.height) * 2

        return width_unit, height_unit


@register("%", UNIT_SYSTEMS)
class PercentageUnit(Unit):
    """
    Percentage unit system.

    - 100% width corresponds to the full width of the window.
    - 100% height corresponds to the full height of the window.
    """

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int((x / 100) * self.window.width)
        y_pixel = int((y / 100) * self.window.height)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_percentage = (x / self.window.width) * 100
        y_percentage = (y / self.window.height) * 100

        return x_percentage, y_percentage

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int((width / 100) * self.window.width)
        height_pixel = int((height / 100) * self.window.height)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_percentage = (width / self.window.width) * 100
        height_percentage = (height / self.window.height) * 100

        return width_percentage, height_percentage


@register("vw", UNIT_SYSTEMS)
class VWUnit(Unit):
    """
    VW (viewport width) unit system.

    - 1vw is 1% of the window's width.
    """

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int((x / 100) * self.window.width)
        y_pixel = int((y / 100) * self.window.width)  # vw is relative to window width

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_vw = (x / self.window.width) * 100
        y_vw = (y / self.window.width) * 100

        return x_vw, y_vw

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int((width / 100) * self.window.width)
        height_pixel = int(
            (height / 100) * self.window.width
        )  # vw is relative to width

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_vw = (width / self.window.width) * 100
        height_vw = (height / self.window.width) * 100

        return width_vw, height_vw


@register("vh", UNIT_SYSTEMS)
class VHUnit(Unit):
    """
    VH (viewport height) unit system.

    - 1vh is 1% of the window's height.
    """

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int((x / 100) * self.window.height)  # vh is relative to window height
        y_pixel = int((y / 100) * self.window.height)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_vh = (x / self.window.height) * 100
        y_vh = (y / self.window.height) * 100

        return x_vh, y_vh

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(
            (width / 100) * self.window.height
        )  # vh is relative to height
        height_pixel = int((height / 100) * self.window.height)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_vh = (width / self.window.height) * 100
        height_vh = (height / self.window.height) * 100

        return width_vh, height_vh


@register("vd", UNIT_SYSTEMS)
class VDUnit(Unit):
    """
    Viewport Diagonal (vd) unit system.

    1vd is 1% of the diagonal of the window.

    This unit is useful for ensuring elements are scaled proportionally based on the 
    diagonal of the window.
    """

    @property
    def diagonal(self) -> float:
        """
        Calculate the diagonal of the window dynamically.
        """
        return (self.window.width**2 + self.window.height**2) ** 0.5

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int((x / 100) * self.diagonal)
        y_pixel = int((y / 100) * self.diagonal)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_vd = (x / self.diagonal) * 100
        y_vd = (y / self.diagonal) * 100

        return x_vd, y_vd

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int((width / 100) * self.diagonal)
        height_pixel = int((height / 100) * self.diagonal)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_vd = (width / self.diagonal) * 100
        height_vd = (height / self.diagonal) * 100

        return width_vd, height_vd


@register("cm", UNIT_SYSTEMS)
class CMUnit(Unit):
    """
    Centimeter (cm) unit system.

    This unit system converts coordinates and sizes between centimeters and pixels
    using the screen's physical dimensions and resolution (DPI).

    - 1 cm corresponds to a specific number of pixels based on the screen's DPI.
    """

    @property
    def pixels_per_cm(self) -> float:
        """
        Calculate pixels per centimeter based on the current screen DPI.
        """
        return self.window.dpi / 2.54  # 1 inch = 2.54 cm

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int(x * self.pixels_per_cm)
        y_pixel = int(y * self.pixels_per_cm)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_cm = x / self.pixels_per_cm
        y_cm = y / self.pixels_per_cm

        return x_cm, y_cm

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(width * self.pixels_per_cm)
        height_pixel = int(height * self.pixels_per_cm)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_cm = width / self.pixels_per_cm
        height_cm = height / self.pixels_per_cm

        return width_cm, height_cm


@register("mm", UNIT_SYSTEMS)
class MMUnit(Unit):
    """
    Millimeter (mm) unit system.

    1mm corresponds to a specific number of pixels based on the screen's DPI.

    This unit is useful for ensuring accurate physical dimensions in millimeters.
    """

    @property
    def pixels_per_mm(self) -> float:
        """
        Calculate pixels per millimeter based on the current screen DPI.
        """
        return self.window.dpi / 25.4  # 1 inch = 25.4 mm

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int(x * self.pixels_per_mm)
        y_pixel = int(y * self.pixels_per_mm)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_mm = x / self.pixels_per_mm
        y_mm = y / self.pixels_per_mm

        return x_mm, y_mm

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(width * self.pixels_per_mm)
        height_pixel = int(height * self.pixels_per_mm)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_mm = width / self.pixels_per_mm
        height_mm = height / self.pixels_per_mm

        return width_mm, height_mm


@register("in", UNIT_SYSTEMS)
class INUnit(Unit):
    """
    Inches (in) unit system.

    This unit system converts inches to pixels based on the screen's DPI.
    """

    @property
    def dpi(self) -> float:
        """
        Get the current screen DPI.
        """
        return self.window.dpi

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int(x * self.dpi)
        y_pixel = int(y * self.dpi)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_in = x / self.dpi
        y_in = y / self.dpi

        return x_in, y_in

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(width * self.dpi)
        height_pixel = int(height * self.dpi)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_in = width / self.dpi
        height_in = height / self.dpi

        return width_in, height_in


@register("pt", UNIT_SYSTEMS)
class PTUnit(Unit):
    """
    Points (pt) unit system.

    1pt corresponds to a specific number of pixels based on the screen's DPI.

    This unit is useful for typographic elements or for aligning designs with text-based layouts.
    """

    @property
    def pixels_per_pt(self) -> float:
        """
        Calculate pixels per point based on the current screen DPI.
        """
        return self.window.dpi / 72  # 1pt = 1/72 inch

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_pixel = int(x * self.pixels_per_pt)
        y_pixel = int(y * self.pixels_per_pt)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_pt = x / self.pixels_per_pt
        y_pt = y / self.pixels_per_pt

        return x_pt, y_pt

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        width_pixel = int(width * self.pixels_per_pt)
        height_pixel = int(height * self.pixels_per_pt)

        return width_pixel, height_pixel

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        width_pt = width / self.pixels_per_pt
        height_pt = height / self.pixels_per_pt

        return width_pt, height_pt


@register("deg", UNIT_SYSTEMS)
class DegUnit(Unit):
    """
    Degrees of visual angle (deg) unit system.

    This unit system converts degrees of visual angle into pixels based on the distance between
    the viewer and the screen.

    It requires a known distance from the screen to accurately compute the size in pixels.
    """

    @property
    def pixels_per_cm(self) -> float:
        """
        Calculate pixels per centimeter based on the current screen DPI.
        """
        return self.window.dpi / 2.54  # 1 inch = 2.54 cm

    @property
    def distance_cm(self) -> float:
        """
        Get the distance from the viewer to the screen in centimeters.
        """
        return self.window.distance

    def transform(self, x: float, y: float) -> Tuple[int, int]:
        x_rad = (x / 360) * 2 * 3.14159  # Convert degrees to radians
        y_rad = (y / 360) * 2 * 3.14159

        x_cm = 2 * self.distance_cm * (x_rad / 2)
        y_cm = 2 * self.distance_cm * (y_rad / 2)

        x_pixel = int(x_cm * self.pixels_per_cm)
        y_pixel = int(y_cm * self.pixels_per_cm)

        return x_pixel, y_pixel

    def inverse_transform(self, x: int, y: int) -> Tuple[float, float]:
        x_cm = x / self.pixels_per_cm
        y_cm = y / self.pixels_per_cm

        x_rad = 2 * (x_cm / (2 * self.distance_cm))
        y_rad = 2 * (y_cm / (2 * self.distance_cm))

        x_deg = (x_rad / (2 * 3.14159)) * 360
        y_deg = (y_rad / (2 * 3.14159)) * 360

        return x_deg, y_deg

    def transform_size(self, width: float, height: float) -> Tuple[int, int]:
        return self.transform(width, height)

    def inverse_transform_size(self, width: int, height: int) -> Tuple[float, float]:
        return self.inverse_transform(width, height)


def _parse_size_value(
    value: Optional[Union[str, float, int]], default: str = "px"
) -> Tuple[float, str]:
    """
    Parse a size value and return a tuple with the numeric value and the unit.

    Parameters
    ----------
    value : Optional[Union[str, float, int]]
        The value to parse. Can be a number (int or float) or a string with units.
    default : str, default="px"
        The default unit to use if no unit is provided with the input.

    Returns
    -------
    Tuple[float, str]
        A tuple containing the numeric value and the unit.

    Raises
    ------
    ValueError
        If the input string format is incorrect or cannot be parsed.
    """

    if value is None:
        return None, default

    # If the value is a number, return it with the default unit
    if isinstance(value, (int, float)):
        return float(value), default

    # If the value is a string, trim spaces and lowercase it
    value = value.strip().lower()

    # Regular expression to match {number}{optional spaces}{unit}
    match = re.match(r"(-?\d*\.?\d+)\s*([a-z%]*)", value)
    if not match:
        raise ValueError(f"Invalid format for size value: {value}")

    number = float(match.group(1))  # Convert the number part to float
    unit = match.group(2) or default  # Use default unit if none provided

    return number, unit


def parse_width(
    width: Optional[Union[str, float, int]],
    default: str = "px",
    window: "Window" = None,
) -> Optional[int]:
    """
    Parse the width input and convert it into pixel values based on the specified units.

    Parameters
    ----------
    width : Optional[Union[str, float, int]]
        The width to be parsed. Can be a number, a string with units, or None.
    default : str, default="px"
        The default unit system to use if no units are provided with the input.
    window : Optional[Window], default=None
        The window object used for unit conversion. If None, the global default window will be used.

    Returns
    -------
    Optional[int]
        The parsed width in pixel values, or None if the input was None.

    Raises
    ------
    ValueError
        If the input string format is incorrect or cannot be parsed.
    """

    if width is None:
        return None

    # Parse the value to get the number and unit
    number, unit = _parse_size_value(width, default)

    # Get the appropriate unit system based on the unit name
    unit_system = Unit.from_name(unit, window)

    # Transform the width from the given unit to pixels
    return unit_system.transform_size(number, 0)[0]  # Only the width is transformed


def parse_height(
    height: Optional[Union[str, float, int]],
    default: str = "px",
    window: "Window" = None,
) -> Optional[int]:
    """
    Parse the height input and convert it into pixel values based on the specified units.

    Parameters
    ----------
    height : Optional[Union[str, float, int]]
        The height to be parsed. Can be a number, a string with units, or None.
    default : str, default="px"
        The default unit system to use if no units are provided with the input.
    window : Optional[Window], default=None
        The window object used for unit conversion. If None, the global default window will be used.

    Returns
    -------
    Optional[int]
        The parsed height in pixel values, or None if the input was None.

    Raises
    ------
    ValueError
        If the input string format is incorrect or cannot be parsed.
    """

    if height is None:
        return None

    # Parse the value to get the number and unit
    number, unit = _parse_size_value(height, default)

    # Get the appropriate unit system based on the unit name
    unit_system = Unit.from_name(unit, window)

    # Transform the height from the given unit to pixels
    return unit_system.transform_size(0, number)[1]
