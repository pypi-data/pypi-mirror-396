from __future__ import annotations

import logging
from typing import Callable
from typing import Literal

import numpy
from scipy.optimize import curve_fit

from ..core.rocking_curves_map import MAPS_1D
from ..core.rocking_curves_map import MAPS_2D
from ..core.rocking_curves_map import MAPS_3D
from ..math import bivariate_gaussian
from ..math import compute_com_fwhm
from ..math import gaussian
from ..math import trivariate_gaussian

FitMethod = Literal["trf", "lm", "dogbox"]

_ZERO_SUM_RELATIVE_TOLERANCE = 1e-3
""" Relative tolerance used to check if the sum of values equals 0. Skips fit if it is the case."""

_BOUNDS_TOLERANCE = 1e-3
""" Absolute tolerance for to set bounds of fit parameters. The bounds will be set to (min - tol, max + tol) whenever possible."""

_FWHM_MIN_VALUE = 1e-3
""" FWHM value must be strictly positive in order to have a non-singular covariance matrix with a non-zero determinant"""

_CORRELATION_MAX_VALUE = 0.99
""" Correlation must be strictly inferior to one in order to have a non-singular covariance matrix a non-zero determinant"""

_logger = logging.getLogger(__file__)


def _get_1d_bounds(
    method: FitMethod, x_values: numpy.ndarray, min_y: float, max_y: float
):
    """
    Computes bounds for the curve fit of gaussian.

    :return:

    Tuple (bound min, bound max) with 2d shape (2, 4).

    Bounds contain following parameters (in order):
        - mean
        - fwhm
        - amplitude
        - background
    """
    if method not in ("trf", "dogbox"):
        return (-numpy.inf, numpy.inf)

    min_x0 = numpy.min(x_values)
    max_x0 = numpy.max(x_values)

    return (
        [
            min_y - _BOUNDS_TOLERANCE,
            min_x0 - _BOUNDS_TOLERANCE,
            _FWHM_MIN_VALUE,
            0.0,
        ],
        [
            max_y + _BOUNDS_TOLERANCE,
            max_x0 + _BOUNDS_TOLERANCE,
            numpy.inf,
            min_y + _BOUNDS_TOLERANCE,
        ],
    )


def _get_2d_bounds(
    method: FitMethod, x_values: numpy.ndarray, min_y: float, max_y: float
):
    """
    Computes bounds for the curve fit of bivariate gaussian.

    :return:

    Tuple (bound min, bound max) with 2d shape (2, 7).

    The bounds are for the following parameters (in order):
        - mean_x0
        - mean_x1
        - fwhm_x0
        - fwhm_x1
        - amplitude
        - correlation
        - background
    """
    if method not in ("trf", "dogbox"):
        return (-numpy.inf, numpy.inf)

    min_x0, min_x1 = numpy.min(x_values, axis=1)
    max_x0, max_x1 = numpy.max(x_values, axis=1)

    return (
        [
            min_x0 - _BOUNDS_TOLERANCE,
            min_x1 - _BOUNDS_TOLERANCE,
            _FWHM_MIN_VALUE,
            _FWHM_MIN_VALUE,
            min_y - _BOUNDS_TOLERANCE,
            -_CORRELATION_MAX_VALUE,
            0.0,
        ],
        [
            max_x0 + _BOUNDS_TOLERANCE,
            max_x1 + _BOUNDS_TOLERANCE,
            numpy.inf,
            numpy.inf,
            max_y + _BOUNDS_TOLERANCE,
            _CORRELATION_MAX_VALUE,
            min_y + _BOUNDS_TOLERANCE,
        ],
    )


def _get_3d_bounds(
    method: FitMethod, x_values: numpy.ndarray, min_y: float, max_y: float
):
    """
    Computes bounds for the curve fit of trivariate gaussian.

    :return:

    Tuple (bound min, bound max) with 2d shape (2, 11).

    The bounds are for the following parameters (in order):
        - x0_0
        - x1_0
        - x2_0
        - fwhm_x0
        - fwhm_x1
        - fwhm_x2
        - c10
        - c12
        - c20
        - amplitude
        - background
    """
    if method == "lm":
        # `lm` cannot handle bounds: no point in calculating them
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html#scipy.optimize.least_squares
        return (-numpy.inf, numpy.inf)

    mins = numpy.min(x_values, axis=1) - _BOUNDS_TOLERANCE
    maxs = numpy.max(x_values, axis=1) + _BOUNDS_TOLERANCE

    return (
        [
            mins[0] - _BOUNDS_TOLERANCE,
            mins[1] - _BOUNDS_TOLERANCE,
            mins[2] - _BOUNDS_TOLERANCE,
            _FWHM_MIN_VALUE,
            _FWHM_MIN_VALUE,
            _FWHM_MIN_VALUE,
            -_CORRELATION_MAX_VALUE,
            -_CORRELATION_MAX_VALUE,
            -_CORRELATION_MAX_VALUE,
            min_y - _BOUNDS_TOLERANCE,
            0.0,
        ],
        [
            maxs[0] + _BOUNDS_TOLERANCE,
            maxs[1] + _BOUNDS_TOLERANCE,
            maxs[2] + _BOUNDS_TOLERANCE,
            numpy.inf,
            numpy.inf,
            numpy.inf,
            _CORRELATION_MAX_VALUE,
            _CORRELATION_MAX_VALUE,
            _CORRELATION_MAX_VALUE,
            max_y + _BOUNDS_TOLERANCE,
            min_y + _BOUNDS_TOLERANCE,
        ],
    )


