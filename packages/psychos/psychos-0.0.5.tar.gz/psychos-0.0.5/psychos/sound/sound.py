"""psychos.sound.soun module for sound synthesis and playback based on Pyglet."""

import pyglet
from pyglet.media import Player, StaticSource, load as load_sound, PlayerGroup, StreamingSource
from pyglet.media.synthesis import (
    Envelope,
    FlatEnvelope,
    LinearDecayEnvelope,
    TremoloEnvelope,
    Sawtooth as _Sawtooth,
    Silence as _Silence,
    Sine as _Sine,
    Square as _Square,
    Triangle as _Triangle,
    WhiteNoise as _WhiteNoise,
)


from ..core.time import wait

__all__ = [
    "Player",
    "StaticSource",
    "load_sound",
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


class SoundMixin:
    """Mixin to override the default Pyglet sounds methods."""

    def play(self, block: bool = False) -> "Player":
        """Play the sound."""
        
        pyglet.clock.tick() # Force a tick to ensure that the sound is played immediately.
        pyglet.app.platform_event_loop.dispatch_posted_events()
        player = super().play()
        pyglet.clock.tick()
        pyglet.app.platform_event_loop.dispatch_posted_events()
        if block:
            duration = self.duration
            if duration is not None:
                wait(duration)

        return player


class Sine(SoundMixin, _Sine):
    """Sine wave generator.

    This class is a subclass of pyglet.media.synthesis.Sine.

    Args:
        frequency (float): The frequency of the sine wave in Hz.
        duration (float): The duration of the sine wave in seconds.
        sample_rate (int): The sample rate of the sine wave in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """
    pass


class Sawtooth(SoundMixin, _Sawtooth):
    """Sawtooth wave generator.

    This class is a subclass of pyglet.media.synthesis.Sawtooth.

    Args:
        frequency (float): The frequency of the sawtooth wave in Hz.
        duration (float): The duration of the sawtooth wave in seconds.
        sample_rate (int): The sample rate of the sawtooth wave in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """

    pass


class Square(SoundMixin, _Square):
    """Square wave generator.

    This class is a subclass of pyglet.media.synthesis.Square.

    Args:
        frequency (float): The frequency of the square wave in Hz.
        duration (float): The duration of the square wave in seconds.
        sample_rate (int): The sample rate of the square wave in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """

    pass


class Triangle(SoundMixin, _Triangle):
    """Triangle wave generator.

    This class is a subclass of pyglet.media.synthesis.Triangle.

    Args:
        frequency (float): The frequency of the triangle wave in Hz.
        duration (float): The duration of the triangle wave in seconds.
        sample_rate (int): The sample rate of the triangle wave in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """

    pass


class WhiteNoise(SoundMixin, _WhiteNoise):
    """White noise generator.

    This class is a subclass of pyglet.media.synthesis.WhiteNoise.

    Args:
        duration (float): The duration of the white noise in seconds.
        sample_rate (int): The sample rate of the white noise in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """

    pass


class Silence(SoundMixin, _Silence):
    """Silence generator.

    This class is a subclass of pyglet.media.synthesis.Silence.

    Args:
        duration (float): The duration of the silence in seconds.
        sample_rate (int): The sample rate of the silence in Hz.
        envelope (Envelope): The envelope of the sine wave.
    """

    pass
