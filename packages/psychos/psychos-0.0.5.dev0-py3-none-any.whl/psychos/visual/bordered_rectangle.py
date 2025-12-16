from typing import Optional, Union, Tuple, TYPE_CHECKING


from pyglet.shapes import BorderedRectangle as PygletBorderedRectangle


from ..utils import Color
from .units import Unit, parse_height, parse_width
from .window import get_window
from .rectangle import transform_rectangle_anchor

if TYPE_CHECKING:
    from ..visual.window import Window
    from ..types import AnchorHorizontal, AnchorVertical, ColorType, UnitType


class BorderedRectangle(PygletBorderedRectangle):
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        width: Optional[float] = None,
        height: Optional[float] = None,
        border: Optional[float] = None,
        color: Optional["ColorType"] = None,
        border_color: Optional["ColorType"] = None,
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
        border : float, default=1.0
            The width of the border of the rectangle.
        color: Optional[ColorType], default=None
            The color of the rectangle.
        border_color: Optional[ColorType], default=None
            The color of the border of the rectangle.
        window : Optional[Window], default=None
            The window in which the rectangle will be displayed.
        coordinates : Optional[Union[UnitType, Unit]], default=None
            The unit system to be used for positioning the rectangle.
        anchor_x : AnchorHorizontal, default="center"
            The horizontal anchor alignment of the rectangle.
        anchor_y : AnchorVertical, default="center"
            The vertical anchor alignment of the rectangle.
        rotation : float, default=0
            The rotation angle of the rectangle (in degrees from 0-360).
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
        border = parse_width(border, window=self.window) or 1
        color = Color(color).to_rgba255() or (255, 255, 255, 255)
        border_color = Color(border_color).to_rgba255() or (100, 100, 100)
        self._anchor_system_x = anchor_x
        self._anchor_system_y = anchor_y

        x, y = transform_rectangle_anchor(
            x=x,
            y=y,
            width=width,
            height=height,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
        )

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            border=border,
            color=color,
            border_color=border_color,
            **kwargs,
        )
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

    @PygletBorderedRectangle.color.setter
    def color(self, value: Optional[Union["ColorType", "Color"]]):
        """Set the color of the text."""
        value = Color(value).to_rgba255() or (255, 255, 255, 255)
        super().color = value

    @PygletBorderedRectangle.height.setter
    def height(self, value: Optional[Union[str, int, float]]):
        value = parse_height(value, window=self.window)
        super().height = value

    @PygletBorderedRectangle.border.setter
    def border(self, value: Optional[Union[str, int, float]]):
        value = parse_width(value, window=self.window)
        super().border = value

    @PygletBorderedRectangle.border_color.setter
    def border_color(self, value: Optional[Union["ColorType", "Color"]]):
        """Set the color of the text."""
        value = Color(value).to_rgba255() or (255, 255, 255, 255)
        super().border_color = value

    @PygletBorderedRectangle.width.setter
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

    def draw(self) -> "BorderedRectangle":
        super().draw()
        return self
