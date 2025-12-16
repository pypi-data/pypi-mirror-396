"""psychos.core.time: Module with classes and functions for time management."""

import warnings
from datetime import datetime
from time import sleep, perf_counter as _time
from typing import Literal, Optional, Union, Callable

import pyglet

__all__ = ["wait", "Clock", "Interval"]


def _dispatch_events():
    """Dispatch events for all windows in the application.
    This ensures responsiveness during waiting."""
    for window in pyglet.app.windows:
        window.dispatch_pending_events()


def wait(duration: float, sleep_interval: float = 0.8, hog_period: float = 0.02):
    """
    Wait for a specified duration while keeping the application responsive by processing events.

    Parameters
    ----------
    duration : float
        The total time to wait in seconds.
    sleep_interval : float, default=0.8
        The time interval between event dispatching in seconds. This controls how often
        we dispatch events while waiting. Smaller values provide more responsiveness
        but increase CPU usage.
    hog_period : float, default=0.02
        The duration at the end of the wait period during which the function
        continuously checks the time without sleeping to ensure accurate timing.
    """
    start_time = _time()
    end_time = start_time + duration
    end_time_slow = end_time - hog_period

    # Loop until the wait time has passed
    while _time() < end_time_slow:
        # Calculate the remaining time
        remaining_time = min(end_time_slow - _time(), sleep_interval)

        # Sleep for the smaller of the remaining time or the sleep_interval
        if remaining_time > 0:
            sleep(remaining_time)
            
        # After sleeping, dispatch events to ensure responsiveness
        _dispatch_events()

    # Hog the CPU for the remaining time to ensure accurate timing
    if hog_period > 0:
        while _time() < end_time:
            pass


class Clock:
    """
    A class to represent a simple clock that tracks elapsed time.

    The `Clock` class allows for tracking time intervals, with options to format the output as raw
    seconds, a formatted string using `strftime`, or a custom callable to process the elapsed time.

    Parameters
    ----------
    start_time : Optional[float], default=None
        The initial time from which the clock starts counting. If None, the current time is used.
    fmt : Optional[Union[Callable, str]], default=None
        Defines how the elapsed time is returned:
        - If None, returns the elapsed time as a float in seconds.
        - If a string, the elapsed time is returned formatted according to `datetime.strftime`.
        - If a callable, the callable is applied to the elapsed time, and its result is returned.

    Examples
    --------
    Basic usage with no formatting:

    >>> clock = Clock()  # Starts the clock with the current time
    >>> elapsed = clock.time()  # Returns the elapsed time in seconds as a float
    >>> clock.reset()  # Resets the clock's start time to the current time

    Using a formatted string to represent elapsed time:

    >>> clock_fmt = Clock(fmt="%H:%M:%S")  # Format elapsed time as hours, minutes, and seconds
    >>> formatted_time = clock_fmt.time()  # Returns the elapsed time as a formatted string

    Using a custom callable to format elapsed time:

    >>> clock_callable = Clock(fmt=lambda x: f"{int(x)} seconds have passed.")
    >>> custom_time = clock_callable.time()  # Returns elapsed time processed by the callable

    """

    def __init__(
        self,
        start_time: Optional[float] = None,
        fmt: Optional[Union[Callable, str]] = None,
    ):
        """
        Initialize the Clock.

        Parameters
        ----------
        start_time : float, optional
            The time from which the clock starts counting. If None, it takes the current time.
        fmt : Union[Callable, str, None]
            The format of the output. If None, the result will be the elapsed time in seconds.
            If a string, it will be formatted using `datetime.strftime`.
            If a callable, the callable will process the elapsed time.

        Example usage
        -------------
        >>> clock = Clock()  # Starts clock with current time
        >>> clock.time()  # Returns elapsed time in seconds
        >>> clock.reset()  # Resets the clock's start time to now
        >>> clock_fmt = Clock(fmt="%H:%M:%S")
        >>> clock_fmt.time()  # Returns elapsed time formatted as HH:MM:SS
        """

        self.start_time = start_time if start_time is not None else _time()
        self.fmt = fmt

    def time(self) -> Union[float, str]:
        """
        Returns the elapsed time since the clock was started or last reset.

        Returns
        -------
        Union[float, str]
            - If `fmt` is None, returns the time as a float representing seconds.
            - If `fmt` is a string, returns the time formatted according to `strftime` conventions.
            - If `fmt` is a callable, applies the callable to the elapsed time.

        Raises
        ------
        TypeError
            If `fmt` is not None, a string, or a callable.

        Examples
        --------
        >>> clock = Clock()
        >>> clock.time()  # Returns elapsed time in seconds as a float

        >>> clock_fmt = Clock(fmt="%H:%M:%S")
        >>> clock_fmt.time()  # Returns elapsed time formatted as a string (HH:MM:SS)
        """
        elapsed_time = _time() - self.start_time
        if self.fmt is None:
            return elapsed_time
        if isinstance(self.fmt, str):
            current_time = datetime.fromtimestamp(self.start_time + elapsed_time)
            return current_time.strftime(self.fmt)
        if callable(self.fmt):
            return self.fmt(elapsed_time)
        if self.fmt is None:
            return elapsed_time

        raise TypeError(
            "Invalid type for 'fmt'. Must be None, a string, or a callable."
        )

    def reset(self):
        """
        Resets the start time to the current time.

        Example
        -------
        >>> clock = Clock()
        >>> clock.reset()  # Resets the starting point of the clock
        """
        self.start_time = _time()


