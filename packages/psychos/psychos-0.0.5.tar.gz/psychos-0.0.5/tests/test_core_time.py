"""Unit tests for the 'psychos.core.time' module related to time management."""

import pytest
import time

from psychos.core import Clock, Interval, wait


TIME_TOLERANCE = 0.1  # 10% -> Wide tolerance for github actions.
HOG_PERIOD = 0.3  # seconds

def _time():
    return time.perf_counter()

def is_close(actual, expected, tolerance):
    return abs(actual - expected) <= tolerance * expected

def dummy_sleep(duration):
    """Accurate sleep function using busy waiting for accuracy in testing."""
    start_time = _time()
    while _time() - start_time < duration:
        pass

# Test suite for the 'wait' function
def test_wait_function():
    duration = 2  # seconds
    start_time = _time()
    wait(duration, hog_period=HOG_PERIOD)
    end_time = _time()
    elapsed_time = end_time - start_time
    assert is_close(
        elapsed_time, duration, TIME_TOLERANCE
    ), f"'wait' function did not wait for {duration} seconds within 1% tolerance."


# Test suite for the 'Clock' class
def test_clock_time_method():
    clock = Clock()
    dummy_sleep(1)
    elapsed = clock.time()
    assert is_close(
        elapsed, 1, TIME_TOLERANCE
    ), f"'Clock.time()' did not return correct elapsed time within 1% tolerance."


def test_clock_reset_method():
    clock = Clock()
    dummy_sleep(1)
    clock.reset()
    dummy_sleep(1)
    elapsed = clock.time()
    assert is_close(
        elapsed, 1, TIME_TOLERANCE
    ), f"'Clock.reset()' did not reset the start time correctly."


def test_clock_with_fmt_string():
    clock = Clock(fmt="%H:%M:%S")
    formatted_time = clock.time()
    assert isinstance(
        formatted_time, str
    ), "'Clock.time()' with fmt as string did not return a string."
    # Additional checks can be added to verify the format if needed


def test_clock_with_fmt_callable():
    clock = Clock(fmt=lambda x: f"{x:.2f} seconds")
    result = clock.time()
    assert result.endswith(
        "seconds"
    ), "'Clock.time()' with fmt as callable did not process the elapsed time correctly."


def test_clock_with_invalid_fmt():
    clock = Clock(fmt=123)  # Invalid fmt
    with pytest.raises(TypeError):
        clock.time()


# Test suite for the 'Interval' class
def test_interval_wait_within_duration():
    duration = 2  # seconds
    interval = Interval(duration, hog_period=HOG_PERIOD)
    start_time = _time()
    interval.wait()
    end_time = _time()
    elapsed_time = end_time - start_time
    assert is_close(
        elapsed_time, duration, TIME_TOLERANCE
    ), f"'Interval.wait()' did not wait for the correct remaining time within 1% tolerance."


def test_interval_wait_overtime_ignore():
    duration = 1  # seconds
    interval = Interval(duration, on_overtime="ignore", hog_period=HOG_PERIOD)
    dummy_sleep(2)  # Exceed the interval
    start_time = _time()
    interval.wait()  # Should not raise an error or warning
    end_time = _time()
    elapsed_time = end_time - start_time
    assert (
        elapsed_time < 0.1
    ), "'Interval.wait()' with on_overtime='ignore' should not wait when interval is exceeded."


# @pytest.mark.filterwarnings("ignore:.*")
def test_interval_wait_overtime_warning():
    duration = 1  # seconds
    interval = Interval(duration, on_overtime="warning", hog_period=HOG_PERIOD)
    dummy_sleep(2)  # Exceed the interval
    with pytest.warns(RuntimeWarning, match="The interval of"):
        interval.wait()


def test_interval_wait_overtime_exception():
    duration = 1  # seconds
    interval = Interval(duration, on_overtime="exception", hog_period=HOG_PERIOD)
    dummy_sleep(2)  # Exceed the interval
    with pytest.raises(RuntimeError, match="The interval of"):
        interval.wait()


def test_interval_arithmetic_methods():
    interval = Interval(2)
    new_interval = interval + 1
    assert (
        new_interval.duration == 3
    ), "'Interval.__add__' did not return a new Interval with updated duration."

    new_interval = interval - 1
    assert (
        new_interval.duration == 1
    ), "'Interval.__sub__' did not return a new Interval with updated duration."

    new_interval = interval * 2
    assert (
        new_interval.duration == 4
    ), "'Interval.__mul__' did not return a new Interval with updated duration."

    new_interval = interval / 2
    assert (
        new_interval.duration == 1
    ), "'Interval.__truediv__' did not return a new Interval with updated duration."


def test_interval_inplace_arithmetic_methods():
    interval = Interval(2)
    interval += 1
    assert (
        interval.duration == 3
    ), "'Interval.__iadd__' did not update the duration in place."

    interval -= 1
    assert (
        interval.duration == 2
    ), "'Interval.__isub__' did not update the duration in place."

    interval *= 2
    assert (
        interval.duration == 4
    ), "'Interval.__imul__' did not update the duration in place."

    interval /= 2
    assert (
        interval.duration == 2
    ), "'Interval.__itruediv__' did not update the duration in place."


def test_interval_context_manager():
    duration = 2  # seconds
    with Interval(duration, hog_period=HOG_PERIOD) as interval:
        dummy_sleep(1)
    total_time = _time() - interval.start_time
    assert is_close(
        total_time, duration, TIME_TOLERANCE
    ), "'Interval' context manager did not wait for the correct remaining time within 1% tolerance."


def test_interval_remaining_method():
    interval = Interval(2, hog_period=HOG_PERIOD)
    dummy_sleep(1)
    remaining = interval.remaining()
    assert is_close(
        remaining, 1, TIME_TOLERANCE
    ), "'Interval.remaining()' did not return correct remaining time within 1% tolerance."


def test_interval_zero_duration():
    interval = Interval(0)
    start_time = _time()
    with pytest.warns(RuntimeWarning):
        interval.wait()
    elapsed_time = _time() - start_time
    assert elapsed_time < 0.1, "'Interval.wait()' with zero duration should not wait."


def test_interval_negative_duration():
    interval = Interval(-1, on_overtime="ignore")
    start_time = _time()
    interval.wait()
    elapsed_time = _time() - start_time
    assert (
        elapsed_time < 0.01
    ), "'Interval.wait()' with negative duration should not wait."


def test_interval_negative_exception_duration():
    interval = Interval(-1, on_overtime="exception")
    start_time = _time()
    with pytest.raises(RuntimeError):
        interval.wait()
    elapsed_time = _time() - start_time
    assert (
        elapsed_time < 0.01
    ), "'Interval.wait()' with negative duration should not wait."


def test_interval_on_overtime_invalid_value():
    with pytest.raises(ValueError):
        Interval(1, on_overtime="invalid_option")


def test_interval_divide_by_zero():
    interval = Interval(2)
    with pytest.raises(ZeroDivisionError):
        interval / 0
    with pytest.raises(ZeroDivisionError):
        interval /= 0


if __name__ == "__main__":
    pytest.main([__file__])
