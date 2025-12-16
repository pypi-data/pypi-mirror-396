from typing import Tuple, Optional, Union, Literal, Callable

try:
    import numpy as np
except ImportError:
    raise ImportError(
        "The 'numpy' package is required to use the 'synthetic' stimuli module. "
        "You can install it using 'pip install numpy'."
    )

from ..utils import Color
from ..types import ColorType

__all__ = ["gabor_2d", "gabor_3d", "reescale"]

def reescale(
    arr: "np.ndarray",
    vmin: float = -1.0,
    vmax: float = 1.0,
    method: Literal["normalize", "clip"] = "normalize",
) -> "np.ndarray":
    """
    Rescale a numpy array based on the specified method.

    Parameters
    ----------
    arr : np.ndarray
        Input array to be rescaled.
    vmin : float, optional
        Minimum value for normalization or clipping (default is -1.0).
    vmax : float, optional
        Maximum value for normalization or clipping (default is 1.0).
    method : Literal["none", "normalize", "clip"], optional
        Rescaling method:
            - 'none': return the array as is.
            - 'normalize': scale the array so its min maps to vmin and max to vmax.
            - 'clip': clip the array values to lie between vmin and vmax.

    Returns
    -------
    np.ndarray
        The rescaled array.
    """
    if method == "normalize":
        arr_min, arr_max = arr.min(), arr.max()
        if np.isclose(arr_min, arr_max):
            return np.full_like(arr, (vmin + vmax) / 2.0)
        return (arr - arr_min) / (arr_max - arr_min) * (vmax - vmin) + vmin
    elif method == "clip":
        return np.clip(arr, vmin, vmax)
    else:
        raise ValueError("Method must be one of 'normalize', or 'clip'")


def gabor_2d(
    size: Tuple[int, int] = (128, 128),
    spatial_frequency: float = 5.0,  # cycles per image width
    orientation: float = 45.0,  # in degrees, [0..360]
    phase: float = 0.0,  # fraction of 2*pi in [0..1]
    sigma: Optional[
        float
    ] = 0.25,  # normalized (fraction of min dimension); if None, no envelope is applied.
    gamma: float = 1.0,  # aspect ratio (vertical stretch)
    contrast: float = 1.0,
    baseline: float = 0.0,
    center: Optional[Tuple[float, float]] = None,
    rescale: Optional[
        Literal["none", "normalize", "clip"]
    ] = None,  # 'none', 'normalize', or 'clip'
    vmin: float = 0.0,
    vmax: float = 1.0,
    return_envelope: bool = False,
) -> Union["np.ndarray", Tuple["np.ndarray", "np.ndarray"]]:
    """
    Generate a 2D Gabor patch as a numpy array (grayscale), with an optional Gaussian envelope.

    Parameters
    ----------
    size : Tuple[int, int]
        (height, width) of the output array in pixels.
    spatial_frequency : float
        Cycles per entire image width. For orientation=0, this yields exactly
        `spatial_frequency` cycles from left to right.
    orientation : float
        Gabor orientation in degrees, [0..360]. Note: The function rotates the carrier
        by (360 - orientation) degrees.
    phase : float
        Fraction of 2*pi for the carrier phase, in [0..1].
    sigma : Optional[float]
        Standard deviation of the Gaussian envelope, as a fraction of the minimum dimension.
        If None, no envelope is applied (i.e., the envelope is 1 everywhere).
    gamma : float
        Aspect ratio of the Gaussian envelope (width vs. height). If 1.0, the envelope is circular;
        values < 1 or > 1 yield an elliptical envelope.
    contrast : float
        Contrast (amplitude) of the sinusoidal carrier.
    baseline : float
        Baseline offset intensity added to the Gabor.
    center : Optional[Tuple[float, float]]
        (y_center, x_center) specifying the center in pixel coordinates.
        If None, defaults to the image center ((h/2), (w/2)).
    rescale : Literal["none", "normalize", "clip"]
        Rescaling method:
            - 'none': return the raw computed values.
            - 'normalize': linearly scale the array so that its min maps to vmin and max to vmax.
            - 'clip': clip values to the range [vmin, vmax].
    vmin : float
        Minimum value for normalization or clipping. Ignored if rescale=='none'.
    vmax : float
        Maximum value for normalization or clipping. Ignored if rescale=='none'.
    return_envelope : bool
        If True, return a tuple (gabor, envelope), where envelope is the Gaussian envelope
        used (useful for an alpha channel). If sigma is None, envelope is an array of ones.

    Returns
    -------
    Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]
        If return_envelope is False, returns a 2D array containing the Gabor pattern.
        Otherwise, returns a tuple: (gabor, envelope).

    Example
    -------
    >>> import matplotlib.pyplot as plt
    >>> gabor, env = gabor_2d(size=(256, 256), spatial_frequency=2.0, orientation=45.0,
    ...                       phase=0.25, sigma=0.25, gamma=1.0, contrast=1.0,
    ...                       baseline=0.0, rescale='normalize', vmin=-1.0, vmax=1.0,
    ...                       return_envelope=True)
    >>> plt.figure(figsize=(10, 5))
    >>> plt.subplot(1, 2, 1)
    >>> plt.imshow(gabor, cmap='gray', origin='lower')
    >>> plt.title("Gabor Patch")
    >>> plt.subplot(1, 2, 2)
    >>> plt.imshow(env, cmap='gray', origin='lower')
    >>> plt.title("Envelope (Alpha Channel)")
    >>> plt.show()
    """
    h, w = size

    # Convert orientation and phase to radians.
    # Using (360 - orientation) rotates the carrier in the expected direction.
    theta = np.deg2rad(360 - orientation)
    phase_rad = 2.0 * np.pi * phase

    # Default center is the midpoint of the array
    if center is None:
        center = (h / 2.0, w / 2.0)
    cy, cx = center

    # Create grid of coordinates
    y_idx = np.arange(h) - cy
    x_idx = np.arange(w) - cx
    y_mesh, x_mesh = np.meshgrid(y_idx, x_idx, indexing="xy")

    # Rotate coordinate system
    x_prime = x_mesh * np.cos(theta) + y_mesh * np.sin(theta)
    y_prime = -x_mesh * np.sin(theta) + y_mesh * np.cos(theta)

    # Convert spatial frequency from cycles/image width to cycles/pixel
    freq_px = spatial_frequency / float(w)

    # Compute the sinusoidal carrier
    carrier = np.cos(2.0 * np.pi * freq_px * x_prime + phase_rad)

    # Compute the envelope if sigma is provided; otherwise, use ones
    if sigma is not None:
        sigma_px = sigma * min(h, w)
        envelope = np.exp(-0.5 * (x_prime**2 + (gamma * y_prime) ** 2) / (sigma_px**2))
        gabor = contrast * envelope * carrier + baseline
    else:
        envelope = np.ones_like(carrier)
        gabor = contrast * carrier + baseline

    # Apply rescaling if needed
    if rescale:
        gabor = reescale(gabor, vmin, vmax, method=rescale)

    if return_envelope:
        return gabor, envelope
    return gabor


