"""psychos.visual.text: Module with the Text class to display text in a Pyglet window."""

from typing import Optional, Union, Tuple, TYPE_CHECKING

from pyglet.text import Label

from ..utils import Color
from .units import Unit, parse_height, parse_width
from .window import get_window

if TYPE_CHECKING:
    from ..visual.window import Window
    from ..types import AnchorHorizontal, AnchorVertical, ColorType, UnitType


class Text(Label):
    """
    A class to represent text in a Pyglet window using a Label component.

    Parameters
    ----------
    text : str, default=""
        The text to display.
    position : Tuple[float, float], default=(0, 0)
        The position of the text in the window.
    width : Optional[int], default=None
        The width of the text box.
    height : Optional[int], default=None
        The height of the text box.
    color : Optional[ColorType], default=None
        The color of the text.
    anchor_x : AnchorHorizontal, default="center"
        The horizontal anchor alignment of the text.
    anchor_y : AnchorVertical, default="center"
        The vertical anchor alignment of the text.
    window : Optional[Window], default=None
        The window in which the text will be displayed.
    rotation : float, default=0
        The rotation angle of the text.
    multiline : bool, default=False
        Whether the text can span multiple lines.
    font_name : Optional[str], default=None
        The name of the font to use.
    font_size : Optional[float], default=None
        The size of the font to use.
    italic : bool, default=False
        Whether the text is italicized.
    stretch : bool, default=False
        Whether the text is stretched.
    align : AnchorHorizontal, default="center"
        The alignment of the text.
    coordinate_units : Optional[Union[UnitType, Units]], default=None
        The unit system to be used for positioning the text.
    kwargs : dict
        Additional keyword arguments to pass to the Pyglet Label.
    """

    def __init__(
        self,
        text: str = "",
        position: Tuple[float, float] = (0, 0),
        width: Optional[int] = None,
        height: Optional[int] = None,
        color: Optional["ColorType"] = None,
        anchor_x: "AnchorHorizontal" = "center",
        anchor_y: "AnchorVertical" = "center",
        align: "AnchorHorizontal" = "center",
        rotation: float = 0,
        multiline: bool = False,
        font_name: Optional[str] = None,
        font_size: Optional[float] = None,
        italic: bool = False,
        stretch: bool = False,
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", "Unit"]] = None,
        **kwargs,
    ):
        # Retrieve window and set coordinate system
        self.window = window or get_window()
        self._coordinates = None
        self.coordinates = coordinates

        x, y = self.coordinates.transform(*position)

        # Initialize text properties
        width = parse_width(width, window=self.window)
        height = parse_height(height, window=self.window)
        color = Color(color).to_rgba255() or (255, 255, 255, 255)

        super().__init__(
            text=text,
            x=x,
            y=y,
            width=width,
            height=height,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            rotation=rotation,
            multiline=multiline,
            font_name=font_name,
            font_size=font_size,
            italic=italic,
            stretch=stretch,
            align=align,
            color=color,
            **kwargs,
        )

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

    @Label.color.setter
    def color(self, value: Optional[Union["ColorType", "Color"]]):
        """Set the color of the text."""
        value = Color(value).to_rgba255() or (255, 255, 255, 255)
        super().color = value

    @Label.height.setter
    def height(self, value: Optional[Union[str, int, float]]):
        value = parse_height(value, window=self.window)
        super().height = value

    @Label.width.setter
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
        self.x = x
        self.y = y

    def draw(self) -> "Text":
        super().draw()
        return self
