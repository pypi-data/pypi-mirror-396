from __future__ import annotations

from enum import Enum as _Enum

import numpy
import silx.math
from numba import njit
from numba import prange


class Method(_Enum):
    """
    Methods available to compute the background.
    """

    MEDIAN = "median"
    MEAN = "mean"


def compute_background(
    bg_frames: numpy.ndarray,
    method: str | Method,
) -> numpy.ndarray:
    """Compute a background image from a stack of frames"""
    method = Method(method)
    if method is Method.MEAN:
        bg = fast_mean_3D_to_2D(bg_frames)
        bg = bg.astype(bg_frames.dtype)
    elif method is Method.MEDIAN:
        bg = fast_median_3D_to_2D(bg_frames)
    else:
        raise NotImplementedError(f"method {method.value} not Implemented yet")

    return bg


@njit(parallel=True, error_model="numpy", cache=True)
def fast_median_3D_to_2D(input_array: numpy.ndarray) -> numpy.ndarray:
    """Compute the median of a 3-D array **along axis 0** using a Numba-accelerated implementation."""

    result = numpy.empty(input_array.shape[1:], input_array.dtype)
    for j in prange(input_array.shape[1]):
        for i in range(input_array.shape[2]):
            result[j, i] = numpy.median(input_array[:, j, i])
    return result


@njit(parallel=True, error_model="numpy", cache=True)
def fast_mean_3D_to_2D(input_array: numpy.ndarray) -> numpy.ndarray:
    """Compute the mean of a 3-D array **along axis 0** using a Numba-accelerated implementation."""

    result = numpy.empty(input_array.shape[1:], input_array.dtype)
    for j in prange(input_array.shape[1]):
        for i in prange(input_array.shape[2]):
            result[j, i] = numpy.mean(input_array[:, j, i])
    return result


def background_subtraction(img: numpy.ndarray, bg: numpy.ndarray) -> None:
    """
    Compute background subtraction.

    :param array_like img: Raw image
    :param array_like bg: Background image

    :return: Image with subtracted background
    """
    # Substract and replace negative value by zero
    img[img < bg] = 0
    numpy.subtract(img, bg, out=img, where=(img > 0))


def hot_pixel_removal(image: numpy.ndarray, ksize: int = 3) -> None:
    """
    Function to remove hot pixels of the data using median filter.

    :param data: Input data.
    :param ksize: Size of the mask to apply.
    """
    median = silx.math.medfilt(numpy.ascontiguousarray(image), ksize)
    if numpy.issubdtype(image.dtype, numpy.integer):
        subtracted_image = numpy.subtract(image, median, dtype=numpy.int32)
    else:
        subtracted_image = numpy.subtract(image, median)
    threshold = numpy.std(subtracted_image)
    hot_pixels = subtracted_image > threshold
    image[hot_pixels] = median[hot_pixels]


def threshold_removal(
    data: numpy.ndarray, bottom: int | None = None, top: int | None = None
) -> None:
    """
    Set bottom and top threshold to the images in the dataset.

    :param array_like data: Input data
    :param int bottom: Bottom threshold
    :param int top: Top threshold
    :returns: ndarray
    """

    if bottom is not None:
        data[data < bottom] = 0
    if top is not None:
        data[data > top] = 0


def mask_removal(data: numpy.ndarray, mask: numpy.ndarray) -> None:
    """
    Set 0 values of mask to 0.

    :param array_like data: Input data
    :param nd.array mask: Input mask.

    :returns: ndarray with the masked values
    """
    numpy.multiply(data, mask, out=data)
