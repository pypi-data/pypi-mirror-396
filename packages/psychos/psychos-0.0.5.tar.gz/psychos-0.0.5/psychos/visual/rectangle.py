from typing import Optional, Union, Tuple, TYPE_CHECKING


from pyglet.shapes import Rectangle as PygletRectangle


from ..utils import Color
from .units import Unit, parse_height, parse_width
from .window import get_window

if TYPE_CHECKING:
    from ..visual.window import Window
    from ..types import AnchorHorizontal, AnchorVertical, ColorType, UnitType


def transform_rectangle_anchor(
    x: int, y: int, width: int, height: int, anchor_x: str, anchor_y: str
) -> Tuple[int, int]:
    """
    Transform the anchor of a rectangle to its position. Given an achor, returns the location
    of the top left corner of the rectangle (pyglet's position system).
    """
    position_x = {
        "center": x - width // 2,
        "left": x,
        "right": x - width,
    }
    position_y = {
        "top": y,
        "center": y - height // 2,
        "bottom": y - height,
        "baseline": y - height,
    }
    return int(position_x[anchor_x]), int(position_y[anchor_y])


class Rectangle(PygletRectangle):
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        width: Optional[float] = None,
        height: Optional[float] = None,
        color: "ColorType" = None,
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", "Unit"]] = None,
        anchor_x: "AnchorHorizontal" = "center",
        anchor_y: "AnchorVertical" = "center",
        rotation: float = 0,
        **kwargs,
    ):
        """A rectangle shape that can be drawn on the screen.

        Parameters
        ----------
        position : Tuple[float, float], default=(0, 0)
            The position of the rectangle in the window.
        width : Optional[float], default=None
            The width of the rectangle, in the units of the window or the given coordinates.
        height : Optional[float], default=None
            The height of the rectangle, in the units of the window or the given coordinates.
        color: Optional[ColorType], default=None
            The color of the rectangle.
        window : Optional[Window], default=None
            The window in which the rectangle will be displayed.
        coordinates : Optional[Union[UnitType, Unit]], default=None
            The unit system to be used for positioning the rectangle.
        anchor_x : AnchorHorizontal, default="center"
            The horizontal anchor alignment of the rectangle.
        anchor_y : AnchorVertical, default="center"
            The vertical anchor alignment of the rectangle.
        rotation : float, default=0
            The rotation angle of the rectangle (in degrees 0-360).
        kwargs : dict
            Additional keyword arguments to pass to the Pyglet Rectangle.
        """

        # Retrieve window and set coordinate system
        self.window = window or get_window()
        self._coordinates = None
        self.coordinates = coordinates
        x, y = self.coordinates.transform(*position)

        # Initialize text properties
        width = parse_width(width, window=self.window) or 1
        height = parse_height(height, window=self.window) or 1
        color = Color(color).to_rgba255() or (255, 255, 255, 255)
        self._anchor_system_x = anchor_x
        self._anchor_system_y = anchor_y

        x, y = transform_rectangle_anchor(
            x=x, y=y, width=width, height=height, anchor_x=anchor_x, anchor_y=anchor_y
        )

        super().__init__(x=x, y=y, width=width, height=height, color=color, **kwargs)

        if rotation:
            self.rotation = rotation

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

    @PygletRectangle.color.setter
    def color(self, value: Optional[Union["ColorType", "Color"]]):
        """Set the color of the text."""
        value = Color(value).to_rgba255() or (255, 255, 255, 255)
        super().color = value

    @PygletRectangle.height.setter
    def height(self, value: Optional[Union[str, int, float]]):
        value = parse_height(value, window=self.window)
        super().height = value

    @PygletRectangle.width.setter
    def width(self, value: Optional[Union[str, int, float]]):
        value = parse_width(value, window=self.window)
        super().width = value

    @property
    def position(self) -> Tuple[float, float]:
        """Get the position of the text in pixels."""
        return self.x, self.y

    @position.setter
    def position(self, value: Tuple[float, float]):
        """Set the position of the text."""
        x, y = self.coordinates.transform(*value)
        x, y = transform_rectangle_anchor(
            x=x,
            y=y,
            width=self.width,
            height=self.height,
            anchor_x=self._anchor_system_x,
            anchor_y=self._anchor_system_y,
        )
        self.x = x
        self.y = y

    def draw(self) -> "Rectangle":
        super().draw()
        return self
