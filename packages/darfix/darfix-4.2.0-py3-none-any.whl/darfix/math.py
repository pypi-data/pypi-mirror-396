from __future__ import annotations

from typing import Tuple

import numba
import numpy

from darfix._config import FWHM_VAL

Vector3D = Tuple[float, float, float]


@numba.njit(cache=True, fastmath=True, error_model="numpy")
def compute_com_fwhm(
    x: numpy.ndarray, y: numpy.ndarray
) -> tuple[numpy.ndarray, numpy.ndarray]:
    com = numpy.empty(len(x))
    fwhm = numpy.empty(len(x))
    for i in range(len(x)):
        sum_y = numpy.sum(y)
        com[i] = numpy.sum(x[i] * y) / sum_y
        var = numpy.sum((x[i] - com[i]) ** 2 * y) / sum_y
        fwhm[i] = numpy.sqrt(var) * FWHM_VAL
    return com, fwhm


@numba.njit(cache=True, fastmath=True, error_model="numpy")
def gaussian(
    x: numpy.ndarray, amplitude: float, x0: float, fwhm: float, background: float
):
    """
    Gaussian function (https://en.wikipedia.org/wiki/Gaussian_function) with background

    :param x: value where to evaluate
    :param amplitude: peak height
    :param x0: peak center
    :param std_dev: standard deviation
    :param background: lowest value of the curve (value of the limits)

    :returns: result of the function on x
    :rtype: float
    """
    return background + amplitude * numpy.exp(
        -numpy.power(x - x0, 2) / (2 * numpy.power(fwhm / FWHM_VAL, 2))
    )


@numba.njit(cache=True, fastmath=True, error_model="numpy")
def bivariate_gaussian(
    X: numpy.ndarray,
    x0_0: float,
    x1_0: float,
    fwhm_x0: float,
    fwhm_x1: float,
    amplitude: float,
    correlation: float = 0,
    background: float = 0,
):
    """
    Bivariate case of the gaussian function with background (https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Bivariate_case)

    If correlation is set to 0 (default), this is simply a 2D gaussian

    :param x: value where to evaluate
    """
    x0, x1 = X
    sigma_x0 = fwhm_x0 / FWHM_VAL
    sigma_x1 = fwhm_x1 / FWHM_VAL
    return background + amplitude * numpy.exp(
        -0.5
        / (1 - correlation**2)
        * (
            ((x0 - x0_0) / sigma_x0) ** 2
            + ((x1 - x1_0) / sigma_x1) ** 2
            - 2 * correlation * (x0 - x0_0) * (x1 - x1_0) / sigma_x0 / sigma_x1
        )
    )


@numba.njit(cache=True, fastmath=True, error_model="numpy")
def trivariate_gaussian(
    X: numpy.ndarray,
    x0_0: float,
    x1_0: float,
    x2_0: float,
    fwhm_x0: float,
    fwhm_x1: float,
    fwhm_x2: float,
    c10: float,
    c12: float,
    c20: float,
    amplitude: float,
    background: float = 0,
):
    """
    Trivariate case of the gaussian function with background (https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Density_function)

    :param X: stack of N vectors of shape (3, N)
    :param x0_0: mean along axis 0
    :param x1_0: mean along axis 1
    :param x2_0: mean along axis 2
    :param fwhm_x0: standard deviation along axis 0
    :param fwhm_x1: standard deviation along axis 1
    :param fwhm_x2: standard deviation along axis 2
    :param c10: cross-correlation factor between axis 0 and axis 1
    :param c12: cross-correlation factor between axis 1 and axis 2
    :param c02: cross-correlation factor between axis 0 and axis 2
    :param amplitude:
    :param background:
    """
    N = X.shape[1]
    Y = numpy.empty(N)

    sigma_x0 = fwhm_x0 / FWHM_VAL
    sigma_x1 = fwhm_x1 / FWHM_VAL
    sigma_x2 = fwhm_x2 / FWHM_VAL

    covariance_matrix = numpy.array(
        [
            [sigma_x0**2, c10 * sigma_x0 * sigma_x1, c20 * sigma_x0 * sigma_x2],
            [c10 * sigma_x0 * sigma_x1, sigma_x1**2, c12 * sigma_x1 * sigma_x2],
            [c20 * sigma_x0 * sigma_x2, c12 * sigma_x1 * sigma_x2, sigma_x2**2],
        ]
    )

    inv = numpy.linalg.inv(covariance_matrix)

    # Compute Gaussian for each point
    for i in range(N):
        dx0 = X[0, i] - x0_0
        dx1 = X[1, i] - x1_0
        dx2 = X[2, i] - x2_0
        # Quadratic form: (X-mu)^T Σ^-1 (X-mu)
        exponent = (
            dx0 * (inv[0, 0] * dx0 + inv[0, 1] * dx1 + inv[0, 2] * dx2)
            + dx1 * (inv[1, 0] * dx0 + inv[1, 1] * dx1 + inv[1, 2] * dx2)
            + dx2 * (inv[2, 0] * dx0 + inv[2, 1] * dx1 + inv[2, 2] * dx2)
        )
        Y[i] = amplitude * numpy.exp(-0.5 * exponent) + background

    return Y
