import pytest
from psychos.utils.colors import Color

SAMPLE_COLORS = {
    "hex": "#32cd32",
    "hexa": "#32cd3280",  # 50% opacity
    "name": "limegreen",
    "rgb": (50 / 255, 205 / 255, 50 / 255),
    "rgba": (50 / 255, 205 / 255, 50 / 255, 0.5),
    "rgb255": (50, 205, 50),
    "rgba255": (50, 205, 50, 128),  # 50% opacity
    "hsv": (1 / 3, 0.75, 0.80),
    "cmyk": (0.76, 0.0, 3 / 4, 1 / 5),
    "yiq": (0.55, -0.16, -0.31),
    "hsl": (0.33, 0.60, 0.5),
    "hls": (0.33, 0.50, 0.6),
}


@pytest.fixture
def sample_colors():
    """Fixture for creating sample colors used in tests."""
    return SAMPLE_COLORS.copy()


def test_color_init(sample_colors):
    """Test Color class initialization."""
    color = Color(sample_colors["hex"])
    assert color.color == sample_colors["hex"]
    assert color.space == "hex"


def test_to_rgb(sample_colors):
    """Test conversion to RGB."""
    color = Color(sample_colors["hex"])
    assert color.to_rgb() == pytest.approx(sample_colors["rgb"])


def test_to_rgba(sample_colors):
    """Test conversion to RGBA."""
    color = Color(sample_colors["hexa"])

    assert color.to_rgba() == pytest.approx(sample_colors["rgba"], abs=0.1)


def test_to_rgb255(sample_colors):
    """Test conversion to RGB255."""
    color = Color(sample_colors["hex"])
    assert color.to_rgb255() == pytest.approx(sample_colors["rgb255"])


def test_to_rgba255(sample_colors):
    """Test conversion to RGBA255."""
    color = Color(sample_colors["hexa"])
    assert color.to_rgba255() == pytest.approx(sample_colors["rgba255"])


def test_to_hex(sample_colors):
    """Test conversion to hex."""
    color = Color(sample_colors["rgb255"])
    assert color.to_hex().lower() == sample_colors["hex"].lower()


def test_to_hexa(sample_colors):
    """Test conversion to hexa."""
    color = Color(sample_colors["rgba255"], space="rgba255")

    assert color.to_hexa().lower() == sample_colors["hexa"].lower()


def test_to_name(sample_colors):
    """Test conversion to name."""
    color = Color(sample_colors["hex"])
    assert color.to_name() == sample_colors["name"]


def test_to_hsv(sample_colors):
    """Test conversion to HSV."""
    color = Color(sample_colors["hex"])
    assert color.to_hsv() == pytest.approx(sample_colors["hsv"], abs=0.1)


def test_to_cmyk(sample_colors):
    """Test conversion to CMYK."""
    color = Color(sample_colors["hex"])
    assert color.to_cmyk() == pytest.approx(sample_colors["cmyk"], abs=0.1)


def test_to_yiq(sample_colors):
    """Test conversion to YIQ."""
    color = Color(sample_colors["hex"])
    assert color.to_yiq() == pytest.approx(sample_colors["yiq"], abs=0.1)


def test_to_hsl(sample_colors):
    """Test conversion to HSL."""
    color = Color(sample_colors["hex"])
    assert color.to_hsl() == pytest.approx(sample_colors["hsl"], abs=0.1)


def test_invalid_space():
    """Test invalid color space raises a ValueError."""
    with pytest.raises(ValueError):
        Color("red", space="invalid_space")


def test_conversion_path():
    """Test finding the conversion path between color spaces."""
    color = Color("#ff5733")
    path = color._find_conversion("rgb", "hsv")
    assert isinstance(path, list)
    assert len(path) == 1


def test_direct_conversion():
    """Test a direct conversion function works."""
    color = Color("#ff5733")
    assert color.to_rgb255() == (255, 87, 51)


def test_indirect_conversion(sample_colors):
    """Test a conversion with multiple steps."""
    color = Color("#32cd32")
    assert color.to_yiq() == pytest.approx(sample_colors["yiq"], abs=0.1)


def test_color_initialization():
    """Test when using a color for the initialization."""
    color = Color("#32cd32")
    color2 = Color(color)
    assert color.color == color2.color
    assert color.space == color2.space

    assert color.to_rgb() == color2.to_rgb()


def test_invalid_color_space():
    """Test when an invalid color space is used."""
    with pytest.raises(ValueError):
        Color("#32cd32", space=3)


