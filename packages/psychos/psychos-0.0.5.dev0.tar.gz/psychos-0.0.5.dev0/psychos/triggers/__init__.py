"""psychos.triggers: Module for sending triggers to external devices."""

from typing import TYPE_CHECKING

from ..utils.lazy import attach

submod_attrs = {
    "ports": ["get_port", "BasePort", "SerialPort", "ParallelPort", "DummyPort"],
    "triggers": ["BaseTrigger", "DelayTrigger", "StepTrigger"],
}

__getattr__, __dir__, __all__ = attach(__name__, submod_attrs=submod_attrs)

if TYPE_CHECKING:
    __all__ = [
        "get_port",
        "BasePort",
        "SerialPort",
        "ParallelPort",
        "DummyPort",
        "BaseTrigger",
        "DelayTrigger",
        "StepTrigger",
    ]

    from .ports import get_port, BasePort, SerialPort, ParallelPort, DummyPort
    from .triggers import BaseTrigger, DelayTrigger, StepTrigger
