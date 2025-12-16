from typing import Tuple, Optional, Union, Callable, Literal, TYPE_CHECKING


from .raw_image import RawImage
from .synthetic import gabor_3d


if TYPE_CHECKING:
    import numpy as np

    from ..types import ColorType, UnitType
    from .window import Window
    from .units import Unit
    


class Gabor(RawImage):
    """
    A Gabor stimulus for psychophysical experiments.

    This class generates a synthetic Gabor patch using a 3D (color) Gabor generator
    and displays it in a Pyglet window via the RawImage (Sprite) component.
    It combines the parameters for generating the Gabor stimulus with those for positioning,
    scaling, and rotating the image.

    Parameters
    ----------
    # Gabor 3D parameters:
    size : Tuple[int, int], default=(128, 128)
        The (height, width) of the generated image in pixels.
    spatial_frequency : float, default=5.0
        Cycles per entire image width.
    orientation : float, default=45.0
        Gabor orientation in degrees [0, 360]. The carrier is rotated by (360 - orientation) degrees.
    phase : float, default=0.0
        Fraction of 2π for the carrier phase, in the range [0, 1].
    sigma : Optional[float], default=0.15
        Normalized standard deviation (fraction of the minimum dimension) of the Gaussian envelope.
        If None, no envelope is applied (i.e. the envelope defaults to ones).
    gamma : float, default=1.0
        Aspect ratio (vertical stretch) of the Gaussian envelope.
    contrast : float, default=1.0
        Contrast (amplitude) of the sinusoidal carrier.
    center : Optional[Tuple[float, float]], default=None
        Center (y, x) of the Gabor patch in pixel coordinates. Defaults to the image center if None.
    cmap : Union[str, Callable[[np.ndarray], np.ndarray], Tuple[ColorType, ColorType], list], default=("black", "white")
        Colormap used to map the normalized grayscale Gabor to colors.
        If a string, it must be a valid matplotlib colormap name.
        Alternatively, a callable mapping an array in [0,1] to an RGBA image, or a tuple/list of two colors
        (low and high) for linear two-color interpolation (colors are parsed via Color().to_rgb()).
    alpha_channel : Union[Literal["envelope"], None, np.ndarray], default="envelope"
        Determines the alpha channel:
            - "envelope": use the Gaussian envelope computed in gabor_3d.
            - None: do not include an alpha channel (output will be RGB).
            - A numpy array: must have the same shape as the 2D gabor; used as the alpha channel.
    **kwargs
        Additional keyword arguments to be passed to the gabor_3d function.

    # RawImage parameters:
    image_path : Optional[str]
        The path to the image file. (Not used here since the image is generated synthetically.)
    position : Tuple[float, float], default=(0, 0)
        The position of the image in the window.
    width : Optional[float], default=None
        The target width to scale the image to.
    height : Optional[float], default=None
        The target height to scale the image to.
    scale : Optional[float], default=None
        A uniform scaling factor for the image.
    rotation : float, default=0
        The rotation angle of the image in degrees.
    anchor_x : str, default="center"
        The horizontal anchor alignment for the image.
    anchor_y : str, default="center"
        The vertical anchor alignment for the image.
    window : Optional[Window], default=None
        The window in which the image will be displayed.
    coordinates : Optional[Union[UnitType, Units]], default=None
        The coordinate system to use for positioning the image.
    **kwargs (additional)
        Additional keyword arguments are passed to the underlying Pyglet Sprite class.

    Attributes
    ----------
    Inherits all attributes from RawImage, such as position, rotation, scale, etc.

    Example
    -------
    >>> from synthetic_stim import Gabor  # or your module name
    >>> # Create a Gabor stimulus with a viridis colormap and envelope as the alpha channel.
    >>> gabor = Gabor(
    ...     size=(256, 256),
    ...     spatial_frequency=2.0,
    ...     orientation=45.0,
    ...     phase=0.25,
    ...     sigma=0.25,
    ...     gamma=1.0,
    ...     contrast=1.0,
    ...     center=(128, 128),
    ...     cmap='viridis',
    ...     alpha_channel="envelope",
    ...     position=(100, 150),
    ...     width=300,
    ...     rotation=30
    ... )
    >>> gabor.draw()
    """

    def __init__(
        self,
        # Gabor 3D parameters:
        size: Tuple[int, int] = (256, 256),
        spatial_frequency: float = 8.0,
        orientation: float = 45.0,
        phase: float = 0.0,
        sigma: Optional[float] = 0.15,
        gamma: float = 1.0,
        contrast: float = 1.0,
        center: Optional[Tuple[float, float]] = None,
        cmap: Union[
            str, Callable[["np.ndarray"], "np.ndarray"], Tuple["ColorType", "ColorType"], list
        ] = ("black", "white"),
        alpha_channel: Union[Literal["envelope"], None, "np.ndarray"] = "envelope",
        gabor_kwargs={},
        image_path: Optional[str] = None,
        position: Tuple[float, float] = (0, 0),
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        rotation: float = 0,
        anchor_x: str = "center",
        anchor_y: str = "center",
        window: Optional["Window"] = None,
        coordinates: Optional[Union["UnitType", "Unit"]] = None,
        **sprite_kwargs,
    ):
        # Generate synthetic Gabor image data (scaled to 0-255)
        data = 255 * gabor_3d(
            size=size,
            spatial_frequency=spatial_frequency,
            orientation=orientation,
            phase=phase,
            sigma=sigma,
            gamma=gamma,
            contrast=contrast,
            center=center,
            cmap=cmap,
            alpha_channel=alpha_channel,
            **gabor_kwargs,
        )
        data = data.astype(int)
        # Initialize the RawImage with the generated data
        super().__init__(
            raw_image=data,
            position=position,
            width=width,
            height=height,
            scale=scale,
            rotation=rotation,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            window=window,
            coordinates=coordinates,
            **sprite_kwargs,
        )
