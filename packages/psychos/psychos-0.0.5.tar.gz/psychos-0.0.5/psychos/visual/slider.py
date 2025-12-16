"""psychos.visual.slider: Module with the Slider class to display an slider in a Pyglet window."""

from typing import NamedTuple, Optional, Tuple, Union, Literal, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual.window import Window
    from ..types import ColorType, UnitType

from .window import get_window
from .units import Unit, parse_height, parse_width
from ..utils import Color
from ..core.time import Clock, _time
from ..core.interact import interact
from ..types import InteractState
from .rectangle import Rectangle, transform_rectangle_anchor
from .circle import Circle
from .text import Text

__all__ = ["Slider", "SliderState", "InteractState"]

CircleState = Literal["default", "hover", "grab"]


class SliderState(NamedTuple):
    value: float
    elapsed_time: float
    timestamp: float
    has_been_updated: bool
    slider_state: CircleState


class Slider:
    """
    Interactive slider widget for Pyglet windows.

    The :class:`Slider` provides a horizontal bar that allows users to select
    a continuous value using the mouse. It supports hover and grab states with
    customizable appearance and can be easily integrated into interactive or
    behavioral experiments.

    Parameters
    ----------
    initial_value : float, optional
        Initial slider value. Defaults to the midpoint of `interval`.
    interval : tuple of float, default=(0.0, 100.0)
        Minimum and maximum numeric values of the slider.
    position : tuple of float, default=(0, 0)
        Center position of the slider in the given coordinate system.
    width : str or float, default="50vw"
        Total width of the slider line (supports relative units, e.g., "vw").
    height : str or float, default="4vh"
        Height of the slider area.
    color : ColorType, optional
        Base color of the slider (RGBA or named color).
    line_width : str or float, default="2px"
        Thickness of the main slider line.
    tick_width : str or float, default="1px"
        Width of each tick mark line.
    ticks : int or tuple of float, optional
        If int, number of evenly spaced tick marks.
        If tuple, explicit numeric tick values along the interval.
    tick_labels : tuple of str, optional
        Optional text labels for each tick. Must match the number of ticks.
    tick_size : str or float, default=10
        Length of each tick mark (in pixels or relative units).
    tick_padding : str or float, optional
        Distance between the slider line and the tick labels, if provided.
    circle_radius : str or float, default="5px"
        Radius of the draggable circle indicating the current value.
    circle_hover_increase : float, default=1.5
        Multiplicative factor for the circle radius when hovered.
    circle_grab_increase : float, default=1.5
        Multiplicative factor for the circle radius when grabbed.
    action_radius : str or float, default="10px"
        Radius around the circle where hover or grab interactions are triggered.
    action_vertical_radius : str or float, default="20px"
        Vertical tolerance around the slider line for click-and-drag actions.
    circle_hover_color : ColorType, optional
        Color of the circle when hovered. Defaults to `color`.
    circle_grab_color : ColorType, optional
        Color of the circle when grabbed. Defaults to `circle_hover_color`.
    window : Window, optional
        Target window where the slider is drawn. If not provided, uses
        the current active window.
    coordinates : Unit or str, optional
        Coordinate system for positioning (e.g., "px", "norm", "vw", "vh").

    Example
    -------
    A minimal example showing a white slider and real-time value update:

    >>> from psychos.visual import Window, Text, Slider
    >>>
    >>> window = Window(background_color="gray", mouse_visible=True)
    >>> text = Text("", position=(0, 0.3))
    >>> slider = Slider(color="white", circle_grab_color="red", ticks=4)
    >>>
    >>> def callback(slider_state, _):
    ...     text.text = f"Value: {slider_state.value:.2f}"
    ...     text.draw()
    ...     return False  # continue interaction
    >>>
    >>> state = slider.wait_response(callback=callback, exit_key="SPACE")
    >>> print("Final value:", state.value)
    """

    def __init__(
        self,
        initial_value: Optional[float] = None,
        interval: Tuple[float, float] = (0.0, 100),
        position: Tuple[float, float] = (0, 0),
        width: Union[str, int, float] = "50vw",
        height: Union[str, int, float] = "4vh",
        color: "ColorType" = None,
        line_width: Union[str, int, float] = "2px",
        tick_width: Union[str, int, float] = "1px",
        ticks: Optional[Union[Tuple[float, ...], int]] = None,
        tick_labels: Optional[Tuple[str, ...]] = None,
        tick_size: Union[str, int, float] = 10,
        tick_padding: Optional[Union[str, int, float]] = None,
        circle_radius: Union[str, int, float] = "5px",
        circle_hover_increase: float = 1.5,
        circle_grab_increase: float = 1.5,
        action_radius: Union[str, int, float] = "10px",
        action_vertical_radius: Union[str, int, float] = "20px",
        circle_hover_color: "ColorType" = None,
        circle_grab_color: "ColorType" = None,
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", "Unit"]] = None,
    ):

        # Retrieve window and set coordinate system
        self.window = window or get_window()
        self._coordinates = None
        self.coordinates = coordinates
        x, y = self.coordinates.transform(*position)

        # check interval validity
        if interval[0] >= interval[1]:
            raise ValueError("Slider interval is invalid: min must be less than max.")
        if initial_value is None:
            initial_value = (interval[0] + interval[1]) / 2

        # Initialize text properties
        width = parse_width(width, window=self.window) or 1
        height = parse_height(height, window=self.window) or 1
        color = Color(color).to_rgba255() or (255, 255, 255, 255)

        x, y = transform_rectangle_anchor(
            x=x, y=y, width=width, height=height, anchor_x="center", anchor_y="center"
        )
        self._initial_value = initial_value
        self._interval = interval
        self._value = initial_value
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._line_height = parse_height(line_width, window=self.window) or 1
        self._tick_width = parse_width(tick_width, window=self.window) or 1
        self._ticks_values = ticks or ()
        self._tick_labels = tick_labels or ()
        self._tick_size = tick_size
        self._tick_padding = parse_height(tick_padding, window=self.window) or self._height
        self._color = color
        self._components = {}
        self._circle_radius = parse_height(circle_radius, window=self.window) or 1
        self._circle_hover_radius = int(circle_hover_increase * self._circle_radius)
        self._circle_grab_radius = int(circle_grab_increase * self._circle_radius)
        self._action_radius = (
            parse_height(action_radius, window=self.window) or self._circle_hover_radius
        )
        self._action_vertical_radius = (
            parse_height(action_vertical_radius, window=self.window) or self._circle_hover_radius
        )

        circle_hover_color = Color(circle_hover_color).to_rgba255() if circle_hover_color else color
        self._circle_hover_color = circle_hover_color

        circle_grab_color = (
            Color(circle_grab_color).to_rgba255() if circle_grab_color else circle_hover_color
        )
        self._circle_grab_color = circle_grab_color

        self._state: CircleState = "default"  # could be "default", "hover", "grab"
        self._has_been_updated = False
        self._initialize_components()

    def _initialize_components(self):
        """Initialize the slider subcomponents: line, ticks, and circle."""
        self._components["mid_line"] = Rectangle(
            position=(self._x, self._y),
            width=self._width,
            height=self._line_height,
            color=self._color,
            window=self.window,
            coordinates="px",
            anchor_x="left",
            anchor_y="center",
        )

        self.tick_marks = []
        tick = self._initialize_tick(self._x, self._line_height)
        self.tick_marks.append(tick)

        self.tick_labels = []

        # Initialize the rest of ticks if provided
        if isinstance(self._ticks_values, int):  # Evenly spaced ticks
            n_ticks = self._ticks_values
            min_val, max_val = self._interval
            step = (max_val - min_val) / (n_ticks + 1)
            self._ticks_values = tuple(min_val + step * (i + 1) for i in range(n_ticks))

        for tick_value in self._ticks_values:
            x = self._map_value_to_position(tick_value)
            tick = self._initialize_tick(x, self._tick_width)
            self.tick_marks.append(tick)

        tick = self._initialize_tick(self._x + self._width, self._line_height)
        self.tick_marks.append(tick)

        # Now initialize tick labels if provided
        if self._tick_labels:
            assert len(self._tick_labels) == len(self.tick_marks), (
                "Number of tick labels must match number of tick marks."
                f" Got {len(self._tick_labels)} labels and {len(self.tick_marks)} ticks."
            )

            for label_text, tick in zip(self._tick_labels, self.tick_marks):
                label = Text(
                    text=str(label_text),
                    position=(tick.x, tick.y - self._tick_padding),
                    font_size=self._tick_size,
                    color=self._color,
                    window=self.window,
                    coordinates="px",
                    anchor_x="center",
                    anchor_y="top",
                )
                self.tick_labels.append(label)

        # Now the circle representing the current value
        x = self._map_value_to_position(self._initial_value)
        self._components["circle"] = Circle(
            position=(x + self._circle_radius / 2, self._y),
            radius=self._circle_radius,
            color=self._color,
            window=self.window,
            coordinates="px",
        )

    def _map_value_to_position(self, value: float) -> float:
        """Map a value in the interval to a position on the slider."""
        min_val, max_val = self._interval
        proportion = (value - min_val) / (max_val - min_val)
        position = self._x + proportion * self._width
        return position

    def _initialize_tick(self, x: float, line_height: float) -> Rectangle:
        """Initialize a tick mark at position x."""
        tick = Rectangle(
            position=(x, self._y + self._height / 2),
            width=self._height,
            height=line_height,
            color=self._color,
            window=self.window,
            coordinates="px",
            anchor_x="left",
            anchor_y="center",
            rotation=90,
        )
        return tick

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

    @property
    def color(self) -> Tuple[int, int, int, int]:
        """Get the color of the text."""
        return self._color

    @color.setter
    def color(self, value: Optional[Union["ColorType", "Color"]]):
        """Set the color of the text."""
        value = Color(value).to_rgba255() or (255, 255, 255, 255)
        self._color = value

        self._components["mid_line"].color = value
        for tick in self.tick_marks:
            tick.color = value

        # Then update circle color based on state
        self._update_circle()

    @property
    def height(self) -> float:
        """Get the height of the slider."""
        return self._height

    @height.setter
    def height(self, value: Optional[Union[str, int, float]]):
        value = parse_height(value, window=self.window)
        self._height = value

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: Optional[Union[str, int, float]]):
        value = parse_width(value, window=self.window)
        self._width = value

    @property
    def position(self) -> Tuple[float, float]:
        """Get the position of the text in pixels."""
        return self._x, self._y

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
        self._x = x
        self._y = y

    def _update_circle(self):
        """Update the circle appearance based on the current state."""
        if self._state == "hover":
            self._components["circle"].radius = self._circle_hover_radius
            self._components["circle"].color = self._circle_hover_color
        elif self._state == "grab":
            self._components["circle"].radius = self._circle_grab_radius
            self._components["circle"].color = self._circle_grab_color
        else:
            self._components["circle"].radius = self._circle_radius
            self._components["circle"].color = self._color

    def draw(self) -> "Slider":
        """Draw the slider on the window."""
        self._components["mid_line"].draw()
        for tick in self.tick_marks:
            tick.draw()

        for label in self.tick_labels:
            label.draw()

        self._update_circle()
        self._components["circle"].draw()

        return self

    def _update_value_from_mouse(self, x: float, y: float, button_pressed: bool) -> None:
        """Update the slider value when dragging or clicking near the line."""

        if x is None or y is None:
            self._state = "default"
            return

        circle = self._components["circle"]
        circle_x, circle_y = circle.position

        dist_sq = (x - circle_x) ** 2 + (y - circle_y) ** 2
        in_action_area = dist_sq <= self._action_radius**2

        in_vertical_area = (self._y - self._action_vertical_radius) <= y <= (
            self._y + self._action_vertical_radius
        ) and self._x <= x <= (self._x + self._width)

        update_value = False

        # --- State logic ---
        if not button_pressed:
            self._state = "hover" if in_action_area else "default"

        elif button_pressed:
            if self._state != "grab" and (in_action_area or in_vertical_area):
                self._state = "grab"

            if self._state == "grab":
                update_value = True

        # --- Update position and value ---
        if update_value:
            new_x = min(max(x, self._x), self._x + self._width)
            circle.position = (new_x, circle_y)

            min_val, max_val = self._interval
            proportion = (new_x - self._x) / self._width
            self._value = min_val + proportion * (max_val - min_val)
            self._has_been_updated = True

    @property
    def value(self) -> float:
        """Get the current value of the slider."""
        return self._value

    @value.setter
    def value(self, value: float):
        """Set the current value of the slider."""
        if not (self._interval[0] <= value <= self._interval[1]):
            raise ValueError(
                "Value must be within the slider interval" f" {self._interval}, got {value}."
            )
        self._value = value
        # Update circle position accordingly
        x = self._map_value_to_position(value)
        circle = self._components["circle"]
        circle.position = (x + self._circle_radius / 2, circle.y)

    @property
    def initial_value(self) -> float:
        """Get the initial value of the slider."""
        return self._initial_value

    @initial_value.setter
    def initial_value(self, value: float):
        """Set the initial value of the slider."""
        if not (self._interval[0] <= value <= self._interval[1]):
            raise ValueError(
                "Initial value must be within the slider interval"
                f" {self._interval}, got {value}."
            )
        self._initial_value = value

    def wait_response(
        self,
        callback: Optional[Callable] = None,
        max_wait: Optional[float] = None,
        exit_key: Union[str, Tuple[str, ...]] = (),
        clock: Optional["Clock"] = None,
    ) -> float:
        """
        Wait for user interaction with the slider and return the final state.

        This method continuously updates and redraws the slider in real time while
        monitoring mouse movement, button presses, and keyboard input. It can optionally
        call a user-provided `callback` function every frame to handle custom logic
        (e.g., updating text, plotting feedback, or conditional stopping).

        The loop terminates when:

        - The user presses any of the specified `exit_key` keys, or
        - The callback function returns ``True``, or
        - The optional time limit (`max_wait`) is reached.

        Parameters
        ----------
        callback : callable, optional
            A function called every frame during interaction,
            ``callback(slider_state, window_state)``. It should accept two arguments:

            - `slider_state` (:class:`SliderState`) contains the current slider value,
                elapsed time, timestamp, and interaction state.
            - `window_state` (:class:`InteractState`) contains the current mouse position,
                pressed keys, and other window-level events.

            The callback must return:

            - ``True`` to stop the interaction early.
            - ``False`` to continue waiting.

        max_wait : float, optional
            Maximum waiting time in seconds. If not provided, waits indefinitely.
        exit_key : str or tuple of str, default="ESCAPE"
            Key(s) that immediately terminate the interaction when pressed.
        clock : Clock, optional
            Clock object providing precise timing. If not given, uses the default internal clock.

        Returns
        -------
        SliderState
            A named tuple with the final slider state, containing:

            - ``value`` : float — final slider value.
            - ``elapsed_time`` : float — total interaction duration.
            - ``timestamp`` : float — time when the interaction ended.
            - ``slider_state`` : {"default", "hover", "grab"} — final circle state.
            - ``has_been_updated`` : bool — whether the slider value was changed.

        """
        self._has_been_updated = False
        exit_keys = (exit_key,) if isinstance(exit_key, str) else exit_key
        start_time = clock.time() if clock else _time()
        self._value = self._initial_value

        def slider_callback(state: "InteractState") -> bool:
            current_time = clock.time() if clock else _time()
            elapsed_time = current_time - start_time
            self._update_value_from_mouse(
                x=state.mouse_x, y=state.mouse_y, button_pressed=bool(state.mouse_button)
            )
            self.draw()
            if callback:
                slider_state = SliderState(
                    value=self._value,
                    slider_state=self._state,
                    elapsed_time=elapsed_time,
                    timestamp=current_time,
                    has_been_updated=self._has_been_updated,
                )
                callback_res = callback(slider_state, state)
            self.window.flip()

            # True to continue waiting, False to stop
            if state.pressed_key in exit_keys:
                return False

            return not callback_res

        interact(callback=slider_callback, max_wait=max_wait, window=self.window)

        # Return the final value
        slider_state = SliderState(
            value=self._value,
            elapsed_time=(clock.time() if clock else _time()) - start_time,
            timestamp=(clock.time() if clock else _time()),
            slider_state=self._state,
            has_been_updated=self._has_been_updated,
        )

        return slider_state
