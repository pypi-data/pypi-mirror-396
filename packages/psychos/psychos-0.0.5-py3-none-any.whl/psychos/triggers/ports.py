"""This module provides implementations for sending values through a communication port."""

import logging
from typing import Union, Literal

from ..utils.decorators import register

__all__ = ["get_port", "BasePort", "SerialPort", "ParallelPort", "DummyPort"]

logger = logging.getLogger(__name__)


PORTS = {}

PortLiteral = Union[Literal["serial"], Literal["parallel"], Literal["dummy"], str]


def get_port(name: PortLiteral):
    """Get a port implementation by name (e.g. serial, parallel, dummy)."""
    port = PORTS.get(name, None)
    if port is None:
        raise ValueError(
            f"Unknown port: {name}. Available port implementations: {list(PORTS.keys())}"
        )


class BasePort:
    """Base class for a port."""

    def __init__(self, address, log: bool = True):
        self.address = address
        self.log = log

    def send(self, value):
        """Send a trigger code through the port."""
        raise NotImplementedError("Subclasses must implement this method.")

    def reset(self):
        """Reset the port (e.g., set trigger to 0)."""
        raise NotImplementedError("Subclasses must implement this method.")

    def close(self):
        """Close the port connection."""
        raise NotImplementedError("Subclasses must implement this method.")

    def encode(self, value):
        """Encode a value to send through the port."""
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.address})"

    def _log(self, message):
        if self.log:
            logger.info(f"{self}: {message}")

    def __del__(self):
        self.close()


@register("serial", PORTS)
class SerialPort(BasePort):
    """
    Serial port implementation using pyserial.

    This class provides an implementation of a serial communication port using the
    pyserial library. It supports sending data as either integers (converted to a
    single byte) or as bytes, resetting the port to a predefined state, and closing
    the connection.

    Note
    ----
    This class is based on `pyserial` and requires it to be installed. You can install
    it via pip.

    Examples
    --------
    Using a Windows COM port:
    >>> sp = SerialPort(address='COM3', baudrate=9600, timeout=1)
    >>> sp.send(255)         # Sends the byte corresponding to 255.
    >>> sp.send(b'\xff')     # Sends the byte directly.
    >>> sp.reset()           # Resets the port.
    >>> sp.close()           # Closes the connection.

    Using a Unix-like system port:
    >>> sp = SerialPort(address='/dev/ttyUSB0', baudrate=115200)
    >>> sp.send(128)         # Sends the byte corresponding to 128.
    >>> sp.send(b'\x80')     # Sends the byte directly.
    """

    def __init__(
        self,
        address: str,
        baudrate: int = 115200,
        reset_value: bytes = b"\x00",
        log: bool = True,
        **kwargs,
    ):
        """
        Initialize the SerialPort instance.

        Parameters
        ----------
        address : Optional[str], optional
            The serial port address (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Unix-like systems).
            Defaults to None.
        baudrate : int, optional
            The baud rate for the serial connection. Defaults to 115200.
        reset_value : bytes, optional
            The byte sequence used to reset the port. Defaults to b"\\x00".
        **kwargs
            Additional keyword arguments to pass to the serial.Serial constructor (e.g., timeout).

        Raises
        ------
        ImportError
            If the pyserial library is not installed.

        Examples
        --------
        >>> sp = SerialPort(address='COM3', baudrate=9600, timeout=1)
        >>> sp = SerialPort(address='/dev/ttyUSB0', baudrate=115200)
        """
        try:
            import serial
        except ImportError:
            raise ImportError("pyserial is required for SerialPort.")

        super().__init__(address, log=log)
        self.reset_value = reset_value
        self.connection = serial.Serial(address, baudrate=baudrate, **kwargs)

    def send(self, value: Union[int, bytes]):
        """
        Send a value over the serial port.

        If an integer is provided, it is converted to a single byte using big-endian byte order.
        If a multi-byte conversion is required, convert the value to bytes before calling this method.

        Parameters
        ----------
        value : Union[int, bytes]
            The value to send. If an integer is provided, it will be converted to a single byte.
            For other sizes or multi-byte values, pass the value as bytes.

        Examples
        --------
        >>> sp = SerialPort(address='COM3')
        >>> sp.send(255)         # Converts 255 to a single byte and sends it.
        >>> sp.send(b'\xff')     # Sends the byte directly.
        """
        if self.connection is None:
            raise RuntimeError("The port is closed.")

        value = self.encode(value)
        self.connection.write(value)
        self._log(f"Sent value: {value}")

    def encode(self, value: Union[int, bytes]) -> bytes:
        """Encode a value as bytes."""
        if isinstance(value, int):
            value = hex(value)[2:4].encode()
        return value

    def reset(self):
        """
        Reset the serial port by sending the predefined reset value.

        This is typically used to return the port to a known, idle state.
        """
        self.connection.write(self.reset_value)

    def close(self):
        """
        Close the serial port connection.

        This method should be called to properly release the serial port when it is no longer needed.
        """
        if self.connection is not None:
            self.connection.close()
            del self.connection
            self.connection = None
            self._log("Closed port connection")


