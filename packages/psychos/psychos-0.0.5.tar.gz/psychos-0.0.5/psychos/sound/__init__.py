"""psychos.sound: Module for creating sound elements in a Pyglet window."""

from typing import TYPE_CHECKING

from ..utils.lazy import attach


__all__ = [
    "load_sound",
    "Player",
    "StaticSource",
    "PlayerGroup",
    "StreamingSource",
    "Envelope",
    "FlatEnvelope",
    "LinearDecayEnvelope",
    "TremoloEnvelope",
    "Sawtooth",
    "Silence",
    "Sine",
    "Square",
    "Triangle",
    "WhiteNoise",
]


submod_attrs = {
    "sound": __all__,
}

__getattr__, __dir__, __all__ = attach(__name__, submod_attrs=submod_attrs)

if TYPE_CHECKING:
    from .sound import (
        load_sound,
        Player,
        StaticSource,
        PlayerGroup,
        StreamingSource,
        Envelope,
        FlatEnvelope,
        LinearDecayEnvelope,
        TremoloEnvelope,
        Sawtooth,
        Silence,
        Sine,
        Square,
        Triangle,
        WhiteNoise,
    )