def _trivariate_gaussian_p0(com: list[float], fwhm: list[float], ptp_y: float):
    """
    Computes p0 for the curve fit of trivariate gaussian.

    p0 contains following parameters (in order):
        - x0_0
        - x1_0
        - x2_0
        - fwhm_x0
        - fwhm_x1
        - fwhm_x2
        - c10
        - c12
        - c20
        - amplitude
        - background
    """
    return [
        *com,
        *fwhm,
        0.0,
        0.0,
        0.0,
        ptp_y,
        0.0,
    ]


def _bivariate_gaussian_p0(com: list[float], fwhm: list[float], ptp_y: float):
    """
    Computes p0 for the curve fit of bivariate gaussian.

    p0 contains following parameters (in order):
        - mean_x0
        - mean_x1
        - fwhm_x0
        - fwhm_x1
        - amplitude
        - coorelation
        - background
    """
    return [
        *com,
        *fwhm,
        ptp_y,
        0.0,
        0.0,
    ]


def _gaussian_p0(com: list[float], fwhm: list[float], ptp_y: float):
    """
    Computes p0 for the curve fit of gaussian.

    p0 contains following parameters (in order):
        - mean
        - fwhm
        - amplitude
        - background
    """
    return [
        ptp_y,
        *com,
        *fwhm,
        0.0,
    ]


def _fit_xd_rocking_curve(
    len_maps: int,
    gaussian_function: Callable,
    p0_function: Callable[[list[float], list[float], float], list],
    bounds_function: Callable[[FitMethod, numpy.ndarray, float, float], numpy.ndarray],
    y_values: numpy.ndarray,
    x_values: numpy.ndarray,
    method: FitMethod | None,
    thresh: float | None,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    :param  len_maps: len of the returned maps array
    :param  gaussian_function: the callable model function f used in `scipy.optimize.curve_fit`
    :param  p0_function: the callable used to define p0 vector
    :param  bounds_function: the callable used to the bounds in case of 'trf' or 'dogbox' method
    :param  y_values: 1D array: N points (uint16)
    :param  x_values: 2D array: K dimensions, N points (float64)

    :return: Tuple with:
    - the fitted gaussian : 1D array of N points (float64)
    - fit parameters :  1D array of length len_maps
    """
    if method is None:
        method = "trf"
    if thresh is None:
        thresh = 15.0

    com, fwhm = compute_com_fwhm(x_values, y_values)

    ptp_y = numpy.ptp(y_values)

    fitted_y = numpy.zeros_like(y_values)
    y_not_zero_mask = y_values > 0

    if ptp_y <= thresh:
        # Ptp under threshold
        return fitted_y, numpy.full(len_maps, numpy.nan)

    if len(y_values) < len_maps:
        return fitted_y, numpy.full(len_maps, numpy.nan)

    ptp_y = numpy.ptp(y_values)

    p0 = p0_function(com, fwhm, ptp_y)

    vmax = max(y_values.max(), ptp_y)

    bounds = bounds_function(
        method,
        x_values,
        min_y=thresh,
        max_y=vmax,
    )

    x_values_masked = x_values[:, y_not_zero_mask]

    try:
        fit_params, cov = curve_fit(
            f=gaussian_function,
            xdata=x_values_masked,
            ydata=y_values[y_not_zero_mask],
            p0=p0,
            method=method,
            bounds=bounds,
        )
    except (RuntimeError, ValueError) as e:
        _logger.info(
            f"Encountered the following error while fitting rocking curves: '{e}'"
        )
        _logger.debug(f"p0 : \n{p0}\nbounds : \n{bounds}")
        return fitted_y, numpy.full(len_maps, numpy.nan)

    fitted_y[y_not_zero_mask] = gaussian_function(x_values_masked, *fit_params)

    return fitted_y, fit_params


def fit_1d_rocking_curve(
    y_values: numpy.ndarray,
    x_values: numpy.ndarray,
    method: FitMethod | None = None,
    thresh: float | None = 15.0,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    :param  y_values: 1D array N uint16
    :param  x_values: 1D array of N float64

    :return: Tuple with:
    - the fitted gaussian : 1D array of float64
    - fit parameters :  1D array of length len(MAPS_1D)
    """
    # _fit_xd_rocking_curve expect array with shape (N_dims, N_points)
    x_values = x_values[numpy.newaxis, :]

    def _gaussian(x, *args):
        # gaussian() x with n dims == 1
        return gaussian(x[0], *args)

    return _fit_xd_rocking_curve(
        len(MAPS_1D),
        _gaussian,
        _gaussian_p0,
        _get_1d_bounds,
        y_values,
        x_values,
        method,
        thresh,
    )


def fit_2d_rocking_curve(
    y_values: numpy.ndarray,
    x_values: numpy.ndarray,
    method: FitMethod | None = None,
    thresh: float | None = 15.0,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    :param y_values: 1D array of N uint16
    :param x_values: 2D array (2,N) of float64

    :return: Tuple with:
    - the fitted gaussian : 1D array of N float64
    - fit parameters :  1D array of length len(MAPS_2D)
    """
    return _fit_xd_rocking_curve(
        len(MAPS_2D),
        bivariate_gaussian,
        _bivariate_gaussian_p0,
        _get_2d_bounds,
        y_values,
        x_values,
        method,
        thresh,
    )


def fit_3d_rocking_curve(
    y_values: numpy.ndarray,
    x_values: numpy.ndarray,
    method: FitMethod | None = None,
    thresh: float | None = 15.0,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    :param  y_values: 1D array of N uint16
    :param  x_values: 2D array (3,N) of float64

    Return: Tuple with:
    - the fitted gaussian : 1D array of N float64
    - fit parameters :  1D array of length len(MAPS_3D)
    """
    return _fit_xd_rocking_curve(
        len(MAPS_3D),
        trivariate_gaussian,
        _trivariate_gaussian_p0,
        _get_3d_bounds,
        y_values,
        x_values,
        method,
        thresh,
    )
