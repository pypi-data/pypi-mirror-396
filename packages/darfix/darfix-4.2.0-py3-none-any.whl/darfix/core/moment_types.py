from __future__ import annotations

from enum import Enum


class MomentType(Enum):
    COM = "Center of mass"
    FWHM = "FWHM"
    SKEWNESS = "Skewness"
    KURTOSIS = "Kurtosis"
