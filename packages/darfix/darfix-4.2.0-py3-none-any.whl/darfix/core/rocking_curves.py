from __future__ import annotations

from typing import Sequence

import numpy
import tqdm
from joblib import Parallel
from joblib import delayed

from ..io.utils import create_nxdata_dict
from ..processing.rocking_curves import FitMethod
from ..processing.rocking_curves import fit_1d_rocking_curve
from ..processing.rocking_curves import fit_2d_rocking_curve
from ..processing.rocking_curves import fit_3d_rocking_curve
from .rocking_curves_map import MAPS_1D
from .rocking_curves_map import MAPS_2D
from .rocking_curves_map import MAPS_3D
from .rocking_curves_map import Maps_1D
from .utils import NoDimensionsError
from .utils import TooManyDimensionsForRockingCurvesError


def _rocking_curves_per_px(data: numpy.ndarray):
    """
    Generator that returns the rocking curve for every pixel

    :param ndarray data: data to analyse
    """
    for j in range(data.shape[1]):
        for i in range(data.shape[2]):
            yield data[:, j, i]


def _wrap_fit_function(fit_function, motor_values, thresh, method, curve_per_px):
    """
    Just a wrapper to pack the result of the fit.

    See `_fit_xd_data` for parameters details and typing
    """

    y_gauss, fit_result = fit_function(curve_per_px, motor_values, method, thresh)

    return y_gauss, fit_result


def fit_rocking_curve_parallel(
    data: numpy.ndarray,
    motor_values: Sequence[numpy.ndarray] | numpy.ndarray,
    thresh: float | None,
    method: FitMethod | None,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    Fit the rocking curves using multiprocessing.

    :param data: 3D data [N frames, height, width] array to fit.
    :param motor_values: x values associated to axis 0 of the 3D data. Can be 2D [dims count, N frames] or 1D [N frames]
    :param thresh: Optional threshold value for each rocking curve. If Peak-to-peak value is nelow this threshold, data is not fitted.
    :param method: Method to use in `scipy.optimize.curve_fit`.

    :return:
    - Fitted 3D data array [N frames, height, width]
    - A [len_maps, height, width] 3D array of the fit parameters.
    """

    motor_values = numpy.asarray(motor_values, numpy.float64)
    height, width = data.shape[-2:]

    if motor_values.ndim == 1:
        fit_function = fit_1d_rocking_curve
        len_maps = len(MAPS_1D)
    elif motor_values.ndim == 2 and motor_values.shape[0] == 2:
        fit_function = fit_2d_rocking_curve
        len_maps = len(MAPS_2D)
    elif motor_values.ndim == 2 and motor_values.shape[0] == 3:
        fit_function = fit_3d_rocking_curve
        len_maps = len(MAPS_3D)
    else:
        raise ValueError(f"motor_values has a bad shape : {motor_values.shape}")

    output_data = numpy.zeros_like(data)
    maps = numpy.full((len_maps,) + data.shape[-2:], numpy.nan)

    with Parallel(n_jobs=-1, return_as="generator") as parallel_processing:
        results = parallel_processing(
            delayed(_wrap_fit_function)(
                fit_function, motor_values, thresh, method, curve
            )
            for curve in _rocking_curves_per_px(data)
        )

        for idx, (y_gauss, maps_ji) in tqdm.tqdm(
            enumerate(results), desc="Fit rocking curves", total=height * width
        ):
            j = idx // data.shape[2]
            i = idx % data.shape[2]
            output_data[:, j, i] = y_gauss
            maps[:, j, i] = maps_ji

    return output_data, maps


def generate_rocking_curves_nxdict(
    dataset,  # ImageDataset. Cannot type due to circular import
    maps: numpy.ndarray,
    residuals: numpy.ndarray | None,
) -> dict:
    if not dataset.dims.ndim:
        raise NoDimensionsError("generate_rocking_curves_nxdict")
    entry = "entry"

    nx = {
        entry: {"@NX_class": "NXentry"},
        "@NX_class": "NXroot",
        "@default": entry,
    }

    if dataset.transformation:
        axes = [
            dataset.transformation.yregular,
            dataset.transformation.xregular,
        ]
        axes_names = ["y", "x"]
        axes_long_names = [
            dataset.transformation.label,
            dataset.transformation.label,
        ]
    else:
        axes = None
        axes_names = None
        axes_long_names = None

    if dataset.dims.ndim == 1:
        map_names = MAPS_1D
    elif dataset.dims.ndim == 2:
        map_names = MAPS_2D
    elif dataset.dims.ndim == 3:
        map_names = MAPS_3D
    else:
        raise TooManyDimensionsForRockingCurvesError()

    for i, map_name in enumerate(map_names):
        signal = maps[i]
        nx[entry][map_name] = create_nxdata_dict(
            signal, map_name, axes, axes_names, axes_long_names
        )
    if residuals is not None:
        nx[entry]["Residuals"] = create_nxdata_dict(
            residuals, "Residuals", axes, axes_names, axes_long_names
        )
    nx[entry]["@default"] = Maps_1D.AMPLITUDE.value

    return nx


def compute_residuals(
    target_dataset,  # ImageDataset. Cannot type due to circular import
    original_dataset,  # ImageDataset. Cannot type due to circular import
    indices: numpy.ndarray | None,
):
    return numpy.sqrt(
        (
            numpy.subtract(
                target_dataset.as_array3d(indices),
                original_dataset.as_array3d(indices),
            )
            ** 2
        ).sum(axis=(0))
    )