def gabor_3d(
    size: Tuple[int, int] = (256, 256),
    spatial_frequency: float = 8.0,  # cycles per image width
    orientation: float = 45.0,  # in degrees, [0..360]
    phase: float = 0.0,  # fraction of 2*pi in [0..1]
    sigma: Optional[
        float
    ] = 0.15,  # normalized (fraction of min dimension); if None, no envelope is applied.
    gamma: float = 1.0,  # aspect ratio (vertical stretch)
    contrast: float = 1.0,
    center: Optional[Tuple[float, float]] = None,
    cmap: Union[str, Callable[[np.ndarray], np.ndarray], Tuple[ColorType, ColorType], list] = (
        "black",
        "white",
    ),
    # alpha_channel can be "envelope", None, or a numpy array with shape matching the 2D gabor.
    alpha_channel: Union[Literal["envelope"], None, np.ndarray] = "envelope",
    **kwargs,  # additional kwargs passed to gabor_2d (e.g., baseline, rescale, etc.)
) -> np.ndarray:
    """
    Generate a 3D (color) Gabor patch as a numpy array by mapping a grayscale 2D Gabor
    (computed via gabor_2d) into RGB values using a colormap. An optional alpha channel
    may be included.

    Parameters
    ----------
    size : Tuple[int, int]
        (height, width) of the output image in pixels.
    spatial_frequency : float
        Cycles per entire image width.
    orientation : float
        Gabor orientation in degrees, [0..360].
    phase : float
        Fraction of 2*pi for the carrier phase, in [0..1].
    sigma : Optional[float]
        Standard deviation of the Gaussian envelope as a fraction of the minimum dimension.
        If None, no envelope is applied (envelope defaults to ones).
    gamma : float
        Aspect ratio of the Gaussian envelope.
    contrast : float
        Contrast (amplitude) of the sinusoidal carrier.
    center : Optional[Tuple[float, float]]
        Center (y, x) in pixel coordinates. Defaults to image center if None.
    cmap : Union[str, Callable[[np.ndarray], np.ndarray], Tuple[ColorType, ColorType], list]
        Colormap used to map normalized grayscale values to colors. If a string,
        it must be a valid matplotlib colormap name. Alternatively, a callable
        mapping an array in [0,1] to an RGBA image, or a tuple/list of two colors
        (low and high) for linear two-color interpolation.
    alpha_channel : Union[Literal["envelope"], None, np.ndarray]
        Determines the alpha channel:
            - "envelope": use the Gaussian envelope computed in gabor_2d.
            - None: do not include an alpha channel (output will be RGB).
            - A numpy array: must have the same shape as the 2D gabor; used as the alpha channel.
    **kwargs
        Additional keyword arguments passed to gabor_2d (e.g., baseline, rescale).

    Returns
    -------
    np.ndarray
        If an alpha channel is provided, returns an RGBA image (height x width x 4);
        otherwise, returns an RGB image (height x width x 3).

    Example
    -------
    >>> import matplotlib.pyplot as plt
    >>> # Using a matplotlib colormap:
    >>> gabor_color = gabor_3d(size=(256, 256), spatial_frequency=2.0, orientation=45.0,
    ...                        phase=0.25, sigma=0.25, gamma=1.0, contrast=1.0,
    ...                        cmap='viridis', alpha_channel="envelope",
    ...                        baseline=0.0, rescale='normalize', vmin=0.0, vmax=1.0)
    >>> plt.imshow(gabor_color, origin='lower')
    >>> plt.title("3D Gabor Patch with Envelope as Alpha")
    >>> plt.show()
    >>> # Using two-color interpolation:
    >>> gabor_color2 = gabor_3d(size=(256, 256), spatial_frequency=2.0, orientation=45.0,
    ...                         phase=0.25, sigma=0.25, gamma=1.0, contrast=1.0,
    ...                         cmap=('black', 'white'), alpha_channel="envelope")
    >>> plt.imshow(gabor_color2, origin='lower')
    >>> plt.title("3D Gabor Patch (Black-to-White)")
    >>> plt.show()
    """
    # Obtain 2D grayscale Gabor and envelope via gabor_2d (pass extra kwargs if needed)
    gabor_gray, envelope = gabor_2d(
        size=size,
        spatial_frequency=spatial_frequency,
        orientation=orientation,
        phase=phase,
        sigma=sigma,
        gamma=gamma,
        contrast=contrast,
        center=center,
        return_envelope=True,
        **kwargs,
    )

    # Normalize the grayscale image to [0,1] for color mapping
    if np.isclose(gabor_gray.min(), gabor_gray.max()):
        norm_gray = np.full_like(gabor_gray, 0.5)
    else:
        norm_gray = (gabor_gray - gabor_gray.min()) / (gabor_gray.max() - gabor_gray.min())

    # Reapply contrast after normalization.
    if contrast != 1.0:
        norm_gray = 0.5 + contrast * (norm_gray - 0.5)

    # Map normalized grayscale values to color (RGBA)
    if isinstance(cmap, str):
        try:
            from matplotlib.pyplot import get_cmap
        except ImportError:
            raise ImportError(
                "The 'matplotlib' package is required to use a colormap string. "
                "You can install it using 'pip install matplotlib'."
            )
        cmap_func = get_cmap(cmap)
        colored = cmap_func(norm_gray)  # returns an RGBA image (h, w, 4)
    elif callable(cmap):
        colored = cmap(norm_gray)
        # If the callable returns RGB only, add an alpha channel of ones
        if colored.shape[2] == 3:
            colored = np.dstack([colored, np.ones_like(colored[..., 0])])
    elif isinstance(cmap, (tuple, list)) and len(cmap) == 2:
        # Two-color interpolation: parse each color via Color().to_rgb()
        col1 = np.array(Color(cmap[0]).to_rgb())
        col2 = np.array(Color(cmap[1]).to_rgb())
        # Interpolate: for each pixel, color = (1 - v)*col1 + v*col2
        # norm_gray has shape (h, w); reshape for broadcasting.
        colored_rgb = (1 - norm_gray[..., None]) * col1 + norm_gray[..., None] * col2
        # Add alpha channel of ones (will be replaced if requested)
        colored = np.dstack([colored_rgb, np.ones_like(norm_gray)])
    else:
        raise ValueError(
            "cmap must be a valid colormap string, callable, or a tuple/list of two colors."
        )

    # Adjust the alpha channel as specified
    if alpha_channel == "envelope":
        colored[..., 3] = envelope  # override the alpha channel with the envelope
    elif alpha_channel is None:
        colored = colored[..., :3]  # drop alpha channel
    elif isinstance(alpha_channel, np.ndarray):
        if alpha_channel.shape != gabor_gray.shape:
            raise ValueError(
                "Provided alpha_channel array must match the shape of the gabor image."
            )
        colored[..., 3] = alpha_channel
    else:
        raise ValueError("alpha_channel must be 'envelope', None, or a numpy array.")

    return colored
