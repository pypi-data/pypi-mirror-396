"""Module for handling key events in Pyglet windows."""

import time

from typing import Iterable, Dict, Literal, List, Optional, Union, TYPE_CHECKING

from pyglet.window import key
from ..types import KeyEvent

if TYPE_CHECKING:
    from ..visual.window import Window
    from .time import Clock


__all__ = ["wait_key", "list_keys", "list_modifiers"]

# Key names
KEY_NAMES_MAP = key._key_names.copy()  # pylint: disable=protected-access
REVERSE_KEY_MAP = {v: k for k, v in KEY_NAMES_MAP.items()}
REVERSE_KEY_MAP.update({k[1:]: v for k, v in REVERSE_KEY_MAP.items() if k.startswith("_")})

MODIFIERS_MAP = {
    "SHIFT": key.MOD_SHIFT,
    "CTRL": key.MOD_CTRL,
    "ALT": key.MOD_ALT,
    "CAPSLOCK": key.MOD_CAPSLOCK,
    "NUMLOCK": key.MOD_NUMLOCK,
    "WINDOWS": key.MOD_WINDOWS,
    "COMMAND": key.MOD_COMMAND,
    "OPTION": key.MOD_OPTION,
    "SCROLLLOCK": key.MOD_SCROLLLOCK,
    "FUNCTION": key.MOD_FUNCTION,
}
REVERSE_MODIFIERS_MAP = {v: k for k, v in MODIFIERS_MAP.items()}


def list_keys() -> List[str]:
    """
    List all available key names.

    Returns
    -------
    Iterable[str]
        A list of all available key names.
    """
    return list(KEY_NAMES_MAP.keys())


def list_modifiers() -> List[str]:
    """
    List all available modifier names.

    Returns
    -------
    Iterable[str]
        A list of all available modifier names.
    """
    return list(MODIFIERS_MAP.keys())


def wait_key(
    keys: Optional[Union[Iterable[Union[str, int]], str, int]] = None,
    modifiers: Optional[Union[Iterable[Union[str, int]], str, int]] = None,
    clock: Optional["Clock"] = None,
    max_wait: Optional[float] = None,
    event: Literal["press", "release"] = "press",
    clear_events: bool = True,
    window: Optional["Window"] = None,
) -> KeyEvent:
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

    # Convert `keys` input to a set of valid key symbols (uppercased if it's a string)
    keys = (
        {_symbol_to_id(keys)}
        if isinstance(keys, (str, int))
        else {_symbol_to_id(k) for k in keys} if keys else None
    )

    # Convert `modifiers` input to a set of valid modifier bitmasks
    modifiers_mask = sum({_symbol_to_id(modifiers, MODIFIERS_MAP)}) if modifiers else None

    # Create a key state handler and push the event handler to the window
    key_handler = key.KeyStateHandler()
    window.push_handlers(key_handler)

    key_pressed = False
    pressed_key, pressed_modifiers = None, None
    on_key_event = f"on_key_{event}"

    # Key press event handler
    @window.event(on_key_event)
    def check_key(symbol, mod_state):
        nonlocal key_pressed, pressed_key, pressed_modifiers
        if symbol is not None and (keys is None or symbol in keys):
            if modifiers is None or (
                modifiers_mask is not None and mod_state & modifiers_mask == modifiers_mask
            ):
                key_pressed = True
                pressed_key = _id_to_symbol(symbol)
                pressed_modifiers = _get_modifiers_list(mod_state)

    # Optimized main loop to wait for key press or max wait timeout
    end_time = start_time + max_wait if max_wait is not None else float("inf")
    
    timestamp = clock.time() if clock else time.time()
    while not key_pressed and timestamp <= end_time:
        window.dispatch_events()
        timestamp = clock.time() if clock else time.time()
        

    # # Capture the timestamp at the moment the key is pressed or when the wait ends
    # timestamp = clock.time() if clock else time.time()

    # Remove the event handler and pop the key handler
    window.remove_handlers(**{on_key_event: check_key})
    window.pop_handlers()

    return KeyEvent(key=pressed_key, modifiers=pressed_modifiers, timestamp=timestamp, event=event)


def _symbol_to_id(symbol: Union[str, int], mapping: Optional[Dict[str, int]] = None) -> int:
    """Convert a key or modifier symbol to its Pyglet ID."""
    mapping = mapping or REVERSE_KEY_MAP
    return mapping.get(symbol.upper(), -1) if isinstance(symbol, str) else symbol


def _id_to_symbol(identifier: int, mapping: Optional[Dict[int, str]] = None) -> str:
    """Convert a Pyglet key ID to its string representation."""
    mapping = mapping or KEY_NAMES_MAP
    symbol = mapping.get(identifier, f"UNKNOWN_{identifier}")
    return symbol[1:] if symbol.startswith("_") else symbol


def _get_modifiers_list(mod_state: int) -> List[str]:
    """Convert modifier bitmask to a list of human-readable modifier names."""
    if mod_state == 0:
        return None
    return "|".join(
        [REVERSE_MODIFIERS_MAP[mod] for mod in REVERSE_MODIFIERS_MAP if mod_state & mod]
    )
