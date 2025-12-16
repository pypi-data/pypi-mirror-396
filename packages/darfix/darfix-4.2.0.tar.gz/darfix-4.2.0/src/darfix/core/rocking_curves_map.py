from __future__ import annotations

from enum import Enum as _Enum


class Maps_1D(_Enum):
    """Names of the fitting parameters of the 1D fit result. Each result is a map of frame size."""

    AMPLITUDE = "Amplitude"
    FWHM = "FWHM"
    PEAK = "Peak position"
    BACKGROUND = "Background"


class Maps_2D(_Enum):
    """Names of the fitting parameters of the 2D fit result. Each result is a map of frame size."""

    PEAK_X = "Peak position first motor"
    PEAK_Y = "Peak position second motor"
    FWHM_X = "FWHM first motor"
    FWHM_Y = "FWHM second motor"
    AMPLITUDE = "Amplitude"
    CORRELATION = "Correlation"
    BACKGROUND = "Background"


class Maps_3D(_Enum):
    """Names of the fitting parameters of the 3D fit result. Each result is a map of frame size."""

    PEAK_X = "Peak position first motor"
    PEAK_Y = "Peak position second motor"
    PEAK_Z = "Peak position third motor"
    FWHM_X = "FWHM first motor"
    FWHM_Y = "FWHM second motor"
    FWHM_Z = "FWHM third motor"
    CORRELATION_XY = "Cross-correlation between first and second motors"
    CORRELATION_XZ = "Cross-correlation between first and third motors"
    CORRELATION_YZ = "Cross-correlation between second and third motors"
    AMPLITUDE = "Amplitude"
    BACKGROUND = "Background"


MAPS_1D: tuple[Maps_1D] = tuple(member.value for member in Maps_1D)
MAPS_2D: tuple[Maps_2D] = tuple(member.value for member in Maps_2D)
MAPS_3D: tuple[Maps_3D] = tuple(member.value for member in Maps_3D)