def test_detect_space_named_color():
    """Test when a named color is used."""
    color = Color("limegreen")
    assert color.space == "name"
    assert color.color == "limegreen"


def test_detect_space_rgb():
    color = Color((0.5, 0.5, 0.5))
    assert color.space == "rgb"
    assert color.color == (0.5, 0.5, 0.5)


def test_detect_space_rgba():
    color = Color((0.5, 0.5, 0.5, 0.5))
    assert color.space == "rgba"
    assert color.color == (0.5, 0.5, 0.5, 0.5)


def test_detect_space_rgba255():
    color = Color((128, 128, 128, 128), space="rgba255")
    assert color.space == "rgba255"
    assert color.color == (128, 128, 128, 128)


def test_ambiguous_color_space_iterable():
    """Test when an ambiguous color space is used."""
    with pytest.raises(ValueError):
        Color([0.5, -1, 0.3])


def test_str():
    color = Color("#32cd32")
    assert str(color) == "Color(#32cd32, space='hex')"


def test_list_named_colors():
    """Test listing named colors."""
    named_colors = Color.list_named_colors()
    assert len(named_colors) > 100
    assert "limegreen" in named_colors


def test_register_named_color():
    """Test registering a named color."""
    Color.register_named_color("custom", "#32cd32")
    assert "custom" in Color.list_named_colors()
    assert Color("custom").to_hex() == "#32cd32"


def test_register_custom_color_conversion():
    """Test registering a color conversion."""

    Color.register_conversion("hex", "custom_space", lambda _: (0.5, 0.5, 0.5))
    color = Color("#32cd32")
    assert color.to(space="custom_space") == (0.5, 0.5, 0.5)


@pytest.mark.parametrize("to_space", SAMPLE_COLORS.keys())
@pytest.mark.parametrize("from_space", SAMPLE_COLORS.keys())
def test_registerd_conversions(to_space, from_space, sample_colors):
    alpha_spaces = ["hexa", "rgba", "rgba255"]

    to_color = sample_colors[to_space]

    has_from_alpha = from_space in alpha_spaces
    has_to_alpha = to_space in alpha_spaces

    if has_from_alpha:
        color = Color(sample_colors["rgba255"], space="rgba255")
        color = Color(color.to(from_space), space=from_space)
    elif not has_from_alpha:
        color = Color(sample_colors["rgb255"], space="rgb255")
        color = Color(color.to(from_space), space=from_space)

    if to_space == from_space:
        assert color.to(to_space) == color.color
    elif to_space == "name":
        assert color.to(to_space) == sample_colors["name"]
    elif to_space in ["hexa", "hex"]:
        target_color = to_color.lower()
        if has_to_alpha and not has_from_alpha:
            target_color = target_color[:7] + "ff"
        assert color.to(to_space).lower() == target_color
    elif has_from_alpha or not has_to_alpha:
        assert color.to(to_space) == pytest.approx(to_color, abs=0.1)
    elif not has_from_alpha and has_to_alpha:
        assert color.to(to_space)[:3] == pytest.approx(to_color[:3], abs=0.1)
    else:
        pytest.skip("Conversion not implemented")


def test_none_color_init():
    """Test initializing a color with None."""
    color = Color(None)
    assert color.color is None
    assert color.space is None


@pytest.mark.parametrize("to_space", SAMPLE_COLORS.keys())
def test_conversions_from_none(to_space):
    color = Color(None)
    assert color.to(to_space) is None


def test_invalid_auto_detection():

    with pytest.raises(ValueError):
        Color(3)


def test_invalid_string_color():
    with pytest.raises(ValueError):
        Color("invalid_color")


def test_not_found_path_conversions():
    # Register color conversion
    Color.register_conversion("test", "hex", lambda _: "#ffffff")
    # Check if the conversion is found
    color = Color("#32cd32", space="hex")
    # Conversion cannot be found (We defined text->hex but not hex->text)
    with pytest.raises(ValueError):
        color.to("test")


def test_not_found_named_color():

    color = Color("#32cc32")
    with pytest.raises(ValueError):
        color.to_name()


def test_invalid_name_color():

    # If you specify a named color, you delay the color validation until the conversion
    color = Color("invalid_color", space="name")

    with pytest.raises(ValueError):
        color.to_rgb()


def test_detect_rgba255():
    color = Color((128, 128, 128, 128))
    assert color.space == "rgba255"
    assert color.color == (128, 128, 128, 128)

def test_cmyk_black():
    color = Color((0, 0, 0), space="rgb")
    assert color.to_cmyk() == (0., 0., 0., 1.)