class Interval:
    """
    A class to handle time intervals, including support for context management
    to ensure precise timing and handling of remaining time.

    Parameters
    ----------
    duration : float
        The duration of the interval in seconds.
    on_overtime : Literal["ignore", "warning", "exception"], default="warning"
        Specifies what to do if the elapsed time exceeds the duration:
        - "ignore": Do nothing.
        - "warning": Raise a warning if the interval is exceeded.
        - "exception": Raise an exception if the interval is exceeded.
    sleep_interval : float, default=0.8
        The sleep interval for how long the function sleeps in the wait period.
        This controls the frequency of event dispatching.
    hog_period : float, default=0.02
        The hog period is the duration in the final part of the wait
        where continuous checking is done for more precise timing.
    start_time : Optional[float], default=None
        If provided, the interval will use this as the start time, otherwise it will
        default to the current time using `time()`.

    Example usage
    -------------
    >>> # Basic usage with a 5-second interval
    >>> interval = Interval(5)
    >>> # Do some work ...
    >>> interval.wait()  # Wait for the remaining time of the interval

    >>> interval.reset()  # Reset the interval to restart the timing
    >>> # Do some more work ...
    >>> interval.wait()  # Wait for the remaining time to reach 5 seconds

    >>> # Using the class in a context manager to ensure timing
    >>> with Interval(5):
    >>>     time.sleep(3)
    >>> # Exiting the 'with' block will automatically wait for the remaining time
    """

    def __init__(
        self,
        duration: float,
        on_overtime: Literal["ignore", "warning", "exception"] = "warning",
        sleep_interval: float = 0.8,
        hog_period: float = 0.02,
        start_time: Optional[float] = None,
    ):
        self.duration = duration
        if on_overtime not in ["ignore", "warning", "exception"]:
            raise ValueError(
                "Invalid value for 'on_overtime'. Must be 'ignore', 'warning', or 'exception'."
            )
        self.on_overtime = on_overtime
        self.start_time = (
            start_time if start_time is not None else _time()
        )  # Set start time
        self.sleep_interval = sleep_interval
        self.hog_period = hog_period
        self.elapsed_time = None

    def reset(self) -> None:
        """Reset the start time to the current timestamp."""
        self.start_time = _time()

    def wait(self) -> None:
        """
        Wait for the remaining time of the interval. If the interval has already passed,
        handle it based on the `on_overtime` parameter.

        Raises
        ------
        RuntimeError:
            If `on_overtime` is set to "exception" and the interval has already passed.
        Warning:
            If `on_overtime` is set to "warning" and the interval has already passed.
        """
        # Calculate the elapsed time and remaining time

        self.elapsed_time = _time() - self.start_time
        remaining_time = self.duration - self.elapsed_time

        if remaining_time > 0:
            wait(
                duration=remaining_time,
                sleep_interval=self.sleep_interval,
                hog_period=self.hog_period,
            )  # Wait for the remaining time
        else:
            message = (
                f"The interval of {self.duration} seconds was exceeded"
                f"by {-remaining_time:.2f} seconds."
            )

            if self.on_overtime == "exception":
                raise RuntimeError(message)
            if self.on_overtime == "warning":
                warnings.warn(message, RuntimeWarning)
            # If "ignore", do nothing

    def remaining(self) -> float:
        """
        Get the remaining time of the interval.

        Returns
        -------
        float
            The remaining time in seconds.
        """
        return self.duration - (_time() - self.start_time)

    def __enter__(self) -> "Interval":
        """Reset the start time when entering the `with` block."""
        self.reset()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """End the interval and wait for the remaining time when exiting the `with` block."""
        self.wait()

    # --- Arithmetic Methods with Numbers Only ---

    def __add__(self, other: float) -> "Interval":
        """
        Add a number to the duration of this Interval.

        Returns a new Interval with the same parameters and the updated duration.
        """
        if isinstance(other, (int, float)):
            return Interval(
                self.duration + other,
                on_overtime=self.on_overtime,
                sleep_interval=self.sleep_interval,
                hog_period=self.hog_period,
                start_time=self.start_time,  # Copy start_time
            )
        return NotImplemented

    def __sub__(self, other: float) -> "Interval":
        """
        Subtract a number from the duration of this Interval.

        Returns a new Interval with the same parameters and the updated duration.
        """
        if isinstance(other, (int, float)):
            return Interval(
                self.duration - other,
                on_overtime=self.on_overtime,
                sleep_interval=self.sleep_interval,
                hog_period=self.hog_period,
                start_time=self.start_time,  # Copy start_time
            )
        return NotImplemented

    def __mul__(self, other: float) -> "Interval":
        """
        Multiply the duration of this Interval by a number.

        Returns a new Interval with the same parameters and the updated duration.
        """
        if isinstance(other, (int, float)):
            return Interval(
                self.duration * other,
                on_overtime=self.on_overtime,
                sleep_interval=self.sleep_interval,
                hog_period=self.hog_period,
                start_time=self.start_time,  # Copy start_time
            )
        return NotImplemented

    def __truediv__(self, other: float) -> "Interval":
        """
        Divide the duration of this Interval by a number.

        Returns a new Interval with the same parameters and the updated duration.
        """
        if isinstance(other, (int, float)):
            return Interval(
                self.duration / other,
                on_overtime=self.on_overtime,
                sleep_interval=self.sleep_interval,
                hog_period=self.hog_period,
                start_time=self.start_time,  # Copy start_time
            )
        return NotImplemented

    def __iadd__(self, other: float) -> "Interval":
        """
        Add a number to the duration of the current Interval (in-place).
        """
        if isinstance(other, (int, float)):
            self.duration += other
        return self

    def __isub__(self, other: float) -> "Interval":
        """
        Subtract a number from the duration of the current Interval (in-place).
        """
        if isinstance(other, (int, float)):
            self.duration -= other
        return self

    def __imul__(self, other: float) -> "Interval":
        """
        Multiply the duration of the current Interval by a number (in-place).
        """
        if isinstance(other, (int, float)):
            self.duration *= other
        return self

    def __itruediv__(self, other: float) -> "Interval":
        """
        Divide the duration of the current Interval by a number (in-place).
        """
        if isinstance(other, (int, float)):
            self.duration /= other
        return self
