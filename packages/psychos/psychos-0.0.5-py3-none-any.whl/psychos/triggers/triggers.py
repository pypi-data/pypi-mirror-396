"""This module provides implementations for sending triggers through a communication port."""

from typing import Union, Optional, Dict

from .ports import BasePort
from ..core.time import wait

__all__ = ["BaseTrigger", "DelayTrigger", "StepTrigger"]


class BaseTrigger:
    """
    Abstract base class for trigger implementations.

    This class provides a common interface for sending triggers through a communication port.
    It includes functionality to resolve trigger values using an optional mapping and to manage
    the port connection.

    Attributes
    ----------
    port : BasePort
        The communication port used to send trigger values.
    mapping : Dict[str, Union[int, bytes]]
        An optional dictionary mapping trigger names to their corresponding values.
    """

    def __init__(
        self,
        port: BasePort,
        mapping: Optional[Dict[str, Union[int, bytes]]] = None,
    ):
        """
        Initialize a BaseTrigger instance.

        Parameters
        ----------
        port : BasePort
            The communication port instance used for sending triggers.
        mapping : Dict[str, Union[int, bytes]], optional
            A dictionary mapping trigger names (as strings) to their corresponding values
            (as integers or bytes). Defaults to None.
        """
        self.port = port
        self.mapping = mapping or {}

    def resolve_value(self, value: Union[str, int, bytes]) -> Union[int, bytes]:
        """
        Resolve the trigger value using the provided mapping.

        If the value is a string, it is used as a key to retrieve the corresponding trigger value
        from the mapping. If no mapping exists for the string, a ValueError is raised.

        Parameters
        ----------
        value : Union[str, int, bytes]
            The trigger value to resolve. If a string is provided, it is treated as a key
            for the mapping.

        Returns
        -------
        Union[int, bytes]
            The resolved trigger value.

        Raises
        ------
        ValueError
            If the value is a string and not found in the mapping.
        """
        if isinstance(value, str):
            resolved = self.mapping.get(value, None)
            if resolved is None:
                raise ValueError(f"Value '{value}' not found in mapping.")
            value = resolved

        return value

    def send(self, value: Union[str, int, bytes]):
        """
        Send a trigger value through the communication port.

        This method should be implemented by subclasses.

        Parameters
        ----------
        value
            The trigger value to send. Its type (string, integer, or bytes) will be resolved
            appropriately by the subclass.

        Raises
        ------
        NotImplementedError
            Always, as this is an abstract method.
        """
        raise NotImplementedError("Should be implemented in subclass. This is a base class.")

    def close(self):
        """
        Close the trigger by closing the associated communication port.

        After closing, the port reference is set to None.
        """
        self.port.close()

    def __repr__(self):
        """
        Return a string representation of the trigger instance.

        Returns
        -------
        str
            A string representation including the class name and associated port.
        """
        return f"{self.__class__.__name__}({self.port})"

    def __del__(self):
        """
        Destructor for the trigger instance.

        Automatically closes the communication port when the trigger instance is garbage collected.
        """
        self.close()


class DelayTrigger(BaseTrigger):
    """
    Trigger that sends a value, waits for a specified delay, then resets the port.

    This trigger sends a value through the communication port, waits for a predefined delay to ensure
    that the value is registered, and then resets the port to a default state.

    Attributes
    ----------
    delay : float
        The delay in seconds after sending the trigger before resetting the port.
    """

    def __init__(
        self,
        port: "BasePort",
        mapping: Optional[dict] = None,
        delay: float = 0.01,
    ):
        """
        Initialize a DelayTrigger instance.

        Parameters
        ----------
        port : BasePort
            The communication port instance used for sending triggers.
        mapping : dict, optional
            A dictionary mapping trigger names to values.
        delay : float, optional
            The delay in seconds to wait after sending the trigger before resetting.
            Defaults to 0.01.
        """
        super().__init__(port=port, mapping=mapping)
        self.delay = delay

    def send(self, value: Union[str, int, bytes]):
        """
        Send a trigger value, wait for a specified delay, and then reset the port.

        Parameters
        ----------
        value
            The trigger value to send. This can be a string (which will be resolved using the mapping),
            an integer, or bytes.
        """
        value = self.resolve_value(value)
        self.port.send(value)
        wait(self.delay)
        self.port.reset()


class StepTrigger(BaseTrigger):
    """
    Trigger that sends a value without resetting the port.

    This trigger sends a value via the communication port and leaves the port in the state of
    the last sent value.
    """

    def send(self, value: Union[str, int, bytes]):
        """
        Send a trigger value without resetting the port.

        Parameters
        ----------
        value
            The trigger value to send. This can be a string (which will be resolved using the mapping),
            an integer, or bytes.
        """
        value = self.resolve_value(value)
        self.port.send(value)
