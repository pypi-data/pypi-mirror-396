"""Module for handling key events in Pyglet windows."""

import time

from typing import Iterable, Dict, Literal, List, Optional, Union, TYPE_CHECKING, Callable

from pyglet.window import key
from ..types import InteractState

if TYPE_CHECKING:
    from ..visual.window import Window
    from .time import Clock

from .keys import (
    KEY_NAMES_MAP,
    REVERSE_KEY_MAP,
    MODIFIERS_MAP,
    _id_to_symbol,
    _symbol_to_id,
    _get_modifiers_list,
)


def interact(
    callback: Callable[[InteractState], bool],
    max_wait: Optional[float] = None,
    clock: Optional["Clock"] = None,
    key_event: Literal["press", "release"] = "press",
    clear_events: bool = True,
    window: Optional["Window"] = None,
):
    """
    Wait for a specific key event (press or release) within the given time frame.

    This function waits for a key event (either press or release) to occur, and returns the key,
    modifiers, and the timestamp when the event happened. It supports specifying a set of keys to
    listen for, or returning the first key event of any kind if no specific keys are provided.
    The function can also accept a timeout (`max_wait`), after which it will return even if no key
    was pressed or released.

    If `modifiers` are provided, the function will check if all specified modifiers are
    pressed at the time of the key event. Modifiers can be ignored if `modifiers` is set to `None`,
    or you can enforce that no modifiers are pressed by passing an empty list.

    Parameters
    ----------
    keys : Optional[Union[Iterable[Union[str, int]], str, int]]
        The keys to wait for. It can be one of the following:
        - A string representing the key's name (e.g., "SPACE", "A", etc.)
        - An integer representing the Pyglet key ID (e.g., `pyglet.window.key.SPACE`)
        - An iterable of strings or integers representing multiple keys.
        If no keys are provided (`keys=None`), the function will return on any key press
        or release event.

    modifiers : Optional[Union[Iterable[Union[str, int]], str, int]]
        The modifiers to check for. It can be one of the following:
        - A string representing a modifier name (e.g., "CTRL", "SHIFT")
        - An integer representing the Pyglet modifier bitmask (e.g., `pyglet.window.key.MOD_SHIFT`)
        - An iterable of strings or integers representing multiple modifiers.
        If `None`, the function ignores any modifiers.
        If an empty list is provided, the function will only return when no modifiers are pressed.

    clock : Optional["Clock"]
        An optional clock object for measuring time. If not provided, the function
        will use `time.time()` from the standard library. The clock object should have
        a `.time()` method that returns the current time.

    max_wait : Optional[float]
        The maximum amount of time to wait for the key event (in seconds). If this value
        is not provided, the function will wait indefinitely for a key event. If the timeout is
        reached before a key event occurs, the function returns `None` and the current timestamp.

    event : Literal["press", "release"], default "press"
        Specifies whether to wait for a key press event (`"press"`) or a key
        release event (`"release"`).

    clear_events : bool, default True
        Whether to clear any pending events before waiting for the key event. This can be useful
        to avoid processing old events that occurred before calling this function.

    window : Optional["Window"]
        The Pyglet window instance to capture key events from.
        If no window is provided, the function will attempt to retrieve the current window via
        `get_window()` from the `visual.window` module. If no window is available, an error will be
        raised.

    Returns
    -------
    KeyEvent
        A named tuple containing the following:
        - `key`: The pressed or released key, returned as a string (e.g., "SPACE").
        If `max_wait` is reached without any event, this will be `None`.
        - `modifiers`: A string representation of the modifiers (e.g., "CTRL|SHIFT") pressed at the
        time of the event. If no modifiers were pressed, this will be an empty string. If modifiers
        are ignored (`modifiers=None`), this will also be empty.
        - `timestamp`: The timestamp when the key event occurred, using either the provided clock
        or `time.time()`.
        - `event`: A string representing whether the key event was a "press" or "release".

    Raises
    ------
    AssertionError
        If an invalid event type is passed or if the window is not found.

    Example
    -------
    Wait for the SPACE key to be pressed or released within 5 seconds:

    >>> key_event = wait_key(keys="SPACE", max_wait=5)
    >>> if key_event.key:
    >>>     print(f"Key {key_event.key} pressed with {key_event.modifiers} ({key_event.timestamp})")
    >>> else:
    >>>     print(f"No key pressed within 5 seconds, timestamp: {key_event.timestamp}")

    Wait for any key press event:

    >>> key_event = wait_key(max_wait=10)
    >>> print(f"Key {key_event.key} pressed with {key_event.modifiers} ({key_event.timestamp})")
    """

    start_time = clock.time() if clock else time.time()

    # Get the current window if not provided
    if window is None:
        from ..visual.window import get_window  # pylint: disable=import-outside-toplevel

        window = get_window()

    if clear_events:
        window.dispatch_events()

    # Create a key state handler and push the event handler to the window
    key_handler = key.KeyStateHandler()
    window.push_handlers(key_handler)

    pressed_key, pressed_modifiers = None, None
    mouse_x, mouse_y = None, None
    mouse_button = None

    on_key_event = f"on_key_{key_event}"

    @window.event(on_key_event)
    def check_key(symbol, mod_state):
        nonlocal pressed_key, pressed_modifiers
        pressed_key = _id_to_symbol(symbol)
        pressed_modifiers = _get_modifiers_list(mod_state)

    # --- Mouse motion handler ---
    @window.event
    def on_mouse_motion(x, y, dx, dy):
        nonlocal mouse_x, mouse_y
        mouse_x, mouse_y = x, y

    # --- Mouse press handler ---
    @window.event
    def on_mouse_press(x, y, button, mod_state):
        nonlocal mouse_button, mouse_x, mouse_y
        mouse_button = button  # e.g., pyglet.window.mouse.LEFT / RIGHT
        mouse_x, mouse_y = x, y

    # Add a mouse release
    @window.event
    def on_mouse_release(x, y, button, mod_state):
        nonlocal mouse_button, mouse_x, mouse_y
        mouse_button = None  # Reset on release
        mouse_x, mouse_y = x, y

    @window.event
    def on_mouse_drag(x, y, dx, dy, button, mod_state):
        nonlocal mouse_x, mouse_y
        mouse_x, mouse_y = x, y

    # Optimized main loop to wait for key press or max wait timeout
    end_time = start_time + max_wait if max_wait is not None else float("inf")

    timestamp = clock.time() if clock else time.time()
    while timestamp <= end_time:
        interact_state = InteractState(
            pressed_key=pressed_key,
            pressed_modifiers=pressed_modifiers,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            mouse_button=mouse_button,
            timestamp=timestamp,
            elapsed_time=timestamp - start_time,
        )

        window.dispatch_events()
        timestamp = clock.time() if clock else time.time()
        should_continue = callback(interact_state)
        if not should_continue:
            break

    # Remove the event handler and pop the key handler
    window.remove_handlers(**{on_key_event: check_key})
    window.remove_handlers(on_mouse_motion)
    window.remove_handlers(on_mouse_press)
    window.remove_handlers(on_mouse_release)
    window.remove_handlers(on_mouse_drag)
    window.pop_handlers()

    return interact_state # Return the final interact state
