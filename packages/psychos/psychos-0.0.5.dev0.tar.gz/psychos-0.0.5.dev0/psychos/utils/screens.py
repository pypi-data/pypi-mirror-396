"""psychos.utils.screens: Utiliy function to get all available screens using pyglet."""
from typing import List

import pyglet



def get_screens() -> List["pyglet.canvas.Screen"]:
    """
    Returns all available screens using pyglet.

    Returns
    -------
    list of pyglet.canvas.Screen
        A list of all screens available on the system.
    """
    display = pyglet.canvas.get_display()
    screens = display.get_screens()
    return screens
