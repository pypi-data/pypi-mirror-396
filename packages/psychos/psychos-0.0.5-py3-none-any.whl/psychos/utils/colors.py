"""psychos.utils.colors: Module with utility functions to handle color conversions."""

import re
from typing import Optional, Tuple, Iterable, Union, Callable, List

from ..types import ColorType, ColorSpace

__all__ = ["Color"]


class Color:
    """
    A class to handle color conversions between different formats.

    Parameters
    ----------
    value : Optional[ColorType]
        The initial color value. Can be:
        - None: This sets the color to None.
        - str: A hex string (e.g., "#FF5733") or color name (e.g., "red").
        - Iterable with 3 or 4 numbers (ints [0,255] or floats).
    """

    COLOR_CONVERSIONS = {}
    NAMED_COLORS = {}

    def __init__(
        self,
        color: Optional[Union[ColorType, "Color"]] = None,
        space: Union[ColorSpace, str] = "auto",
    ) -> None:
        """Initialize the Color"""
        if isinstance(color, Color):
            space = color.space
            color = color.color

        if space is not None and isinstance(space, str):
            space = space.lower().strip()

        if space not in (self.list_spaces() + [None, "auto"]):
            raise ValueError(f"Invalid color space: '{space}'. Available: {self.list_spaces()}")

        self.color = color
        self.space = space

        if self.space == "auto":
            self._detect_space()

    def _detect_space(self):
        """Detect the color space of the input color between common formats (rgb, hex, name)."""
        if self.color is None:
            self.space = None

        elif isinstance(self.color, str):
            self._detect_string_space()

        elif isinstance(self.color, (Iterable, tuple, list)):
            self._detect_iterable_space()
        else:
            raise ValueError("Cannot detect color space from input.")

    def _detect_string_space(self):
        """Detect the color space of the input color string."""

        color = self.color.lower().strip().replace(" ", "")
        # Check if a named color
        if color in self.NAMED_COLORS:
            self.space = "name"
            self.color = color
        # Check if a hex color
        elif re.match(r"^#([0-9a-fA-F]{3}){1,2}$", color):
            self.space = "hex"
        # Check if a hexa color
        elif re.match(r"^#([0-9a-fA-F]{4}){1,2}$", color):
            self.space = "hexa"

        else:
            raise ValueError(
                "Cannot detect color space from input. Is a not valid hex color or named color?"
            )

    def _detect_iterable_space(self):
        """Detect the color space of the input color iterable."""
        colors = tuple(self.color)

        # 3 elements, are between 0 and 1: RGB
        if len(colors) == 3 and all(0 <= c <= 1 for c in colors):
            self.space = "rgb"
        # 4 elements, are between 0 and 1: RGBA
        elif len(colors) == 4 and all(0 <= c <= 1 for c in colors):
            self.space = "rgba"
        # 3 elements, are between 0 and 255: RGB255
        elif len(colors) == 3 and all(0 <= c <= 255 for c in colors):
            self.space = "rgb255"
            self.color = tuple(int(c) for c in colors)
        # 4 elements, are between 0 and 255: RGBA255
        elif len(colors) == 4 and all(0 <= c <= 255 for c in colors):
            self.space = "rgba255"
            self.color = tuple(int(c) for c in colors)
        else:
            raise ValueError("Ambiguous color format. Please specify the color space.")

    def __repr__(self):
        """String representation of the Color object."""
        return f"Color({self.color}, space='{self.space}')"

    @classmethod
    def _find_conversion(cls, from_space: str, to_space: str) -> List[Callable]:
        """
        Find a path of conversions from 'from_space' to 'to_space' using BFS.

        Parameters
        ----------
        from_space : str
            The initial color space.
        to_space : str
            The target color space.

        Returns
        -------
        List[Callable]
            A list of conversion functions to apply in order.

        Raises
        ------
        ValueError
            If no conversion path exists between 'from_space' and 'to_space'.
        """
        from collections import deque  # pylint: disable=import-outside-toplevel

        # BFS initialization
        queue = deque([(from_space, [])])  # (current_space, conversion_path)
        visited = set()

        while queue:
            current_space, path = queue.popleft()

            # If we reached the target space, return the conversion path
            if current_space == to_space:
                return path

            # If already visited, skip
            if current_space in visited:
                continue

            # Mark as visited
            visited.add(current_space)

            # Explore neighbors (available conversions from current_space)
            for neighbor, func in cls.COLOR_CONVERSIONS.get(current_space, []):
                if neighbor not in visited:
                    # Enqueue the neighbor with updated path
                    queue.append((neighbor, path + [func]))

        # If no path was found, raise an error
        raise ValueError(f"No conversion path found from {from_space} to {to_space}")

    @classmethod
    def list_spaces(cls) -> List[str]:
        """List all available color spaces."""
        return list(cls.COLOR_CONVERSIONS.keys())

    @classmethod
    def list_named_colors(cls) -> List[str]:
        """List all available named colors."""
        return list(cls.NAMED_COLORS.keys())

    def to(self, space: Union[ColorSpace, str]) -> ColorType:
        """Generic class to get the color in a specific space.

        Parameters
        ----------

        space : ColorSpace
            The target color space. Can see available options calling :meth:`list_spaces`.

        Returns
        -------
        ColorType
            The color in the target space (e.g. An RGB tuple, a hex string, etc).

        """
        if self.color is None or space == self.space:
            return self.color

        for to_space, func in self.COLOR_CONVERSIONS.get(self.space, []):  # Direct conversion
            if to_space == space:
                return func(self.color)

        # Find the shortest path of conversions to reach the target space
        conversion_path = self._find_conversion(self.space, space)
        color = self.color

        # Apply conversions chain
        for func in conversion_path:
            color = func(color)

        return color

    def to_rgb(self) -> Tuple[float, float, float]:
        """
        Convert the current color to the RGB color space (float values between 0 and 1).

        Returns
        -------
        Tuple[float, float, float]
            A tuple representing the RGB components of the color.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_rgb()
        (1.0, 0.341, 0.2)

        >>> color = Color("red")
        >>> color.to_rgb()
        (1.0, 0.0, 0.0)
        """
        return self.to(space="rgb")

    def to_rgba(self) -> Tuple[float, float, float, float]:
        """
        Convert the current color to the RGBA color space (float values between 0 and 1).

        Returns
        -------
        Tuple[float, float, float, float]
            A tuple representing the RGBA components of the color, with the alpha channel.

        Example
        -------
        >>> color = Color("#ff573380")
        >>> color.to_rgba()
        (1.0, 0.341, 0.2, 0.5)

        >>> color = Color("green")
        >>> color.to_rgba()
        (0.0, 1.0, 0.0, 1.0)
        """
        return self.to(space="rgba")

    def to_rgb255(self) -> Tuple[int, int, int]:
        """
        Convert the current color to the RGB color space (integer values between 0 and 255).

        Returns
        -------
        Tuple[int, int, int]
            A tuple representing the RGB components of the color in integer form.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_rgb255()
        (255, 87, 51)

        >>> color = Color("blue")
        >>> color.to_rgb255()
        (0, 0, 255)
        """
        return self.to(space="rgb255")

    def to_rgba255(self) -> Tuple[int, int, int, int]:
        """
        Convert the current color to the RGBA color space (integer values between 0 and 255).

        Returns
        -------
        Tuple[int, int, int, int]
            A tuple representing the RGBA components of the color in integer form.

        Example
        -------
        >>> color = Color("#ff573380")
        >>> color.to_rgba255()
        (255, 87, 51, 128)

        >>> color = Color("red")
        >>> color.to_rgba255()
        (255, 0, 0, 255)
        """
        return self.to(space="rgba255")

    def to_hex(self) -> str:
        """
        Convert the current color to a hexadecimal string.

        Returns
        -------
        str
            A string representing the color in hex format.

        Example
        -------
        >>> color = Color((255, 87, 51))
        >>> color.to_hex()
        '#ff5733'

        >>> color = Color("blue")
        >>> color.to_hex()
        '#0000ff'
        """
        return self.to(space="hex")

    def to_hexa(self) -> str:
        """
        Convert the current color to a hexadecimal string with alpha (transparency) included.

        Returns
        -------
        str
            A string representing the color in hex format, including the alpha value.

        Example
        -------
        >>> color = Color((255, 87, 51, 128))
        >>> color.to_hexa()
        '#ff573380'

        >>> color = Color("red")
        >>> color.to_hexa()
        '#ff0000ff'
        """
        return self.to(space="hexa")

    def to_name(self) -> str:
        """
        Convert the current color to a named color, if available.

        Returns
        -------
        str
            A string representing the color name, if it matches one of the known color names.

        Raises
        ------
        ValueError
            If no matching color name is found.

        Example
        -------
        >>> color = Color("#ff0000")
        >>> color.to_name()
        'red'

        >>> color = Color("green")
        >>> color.to_name()
        'green'
        """
        return self.to(space="name")

    def to_hsv(self) -> Tuple[float, float, float]:
        """
        Convert the current color to the HSV color space.

        Returns
        -------
        Tuple[float, float, float]
            A tuple representing the HSV components of the color.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_hsv()
        (0.033, 0.8, 1.0)

        >>> color = Color("purple")
        >>> color.to_hsv()
        (0.833, 1.0, 0.502)
        """
        return self.to(space="hsv")

    def to_cmyk(self) -> Tuple[float, float, float, float]:
        """
        Convert the current color to the CMYK color space.

        Returns
        -------
        Tuple[float, float, float, float]
            A tuple representing the CMYK components of the color.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_cmyk()
        (0.0, 0.66, 0.8, 0.0)

        >>> color = Color("yellow")
        >>> color.to_cmyk()
        (0.0, 0.0, 1.0, 0.0)
        """
        return self.to(space="cmyk")

    def to_yiq(self) -> Tuple[float, float, float]:
        """
        Convert the current color to the YIQ color space (used for TV broadcasting).

        Returns
        -------
        Tuple[float, float, float]
            A tuple representing the YIQ components of the color.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_yiq()
        (0.592, 0.458, 0.079)

        >>> color = Color("black")
        >>> color.to_yiq()
        (0.0, 0.0, 0.0)
        """
        return self.to(space="yiq")

    def to_hsl(self) -> Tuple[float, float, float]:
        """
        Convert the current color to the HSL color space (Hue, Saturation, Lightness).

        Returns
        -------
        Tuple[float, float, float]
            A tuple representing the HSL components of the color.

        Example
        -------
        >>> color = Color("#ff5733")
        >>> color.to_hsl()
        (0.033, 1.0, 0.6)

        >>> color = Color("blue")
        >>> color.to_hsl()
        (0.667, 1.0, 0.5)
        """
        return self.to(space="hsl")

    @classmethod
    def register_conversion(cls, from_space: str, to_space: str, func: Callable = None) -> Callable:
        """
        Register a new color conversion function, either by using it as a
        decorator or by calling it directly with a function.

        Usage:
            @Color.register_conversion("rgb", "rgba")
            def rgb_to_rgba(...): pass

            or

            Color.register_conversion("rgb", "rgba", rgb_to_rgba)

        Parameters
        ----------
        from_space : str
            The source color space.
        to_space : str
            The target color space.
        func : callable, optional
            The conversion function to register. If None, it's used as a decorator.

        Returns
        -------
        callable
            The conversion function, or the decorator if `func` is None.
        """
        if func is not None:
            # Direct method call: Color.register_conversion("rgb", "rgba", func)
            cls.COLOR_CONVERSIONS.setdefault(from_space, []).append((to_space, func))
            return func

        # Return the decorator if no function is passed
        def decorator(f):
            cls.COLOR_CONVERSIONS.setdefault(from_space, []).append((to_space, f))
            return f

        return decorator

    @classmethod
    def register_named_color(cls, name: str, hex_code: str) -> None:
        """Register a new named color."""
        cls.NAMED_COLORS[name.lower()] = hex_code

    @classmethod
    def batch_register_named_colors(cls, colors: dict) -> None:
        """Register multiple named colors at once."""
        cls.NAMED_COLORS.update(colors)