@register("parallel", PORTS)
class ParallelPort(BasePort):
    """
    Parallel port implementation using pyparallel.

    This class provides an implementation for sending triggers via a parallel port using the
    pyparallel library. It supports sending data as either integers or as bytes. If an integer
    is provided, it is converted to a single byte using big-endian byte order. For multi-byte
    values, send the data as bytes directly.

    Note
    ----
    This class is based on pyparallel and requires it to be installed. You can install it via pip:

        pip install pyparallel

    Examples
    --------
    Using a typical PC parallel port address:
    >>> pp = ParallelPort(address='0x378')
    >>> pp.send(128)         # Converts 128 to a single byte and sends it.
    >>> pp.send(b'\x80')     # Sends the byte directly.
    >>> pp.reset()           # Resets the port (sets data to 0).

    Using an alternative port address:
    >>> pp2 = ParallelPort(address='0x3BC')
    >>> pp2.send(255)
    """

    def __init__(self, address: str, reset_value: int = 0, log: bool = True, **kwargs):
        """
        Initialize the ParallelPort instance.

        Parameters
        ----------
        address : str
            The address of the parallel port (e.g., '0x378' is a common base address on x86 systems).
        **kwargs
            Additional keyword arguments for compatibility with pyparallel.
        """
        try:
            import parallel
        except ImportError:
            raise ImportError(
                "pyparallel is required for ParallelPort. Install it via 'pip install pyparallel'."
            )

        super().__init__(address, log=log)
        self.reset_value = reset_value
        # Convert hexadecimal string addresses to integer, if applicable.
        try:
            if isinstance(address, str) and address.startswith("0x"):
                addr_int = int(address, 16)
            else:
                addr_int = int(address)
        except (ValueError, TypeError):
            addr_int = address  # If conversion fails, use address as provided.

        self._port = parallel.Parallel(addr_int, **kwargs)

    def send(self, value: Union[int, bytes]):
        """
        Send a value over the parallel port.

        If an integer is provided, it is converted to a single byte using big-endian byte order.
        If a different byte size is required, send the data as bytes directly.

        Parameters
        ----------
        value : Union[int, bytes]
            The value to send. If an integer is provided, it will be converted to a single byte.
            For multi-byte values, provide the data as bytes.

        Examples
        --------
        >>> pp = ParallelPort(address='0x378')
        >>> pp.send(128)         # Converts 128 to a single byte and sends it.
        >>> pp.send(b'\x80')     # Sends the byte directly.
        """
        if self._port is None:
            raise RuntimeError("The port is closed.")

        data = self.encode(value)
        self._port.setData(data)
        self._log(f"Set value: {value}")

    def encode(self, value: Union[int, bytes]):
        """Encode a value as bytes."""
        return value

    def reset(self):
        """
        Reset the parallel port by setting its data register to 0.

        This method returns the port to a known, idle state.
        """
        self._port.setData(self.reset_value)
        self._log(f"Reset port to {self.reset_value}")

    def close(self):
        """
        Close the parallel port connection.

        For pyparallel, there is no explicit close method; this method is provided for interface
        consistency.
        """
        if self._port is not None:
            del self._port
            self._port = None
            self._log("Closed port connection")


@register("dummy", PORTS)
class DummyPort(BasePort):
    """
    Dummy port implementation for testing and debugging.

    This class simulates a port without requiring actual hardware.
    It logs all values that are sent, reset actions, and close operations.

    Examples
    --------
    >>> dummy = DummyPort(address='dummy')
    >>> dummy.send(128)        # Logs the sending of integer 128.
    >>> dummy.send(b'\x80')    # Logs the sending of the byte b'\x80'.
    >>> dummy.reset()          # Logs the reset action.
    >>> dummy.close()          # Logs the close action.
    """

    def __init__(self, log: bool = True):
        """
        Initialize the DummyPort instance.

        Parameters
        ----------
        address : str
            A dummy address identifier.
        **kwargs
            Additional keyword arguments (ignored).
        """
        super().__init__(None, log=log)
        self._open = True

    def send(self, value: Union[int, bytes]):
        """
        Log the value that would be sent over the port.

        If an integer is provided, it must be between 0 and 255. If a bytes object
        is provided, it must be exactly one byte long. For multi-byte values, send the
        data in separate calls.

        Parameters
        ----------
        value : Union[int, bytes]
            The value to log. If an integer, it is logged directly.
            If bytes, it is converted to an integer for logging.
        """
        self._log(f"Sent value: {value} (simulated)")

    def reset(self):
        """
        Log the action of resetting the port.

        This method simulates resetting the port to a known, idle state.
        """
        logger.info("DummyPort: Resetting port (simulated)")

    def close(self):
        """
        Log the action of closing the port.

        This method simulates closing the port connection.
        """
        if self._open:
            self._open = False
            logger.info("DummyPort: Closing port (simulated)")
