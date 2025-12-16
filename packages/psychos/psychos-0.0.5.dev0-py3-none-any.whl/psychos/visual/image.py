"""psychos.visual.image: Module with the Image class to display images in a Pyglet window."""
from typing import Optional, Union, Tuple, TYPE_CHECKING

from pyglet.sprite import Sprite
from pyglet.image import load

from .window import get_window
from .units import Unit, parse_height, parse_width

if TYPE_CHECKING:
    from ..visual.window import Window
    from ..types import UnitType, AnchorHorizontal, AnchorVertical, PathStr


__all__ = ["Image"]


class Image(Sprite):
    """
    A class to display an image in a Pyglet window using the Sprite component.

    This class supports positioning, scaling, and rotation of the image, as well as custom 
    anchor points.

    Parameters
    ----------
    image_path : PathStr
        The path to the image file to be displayed.
    position : Tuple[float, float], default=(0, 0)
        The position of the image in the window, based on the defined coordinate system.
    width : Optional[float], default=None
        The target width to scale the image to. Cannot be used in conjunction with height and scale.
    height : Optional[float], default=None
        The target height to scale the image to. Cannot be used in conjunction with width and scale.
    scale : Optional[float], default=None
        A uniform scaling factor for the image. Cannot be used if width or height is specified.
    rotation : float, default=0
        The rotation angle of the image in degrees.
    anchor_x : AnchorHorizontal, default="center"
        The horizontal anchor alignment for the image.
    anchor_y : AnchorVertical, default="center"
        The vertical anchor alignment for the image.
    window : Optional[Window], default=None
        The window in which the image will be displayed. If None, the default window is used.
    coordinate_units : Optional[Union[UnitType, Units]], default=None
        The coordinate system to be used for positioning the image. If None, the window's default 
        unit system is used.
    kwargs : dict
        Additional keyword arguments passed to the Pyglet Sprite class.

    Attributes
    ----------
    rotation : float
        The rotation of the image in degrees.
    scale : float
        The scale factor of the image. If both width and height are provided, this will be a tuple 
        of (scale_x, scale_y).

    Examples
    --------
    Basic usage with default positioning:

    >>> image = Image("path/to/image.png")
    >>> image.draw()

    Scaling the image based on width:

    >>> image = Image("path/to/image.png", width=200)
    >>> image.draw()

    Scaling the image based on height:

    >>> image = Image("path/to/image.png", height=150)
    >>> image.draw()

    Using a custom scaling factor:

    >>> image = Image("path/to/image.png", scale=2.0)
    >>> image.draw()

    Positioning the image at a specific coordinate:

    >>> image = Image("path/to/image.png", position=(100, 200))
    >>> image.draw()

    Rotating the image by 45 degrees:

    >>> image = Image("path/to/image.png", rotation=45)
    >>> image.draw()

    Custom anchor points (e.g., top-right):

    >>> image = Image("path/to/image.png", anchor_x="right", anchor_y="top")
    >>> image.draw()

    Setting both width and height for non-uniform scaling:

    >>> image = Image("path/to/image.png", width=200, height=300)
    >>> image.draw()

    Dynamically change position:

    >>> image.position = (150, 250)
    >>> image.draw()
    """

    def __init__(
        self,
        image_path: "PathStr",
        position: Tuple[float, float] = (0, 0),
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        rotation: float = 0,
        anchor_x: "AnchorHorizontal" = "center",
        anchor_y: "AnchorVertical" = "center",
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", "Unit"]] = None,
        **kwargs,
    ):
        # Retrieve the window and set coordinate system
        self.window = window or get_window()
        self._coordinates = None
        self.coordinates = coordinates

        x, y = self.coordinates.transform(*position)

        width = parse_width(width, window=self.window)
        height = parse_height(height, window=self.window)

        # Load the image from the given path
        image = load(filename=image_path)
        image.anchor_x, image.anchor_y = _transform_image_anchor(
            anchor_x, anchor_y, image.width, image.height
        )
        scale = _compute_scale(width, height, scale, image.width, image.height)

        # Initialize Sprite (superclass)
        super().__init__(img=image, x=x, y=y, **kwargs)
        self.rotation = rotation

        if isinstance(scale, (int, float)):
            self.scale = scale
        else:
            self.scale_x, self.scale_y = scale

    @property
    def position(self) -> Tuple[float, float]:
        """Get the position of the image."""
        return self.x, self.y

    @position.setter
    def position(self, value: Tuple[float, float]):
        """Set the position of the image."""
        x, y = self.coordinate_units(*value)
        self.x = x
        self.y = y

    @property
    def coordinates(self) -> "Unit":
        """Get the coordinate system used for the text."""
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value: Optional[Union["UnitType", "Unit"]]):
        """Set the coordinate system used for the text."""
        if value is None:
            self._coordinates = self.window.coordinates
        else:
            self._coordinates = Unit.from_name(value, window=self.window)

    def draw(self) -> "Image":
        super().draw()
        return self


def _transform_image_anchor(
    anchor_x: "AnchorHorizontal",
    anchor_y: "AnchorVertical",
    width: float,
    height: float,
) -> Tuple[float, float]:
    """Gets the anchor point for an image based on the given anchor values."""

    # Dictionary mapping for x-axis anchor
    anchor_x_mapping = {"left": 0, "center": width // 2, "right": width}

    # Dictionary mapping for y-axis anchor
    anchor_y_mapping = {
        "bottom": 0,
        "baseline": 0,
        "center": height // 2,
        "top": height,
    }

    try:
        x = anchor_x_mapping[anchor_x]
    except KeyError as e:
        raise ValueError(f"Invalid anchor_x value: {anchor_x}") from e

    try:
        y = anchor_y_mapping[anchor_y]
    except KeyError as e:
        raise ValueError(f"Invalid anchor_y value: {anchor_y}") from e

    return int(x), int(y)


def _compute_scale(
    width: Optional[float],
    height: Optional[float],
    scale: Optional[float],
    image_width: int,
    image_height: int,
) -> Union[float, Tuple[float, float]]:
    """
    Compute the scale for an image based on the provided width, height, or scale.

    Parameters
    ----------
    width : Optional[float]
        The desired width of the image. If provided, will scale the image to this width.
    height : Optional[float]
        The desired height of the image. If provided, will scale the image to this height.
    scale : Optional[float]
        The scaling factor for the image. Cannot be used if width or height is provided.
    image_width : int
        The original width of the image.
    image_height : int
        The original height of the image.

    Returns
    -------
    Union[float, Tuple[float, float]]
        The computed scale as a single float (if width or height is provided, but not both),
        or a tuple (scale_x, scale_y) if both width and height are provided.

    Raises
    ------
    ValueError
        If scale is specified along with width or height.
    """

    # Case 1: If all are None, return a scale of 1
    if width is None and height is None and scale is None:
        return 1.0

    # Case 2: If scale is provided but either width or height is also set, raise an error
    if scale is not None and (width is not None or height is not None):
        raise ValueError("Scale cannot be specified if width or height are set.")

    # Case 3: If width is provided and height is not, compute scale to match width
    if width is not None and height is None:
        return width / image_width

    # Case 4: If height is provided and width is not, compute scale to match height
    if height is not None and width is None:
        return height / image_height

    # Case 5: If both width and height are provided, return a tuple (scale_x, scale_y)
    if width is not None and height is not None:
        scale_x = width / image_width
        scale_y = height / image_height
        return scale_x, scale_y

    # Case 6: If only scale is provided, return it directly
    if scale is not None:
        return scale

    return 1.0