@Color.register_conversion("rgb", "rgba")
def rgb_to_rgba(color: Tuple[float, float, float]) -> Tuple[float, float, float, float]:
    """Conversion between RGB to RGBA"""
    r, g, b = color
    return (r, g, b, 1.0)


@Color.register_conversion("rgba", "rgb")
def rgba_to_rgb(color: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
    """Conversion between RGBA to RGB. This will loss alpha channel"""
    r, g, b, _ = color
    return (r, g, b)


def _to_255(c: float) -> int:
    """Convert a 0-1 float color component to 255 scale."""
    # To int
    c = int(round(c * 255))
    # Clip to 0-255 range
    return min(max(c, 0), 255)


@Color.register_conversion("rgb", "rgb255")
def rgb_to_rgb255(color: Tuple[float, float, float, float]) -> Tuple[int, int, int]:
    """Convert RGB to RGB255."""
    r, g, b = color
    return (_to_255(r), _to_255(g), _to_255(b))


@Color.register_conversion("rgb255", "rgb")
def rgb255_to_rgb(color: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB255 to RGB."""
    return tuple(c / 255.0 for c in color)


@Color.register_conversion("rgba255", "rgba")
def rgba255_to_rgba(color: Tuple[int, int, int, int]) -> Tuple[float, float, float, float]:
    """Convert RGBA255 (0-255 scale) to RGBA (0.0-1.0 scale)."""
    r, g, b, a = color
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)


@Color.register_conversion("rgba", "rgba255")
def rgba_to_rgba255(color: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
    """Convert RGBA (0.0-1.0 scale) to RGBA255 (0-255 scale)."""
    r, g, b, a = color
    return (_to_255(r), _to_255(g), _to_255(b), _to_255(a))


@Color.register_conversion("name", "hex")
def name_to_hex(color: str) -> str:
    """Convert color name to hex."""

    if color.lower().strip().replace(" ", "") in Color.NAMED_COLORS:
        return Color.NAMED_COLORS[color.lower()]

    raise ValueError(
        f"No found color with name: '{color}'. Available colors: {Color.list_named_colors()}"
    )


@Color.register_conversion("hex", "name")
def hex_to_name(color: str) -> str:
    """Convert hex to color name if possible."""
    for name, hex_code in Color.NAMED_COLORS.items():
        if hex_code.lower() == color.lower():
            return name
    raise ValueError(f"No name found for hex color: {color}")


@Color.register_conversion("hex", "rgb255")
def hex_to_rgb255(color: str) -> Tuple[float, float, float]:
    """Convert hex to RGB."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (r, g, b)


@Color.register_conversion("rgb255", "hex")
def rgb255_to_hex(color: Tuple[float, float, float]) -> str:
    """Convert RGB to hex."""
    return f"#{''.join(f'{int(c):02X}' for c in color)}"


@Color.register_conversion("hex", "hexa")
def hex_to_hexa(color: str) -> str:
    """Convert hex to hexa by appending FF for full alpha."""
    return color + "FF" if len(color) == 7 else color


@Color.register_conversion("hexa", "hex")
def hexa_to_hex(color: str) -> str:
    """Convert hexa to hex by removing the alpha channel if it is FF."""
    return color[:7]


@Color.register_conversion("hexa", "rgba255")
def hexa_to_rgba255(color: str) -> Tuple[int, int, int, int]:
    """Convert hexa to RGBA."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    a = int(color[7:9], 16) if len(color) == 9 else 255
    return (r, g, b, a)


@Color.register_conversion("rgba255", "hexa")
def rgba255_to_hexa(color: Tuple[int, int, int, int]) -> str:
    """Convert RGBA to hexa string."""
    r, g, b, a = color
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


@Color.register_conversion("rgb", "yiq")
def rgb_to_yiq(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert RGB to YIQ."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.rgb_to_yiq(*color)


@Color.register_conversion("yiq", "rgb")
def yiq_to_rgb(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert YIQ to RGB."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.yiq_to_rgb(*color)


@Color.register_conversion("rgb", "hls")
def rgb_to_hls(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert RGB to HLS."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.rgb_to_hls(*color)


@Color.register_conversion("hls", "rgb")
def hls_to_rgb(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert HLS to RGB."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.hls_to_rgb(*color)


@Color.register_conversion("rgb", "hsv")
def rgb_to_hsv(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert RGB to HSV."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.rgb_to_hsv(*color)


@Color.register_conversion("hsv", "rgb")
def hsv_to_rgb(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert HSV to RGB."""
    import colorsys  # pylint: disable=import-outside-toplevel

    return colorsys.hsv_to_rgb(*color)


@Color.register_conversion("cmyk", "rgb")
def cmyk_to_rgb(color: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
    """Convert CMYK to RGB."""
    c, m, y, k = color
    r = (1 - c) * (1 - k)
    g = (1 - m) * (1 - k)
    b = (1 - y) * (1 - k)
    return r, g, b


@Color.register_conversion("rgb", "cmyk")
def rgb_to_cmyk(color: Tuple[float, float, float]) -> Tuple[float, float, float, float]:
    """Convert RGB to CMYK."""
    r, g, b = color
    c = 1 - r
    m = 1 - g
    y = 1 - b
    k = min(c, m, y)

    if k == 1:
        return 0.0, 0.0, 0.0, 1.0

    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return c, m, y, k


@Color.register_conversion("hls", "hsl")
def hls_to_hsl(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert HLS to HSL."""
    h, l, s = color
    return h, s, l


@Color.register_conversion("hsl", "hls")
def hsl_to_hls(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert HSL to HLS."""
    h, s, l = color
    return h, l, s


# The following dictionary contains the most common color names and their hex values.
# Have been taken from the package 'webcolors', under the BSD 3-Clause license.
# Source code: https://github.com/ubernostrum/webcolors/blob/24.8.0/src/webcolors/_definitions.py
# Copyright (c) James Bennett, and contributors. All rights reserved.
Color.batch_register_named_colors(
    {
        "aliceblue": "#f0f8ff",
        "antiquewhite": "#faebd7",
        "aqua": "#00ffff",
        "aquamarine": "#7fffd4",
        "azure": "#f0ffff",
        "beige": "#f5f5dc",
        "bisque": "#ffe4c4",
        "black": "#000000",
        "blanchedalmond": "#ffebcd",
        "blue": "#0000ff",
        "blueviolet": "#8a2be2",
        "brown": "#a52a2a",
        "burlywood": "#deb887",
        "cadetblue": "#5f9ea0",
        "chartreuse": "#7fff00",
        "chocolate": "#d2691e",
        "coral": "#ff7f50",
        "cornflowerblue": "#6495ed",
        "cornsilk": "#fff8dc",
        "crimson": "#dc143c",
        "cyan": "#00ffff",
        "darkblue": "#00008b",
        "darkcyan": "#008b8b",
        "darkgoldenrod": "#b8860b",
        "darkgray": "#a9a9a9",
        "darkgreen": "#006400",
        "darkgrey": "#a9a9a9",
        "darkkhaki": "#bdb76b",
        "darkmagenta": "#8b008b",
        "darkolivegreen": "#556b2f",
        "darkorange": "#ff8c00",
        "darkorchid": "#9932cc",
        "darkred": "#8b0000",
        "darksalmon": "#e9967a",
        "darkseagreen": "#8fbc8f",
        "darkslateblue": "#483d8b",
        "darkslategray": "#2f4f4f",
        "darkslategrey": "#2f4f4f",
        "darkturquoise": "#00ced1",
        "darkviolet": "#9400d3",
        "deeppink": "#ff1493",
        "deepskyblue": "#00bfff",
        "dimgray": "#696969",
        "dimgrey": "#696969",
        "dodgerblue": "#1e90ff",
        "eigengrau": "#16161d",
        "firebrick": "#b22222",
        "floralwhite": "#fffaf0",
        "forestgreen": "#228b22",
        "fuchsia": "#ff00ff",
        "gainsboro": "#dcdcdc",
        "ghostwhite": "#f8f8ff",
        "gold": "#ffd700",
        "goldenrod": "#daa520",
        "gray": "#808080",
        "green": "#008000",
        "greenyellow": "#adff2f",
        "grey": "#808080",
        "honeydew": "#f0fff0",
        "hotpink": "#ff69b4",
        "indianred": "#cd5c5c",
        "indigo": "#4b0082",
        "ivory": "#fffff0",
        "khaki": "#f0e68c",
        "lavender": "#e6e6fa",
        "lavenderblush": "#fff0f5",
        "lawngreen": "#7cfc00",
        "lemonchiffon": "#fffacd",
        "lightblue": "#add8e6",
        "lightcoral": "#f08080",
        "lightcyan": "#e0ffff",
        "lightgoldenrodyellow": "#fafad2",
        "lightgray": "#d3d3d3",
        "lightgreen": "#90ee90",
        "lightgrey": "#d3d3d3",
        "lightpink": "#ffb6c1",
        "lightsalmon": "#ffa07a",
        "lightseagreen": "#20b2aa",
        "lightskyblue": "#87cefa",
        "lightslategray": "#778899",
        "lightslategrey": "#778899",
        "lightsteelblue": "#b0c4de",
        "lightyellow": "#ffffe0",
        "lime": "#00ff00",
        "limegreen": "#32cd32",
        "linen": "#faf0e6",
        "magenta": "#ff00ff",
        "maroon": "#800000",
        "mediumaquamarine": "#66cdaa",
        "mediumblue": "#0000cd",
        "mediumorchid": "#ba55d3",
        "mediumpurple": "#9370db",
        "mediumseagreen": "#3cb371",
        "mediumslateblue": "#7b68ee",
        "mediumspringgreen": "#00fa9a",
        "mediumturquoise": "#48d1cc",
        "mediumvioletred": "#c71585",
        "midnightblue": "#191970",
        "mintcream": "#f5fffa",
        "mistyrose": "#ffe4e1",
        "moccasin": "#ffe4b5",
        "navajowhite": "#ffdead",
        "navy": "#000080",
        "oldlace": "#fdf5e6",
        "olive": "#808000",
        "olivedrab": "#6b8e23",
        "orange": "#ffa500",
        "orangered": "#ff4500",
        "orchid": "#da70d6",
        "palegoldenrod": "#eee8aa",
        "palegreen": "#98fb98",
        "paleturquoise": "#afeeee",
        "palevioletred": "#db7093",
        "papayawhip": "#ffefd5",
        "peachpuff": "#ffdab9",
        "peru": "#cd853f",
        "pink": "#ffc0cb",
        "plum": "#dda0dd",
        "powderblue": "#b0e0e6",
        "purple": "#800080",
        "red": "#ff0000",
        "rosybrown": "#bc8f8f",
        "royalblue": "#4169e1",
        "saddlebrown": "#8b4513",
        "salmon": "#fa8072",
        "sandybrown": "#f4a460",
        "seagreen": "#2e8b57",
        "seashell": "#fff5ee",
        "sienna": "#a0522d",
        "silver": "#c0c0c0",
        "skyblue": "#87ceeb",
        "slateblue": "#6a5acd",
        "slategray": "#708090",
        "slategrey": "#708090",
        "snow": "#fffafa",
        "springgreen": "#00ff7f",
        "steelblue": "#4682b4",
        "tan": "#d2b48c",
        "teal": "#008080",
        "thistle": "#d8bfd8",
        "tomato": "#ff6347",
        "turquoise": "#40e0d0",
        "violet": "#ee82ee",
        "wheat": "#f5deb3",
        "white": "#ffffff",
        "whitesmoke": "#f5f5f5",
        "yellow": "#ffff00",
        "yellowgreen": "#9acd32",
    }
)
