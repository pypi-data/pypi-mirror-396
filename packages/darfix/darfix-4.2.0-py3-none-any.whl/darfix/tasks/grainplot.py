from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Literal

import numpy
from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from silx.io.dictdump import dicttonx
from silx.math.combo import min_max

from darfix import dtypes
from darfix.core.moment_types import MomentType

from ..core.grainplot import DimensionRange
from ..core.grainplot import GrainPlotMaps
from ..core.grainplot import OrientationDistData
from ..core.grainplot import compute_mosaicity
from ..core.grainplot import generate_grain_maps_nxdict

_logger = logging.getLogger(__file__)


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: dtypes.Dataset
    """ Input dataset containing a stack of images """
    dimensions: tuple[int, int] = (0, 1)
    """Dimension indices to use for the maps. Default is (0, 1), which means the two first dimensions."""
    range: tuple[DimensionRange | None, DimensionRange | None] = (None, None)
    """Dimensionrange for the two dimensions. If None, use the Center of Mass min and max for the both dimensions."""
    save_maps: bool = True
    """Whether to save the maps to file. Default is True."""
    filename: str | MissingData = MISSING_DATA
    """Only used if save_maps is True. Filename to save the maps to. Default is 'maps.h5' in the dataset directory."""
    orientation_img_origin: Literal["dims", "center"] = "dims"
    "Origin for the orientation distribution image. Can be 'dims', 'center' or None. Default is 'dims'."


class GrainPlot(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    """Generates and saves maps of Center of Mass, FWHM, Skewness, Kurtosis, Orientation distribution and Mosaicity."""

    def run(self):

        inputs = Inputs(**self.get_input_values())

        default_filename = os.path.join(inputs.dataset.dataset._dir, "maps.h5")
        filename: str = self.get_input_value("filename", default_filename)

        moments = inputs.dataset.dataset.apply_moments()
        grainPlotMaps = GrainPlotMaps.from_dataset(inputs.dataset)

        # mosaicity and orientation can only be computed for 2D+ datasets
        if grainPlotMaps.dims.ndim > 1 and inputs.save_maps:
            dimension1, dimension2 = inputs.dimensions
            dimension1_range, dimension2_range = inputs.range

            if dimension1_range is None:
                dimension1_range = _computeMinMax(moments[dimension1][MomentType.COM])
            if dimension2_range is None:
                dimension2_range = _computeMinMax(moments[dimension2][MomentType.COM])

            mosaicity = compute_mosaicity(
                moments,
                x_dimension=dimension1,
                y_dimension=dimension2,
                x_dimension_range=dimension1_range,
                y_dimension_range=dimension2_range,
            )

            orientation_dist_data = OrientationDistData(
                grainPlotMaps,
                x_dimension=dimension1,
                y_dimension=dimension2,
                x_dimension_range=dimension1_range,
                y_dimension_range=dimension2_range,
            )
            assert orientation_dist_data is not None
        else:
            orientation_dist_data = None
            mosaicity = None

        # Save data if asked
        if inputs.save_maps:
            nxdict = generate_grain_maps_nxdict(
                grainPlotMaps, mosaicity, orientation_dist_data
            )
            os.makedirs(Path(filename).parent, exist_ok=True)
            dicttonx(nxdict, filename)

        self.outputs.dataset = inputs.dataset


def _computeMinMax(array: numpy.ndarray) -> DimensionRange:
    min_max_result = min_max(array)
    return min_max_result.minimum, min_max_result.maximum
