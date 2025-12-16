"""psychos.visual.window: Extension of the Pyglet window class with additional functionality."""

from typing import Iterable, Optional, TYPE_CHECKING, Union, Tuple

import pyglet
from pyglet.window import Window as PygletWindow

from .units import Unit, parse_height, parse_width
from ..core.keys import wait_key
from ..core.time import wait
from ..utils import Color

if TYPE_CHECKING:
    from ..types import ColorType, UnitType, Literal, KeyEvent
    from ..core.time import Clock

__all__ = ["Window", "get_window"]


def get_window() -> "Window":
    """
    Retrieve the current default window.

    Returns
    -------
    Window
        The current default window.

    Raises
    ------
    RuntimeError
        If no window has been created yet.
    """
    windows = list(pyglet.app.windows)
    if not windows:
        raise RuntimeError("No window has been created yet.")
    return windows[0]


class Window(PygletWindow):  # pylint: disable=abstract-method
    """
    Custom window for displaying visual elements.

    A subclass of `pyglet.window.Window`, this class provides additional functionality for handling
    units, background color, and event management, while maintaining full compatibility with the
    `pyglet` library. For more information on `pyglet`, refer to the official documentation.

    Parameters
    ----------
    width : Optional[int], default=None
        The width of the window in pixels or another unit type. If None, a default width is used.
    height : Optional[int], default=None
        The height of the window in pixels or another unit type. If None, a default height is used.
    caption : Optional[str], default=None
        The caption or title of the window. If None, no caption is displayed.
    fullscreen : bool, default=False
        Indicates if the window should be displayed in fullscreen mode.
    visible : bool, default=True
        Specifies whether the window is visible upon creation.
    background_color : Optional[ColorType], default=None
        The background color of the window, provided as an RGB/RGBA tuple or a named color string.
        If None, the default color is used.
    mouse_visible : bool, default=False
        Determines if the mouse cursor should be visible within the window.
    units : Union[UnitType, Unit], default="norm"
        The unit system for the window. Can be a string or a Unit object to manage coordinates
        and sizes.
    distance : Optional[float], default=50
        The viewing distance from the screen in centimeters, used for visual angle calculations
        (e.g., degrees).
    inches : Optional[float], default=None
        The diagonal size of the monitor in inches. Required for accurate DPI (dots per inch) and
        physical size calculations.
    clear_after_flip : bool, default=True
        If True, the window will be cleared after flipping the frame buffer, preparing it for the
        next frame.
    kwargs : dict
        Additional keyword arguments to be passed to the Pyglet window constructor.

    Attributes
    ----------
    distance : float
        The viewing distance in centimeters, used for units like degrees of visual angle.
    inches : float
        The diagonal size of the monitor in inches, used for DPI calculations.
    clear_after_flip : bool
        Whether the window is automatically cleared after each frame flip.
    units : Unit
        The current unit system used to convert between different coordinate and size units.

    Examples
    --------
    Basic usage for displaying visual elements:

    .. code-block:: python

        from psychos import Window, Text

        # Create a new window
        window = Window()

        # Create a text stimulus and draw it
        text = Text("Hello, World!").draw()

        # Display the drawn elements on the screen
        window.flip()

        # Keep the window open for 3 seconds
        window.wait(3)

    You can also display other elements like images:

    .. code-block:: python

        from psychos import Window, Image
        from pathlib import Path

        # Create a new window
        window = Window()

        # Load and draw an image
        img_path = Path("image.png")
        image = Image(img_path).draw()

        # Flip the window to display the drawn elements
        window.flip()

        # Keep the window open for 3 seconds
        window.wait(3)
    """

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None,
        fullscreen: bool = False,
        visible: bool = True,
        background_color: Optional["ColorType"] = None,
        mouse_visible: bool = False,
        coordinates: Union["UnitType", "Unit"] = "norm",
        distance: Optional[float] = 50,
        inches: Optional[float] = None,
        clear_after_flip: bool = True,
        screen: Optional[Union["pyglet.canvas.Screen", int]] = None,
        **kwargs,
    ):
        """Creates an instance of the Window class."""

        if isinstance(screen, int):
            display = pyglet.canvas.get_display()
            screen = display.get_screens()[screen]

        super().__init__(
            caption=caption,
            fullscreen=fullscreen,
            visible=visible,
            screen=screen,
            **kwargs,
        )

        self.distance = distance
        self.inches = inches
        self.clear_after_flip = clear_after_flip
        self._coordinates = None
        self._background_color = None
        self._flip_callbacks = []

        if not self.fullscreen and height is not None:
            self.height = height
        if not self.fullscreen and width is not None:
            self.width = width

        self.coordinates = coordinates
        self.background_color = background_color
        self.set_mouse_visible(mouse_visible)
        self.dispatch_events()

    @PygletWindow.width.setter
    def width(self, value: Optional[Union[str, int, float]]) -> None:
        """Set the width of the window."""
        value = parse_width(value, window=self)
        super().width = value

    @PygletWindow.height.setter
    def height(self, value: Optional[Union[str, int, float]]) -> None:
        """Set the height of the window."""
        value = parse_height(value, window=self)
        super().height = value

    @property
    def coordinates(self) -> "Unit":
        """Get the unit system used by the window."""
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value: Union["UnitType", "Unit"]) -> None:
        """Set the unit system used by the window."""
        self._coordinates = Unit.from_name(value, window=self)

    @property
    def background_color(self) -> Optional[Tuple[float, float, float, float]]:
        """Get the background color of the window (r, g, b, a)."""
        return self._background_color

    @background_color.setter
    def background_color(self, color: Optional[Union["ColorType", "Color"]]) -> None:
        """
        Set the background color of the window.

        Parameters
        ----------
        color : Optional[ColorType]
            The background color as a tuple (r, g, b, a) or a color name, or a Color object.
        """
        self._background_color = Color(color).to_rgba()
        if self._background_color is not None:
            pyglet.gl.glClearColor(*self._background_color)

        self.clear()

    @property
    def dpi(self) -> float:
        """
        Get the number of pixels per centimeter in the window, from the monitor's size in inches.

        Returns
        -------
        float
            The number of pixels per centimeter.
        """
        if not self.inches:
            raise ValueError(
                "The diagonal size in inches must be set to calculate DPI. "
                "Specify `inches` to the window constructor."
            )

        # Calculate diagonal resolution in pixels
        diagonal_pixels = (self.screen.width**2 + self.screen.height**2) ** 0.5

        # Calculate pixels per inch (DPI)
        dpi = diagonal_pixels / self.inches

        # Convert DPI to pixels per centimeter
        return dpi

    def on_flip(self, func, *args, **kwargs):
        """
        Register a function to be called after flipping the window's frame buffer.

        This method allows you to register a function to be called after flipping the window's frame
        buffer. The function will be called with the provided arguments and keyword arguments after
        the flip operation is completed.

        If several functions are registered, they will be called in the order they were added.
        """
        self._flip_callbacks.append((func, args, kwargs))

    def flip(self, clear: Optional[bool] = None) -> "Window":
        """
        Flip the window's frame buffer and optionally clear the window after.

        Parameters
        ----------
        clear : Optional[bool], default=None
            Whether to clear the window after flipping. Defaults to the value of
            `self.clear_after_flip`.
        """
        super().flip()

        clear = clear if clear is not None else self.clear_after_flip
        if clear:
            self.clear()

        if self._flip_callbacks:
            for func, args, kwargs in self._flip_callbacks:
                func(*args, **kwargs)
            self._flip_callbacks.clear()

        return self

    def wait(self, duration: float = 1, sleep_interval: float = 0.8, hog_period: float = 0.02):
        """
        Wait for a specified duration while dispatching window events.

        Parameters
        ----------
        duration : float, default=1
            The duration to wait in seconds.
        sleep_interval : float, default=0.8
            The interval to sleep between event dispatches.
        hog_period : float, default=0.02
            The period to hog the CPU at the end of the wait. This is do to
            increase the accuracy of the wait time.
        """
        wait(duration=duration, sleep_interval=sleep_interval, hog_period=hog_period)

    def wait_key(
        self,
        keys: Optional[Union[Iterable[Union[str, int]], str, int]] = None,
        modifiers: Optional[Union[Iterable[Union[str, int]], str, int]] = None,
        clock: Optional["Clock"] = None,
        max_wait: Optional[float] = None,
        event: "Literal['press', 'release']" = "press",
        clear_events: bool = True,
    ) -> "KeyEvent":
        """
        Wait for a specific key event (press or release) within the given time frame.

        This function waits for a key event (either press or release) to occur, and returns the key,
        modifiers, and the timestamp when the event happened. It supports specifying a set of keys
        to listen for, or returning the first key event of any kind if no specific keys are
        provided. The function can also accept a timeout (`max_wait`), after which it will return
        even if no key event occurs.

        If `modifiers` are provided, the function will check if all specified modifiers are pressed
        at the time of the key event. Modifiers can be ignored if `modifiers` is set to `None`, or
        you can enforce that no modifiers are pressed by passing an empty list.

        Parameters
        ----------
        keys : Optional[Union[Iterable[Union[str, int]], str, int]]
            The keys to wait for. It can be one of the following:

            - A string representing the key's name (e.g., "SPACE", "A", etc.).
            - An integer representing the Pyglet key ID (e.g., `pyglet.window.key.SPACE`).
            - An iterable of strings or integers representing multiple keys.

            If no keys are provided (`keys=None`), the function will return on any key press or
            release event.
        modifiers : Optional[Union[Iterable[Union[str, int]], str, int]]
            The modifiers to check for. It can be one of the following:

            - A string representing a modifier name (e.g., "CTRL", "SHIFT").
            - An integer representing the Pyglet modifier bitmask
                (e.g., `pyglet.window.key.MOD_SHIFT`).
            - An iterable of strings or integers representing multiple modifiers.

            If `None`, the function ignores any modifiers. If an empty list is provided, the
            function will only return when no modifiers are pressed.

        clock : Optional["Clock"]
            An optional clock object for measuring time. If not provided, the function will use
            `time.time()` from the standard library. The clock object should have a `.time()` method
            that returns the current time.

        max_wait : Optional[float]
            The maximum amount of time to wait for the key event (in seconds). If this value is not
            provided, the function will wait indefinitely for a key event. If the timeout is reached
            before a key event occurs, the function returns `None` and the current timestamp.

        event : Literal["press", "release"], default "press"
            Specifies whether to wait for a key press event (`"press"`) or a key release
            event (`"release"`).

        clear_events : bool, default True
            Whether to clear any pending events before waiting for the key event. This can be
            useful to avoid processing old events that occurred before calling this function.

        Returns
        -------
        KeyEvent
            A named tuple containing the following:

            - ``key``:
                The pressed or released key, returned as a string (e.g., "SPACE"). If `max_wait`
                is reached without any event, this will be `None`.
            - ``modifiers``:
                A string representation of the modifiers (e.g., "CTRL|SHIFT") pressed at the time
                of the event. If no modifiers were pressed, this will be an empty string.
                If modifiers are ignored (`modifiers=None`), this will also be empty.
            - ``timestamp``:
                The timestamp when the key event occurred, using either the provided clock or
                `time.time()`.
            - ``event``:
                A string representing whether the key event was a "press" or "release".

        Raises
        ------
        AssertionError
            If an invalid event type is passed or if the window is not found.

        Examples
        --------
        Wait for the SPACE key to be pressed or released within 5 seconds:

        >>> key_event = wait_key(keys="SPACE", max_wait=5)
        >>> if key_event.key:
        ...     print(f"Key {key_event.key} pressed with {key_event.modifiers}")
        ... else:
        ...     print(f"No key pressed within 5 seconds, timestamp: {key_event.timestamp}")

        Wait for any key press event:

        >>> key_event = wait_key(max_wait=10)
        >>> print(f"Key {key_event.key} pressed with {key_event.modifiers} ({key_event.timestamp})")
        """
        return wait_key(
            keys=keys,
            modifiers=modifiers,
            clock=clock,
            max_wait=max_wait,
            event=event,
            clear_events=clear_events,
            window=self,
        )
