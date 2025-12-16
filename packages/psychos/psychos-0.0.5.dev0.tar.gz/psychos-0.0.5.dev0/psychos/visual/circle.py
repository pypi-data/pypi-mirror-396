from typing import Optional, Union, Tuple, TYPE_CHECKING

from pyglet.shapes import Circle as PygletCircle

from ..utils import Color
from .units import Unit, parse_width
from .window import get_window

if TYPE_CHECKING:
    from ..types import ColorType, UnitType
    from psychos.visual.window import Window

class Circle(PygletCircle):
    """A circle shape that can be drawn on the screen.

    Parameters
    ----------
    position : Tuple[float, float], default=(0, 0)
        The position of the circle in the window.
    radius : Optional[float], default=None
        The radius of the circle, in the units of the window or the given coordinates.
    color : Optional[ColorType], default=None
        The color of the circle.
    window : Optional[Window], default=None
        The window in which the circle will be displayed.
    coordinates : Optional[Union[UnitType, Unit]], default=None
        The unit system to be used for positioning the circle.
    kwargs : dict
        Additional keyword arguments to pass to the Pyglet Circle.
    """
    
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        radius: Optional[float] = None,
        color: Optional["ColorType"] = None,
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", Unit]] = None,
        **kwargs,
    ):
        self.window = window or get_window()
        self._coordinates = None
        self.coordinates = coordinates
        x, y = self.coordinates.transform(*position)

        radius = parse_width(radius, window=self.window) or 1
        rgba = (255, 255, 255, 255) if color is None else Color(color).to_rgba255()
        super().__init__(x, y, radius, color=rgba, **kwargs)
        self._radius = radius

    @property
    def coordinates(self) -> "Unit":
        """Get the coordinate system used for the circle."""
        return self._coordinates
    
    @coordinates.setter
    def coordinates(self, value: Optional[Union["UnitType", Unit]]):
        """Set the coordinate system used for the circle."""
        if value is None:
            self._coordinates = self.window.coordinates
        else:
            self._coordinates = Unit.from_name(value, window=self.window)

    @PygletCircle.color.setter
    def color(self, value: Optional[Union["ColorType", Color]]):
        """Set the color of the circle."""
        rgba = Color(value).to_rgba255() if value else (255, 255, 255, 255)
        PygletCircle.color.__set__(self, rgba[:3])

    @PygletCircle.radius.setter
    def radius(self, value: Optional[Union[str, int, float]]):
        value = parse_width(value, window=self.window)
        PygletCircle.radius.__set__(self, value)
        self._radius = value

    @property
    def position(self) -> Tuple[float, float]:
        """Get the position of the circle in pixels."""
        return self.x, self.y
    
    @position.setter
    def position(self, value: Tuple[float, float]):
        """Set the position of the circle using its coordinate system."""
        x, y = self.coordinates.transform(*value)
        self.x = x
        self.y = y

    def draw(self) -> "Circle":
        """Draw the circle and return itself."""
        super().draw()
        return self