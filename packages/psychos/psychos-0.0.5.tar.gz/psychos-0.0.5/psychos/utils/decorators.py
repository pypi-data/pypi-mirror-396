"""psychos.utils.decorators: Module with utility decorators for psychos."""

from typing import Callable

__all__ = ["docstring", "register"]


def docstring(from_method: Callable) -> Callable:
    """
    Decorator that copies the docstring from one method to another.

    Parameters
    ----------
    from_method : callable
        The method to copy the docstring from.

    Returns
    -------
    callable
        The decorated method with the copied docstring.
    """

    def decorator(to_method):
        # Copy the docstring from the source method to the target method
        to_method.__doc__ = from_method.__doc__
        return to_method

    return decorator


def register(name: str, dictionary: dict) -> Callable:
    """
    Decorator to register an object in a dictionary under a specific name.

    Parameters
    ----------
    name : str
        The name to register the object.

    dictionary : dict
        The dictionary to register the object in.

    Returns
    -------
    function
        A decorator function to register the object.
    """

    def decorator(cls):
        dictionary[name] = cls
        return cls

    return decorator
