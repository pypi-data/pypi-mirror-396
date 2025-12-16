FWHM_VAL = 2.35482  # For numba


class Config:
    """
    Class containing shared global configuration for the darfix project.

    .. versionadded:: 0.3
    """

    DEFAULT_COLORMAP_NAME = "cividis"
    DEFAULT_COLORMAP_NORM = "linear"
    """Default LUT for the plot widgets.

    The available list of names are available in the module
    :module:`silx.gui.colors`.

    .. versionadded:: 0.3
    """

    FWHM_VAL = FWHM_VAL

    """Magic value that returns FWHM when multiplied by the standard deviation.

    .. versionadded:: 0.5
    """
