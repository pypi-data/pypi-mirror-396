from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Dict
from typing import Tuple

import numpy
from matplotlib.colors import hsv_to_rgb
from silx.math.medianfilter import medfilt2d

from darfix.core.dimension import AcquisitionDims
from darfix.core.transformation import Transformation
from darfix.io.utils import create_nxdata_dict

from ..dtypes import AxisType
from ..dtypes import Dataset
from .moment_types import MomentType
from .utils import compute_hsv

DimensionRange = Tuple[float, float]


DimensionMoments = Dict[MomentType, numpy.ndarray]


@dataclass
class GrainPlotMaps:
    dims: AcquisitionDims
    moments_dims: list[DimensionMoments]
    zsum: numpy.ndarray
    transformation: numpy.ndarray
    title: str

    @staticmethod
    def from_dataset(dataset: Dataset) -> GrainPlotMaps:
        """
        Just retrieve all necessary attributes in `ImageDataset` object to return a `GrainPlotMaps` object.

        :Note:  zsum computation is executed
        """
        imgDataset = dataset.dataset
        return GrainPlotMaps(
            dims=imgDataset.dims,
            moments_dims=imgDataset.moments_dims,
            zsum=imgDataset.zsum(),
            transformation=imgDataset.transformation,
            title=imgDataset.title,
        )


class OrientationDistData:
    KEY_IMAGE_SIZE = 1000

    def __init__(
        self,
        grain_plot_maps: GrainPlotMaps,
        x_dimension: int,
        y_dimension: int,
        x_dimension_range: DimensionRange,
        y_dimension_range: DimensionRange,
        zsum: numpy.ndarray | None = None,
    ) -> None:
        """
        Store data for orientation distribution RGB layer (the HSV colormap) and data (Histogram 2D)

        :param zsum: Precomputed dataset.zsum() used as the weight of the histogram 2D . If None dataset.zsum() is called.
        """

        if len(grain_plot_maps.moments_dims) == 0:
            raise ValueError("Moments should be computed before.")

        com_x = grain_plot_maps.moments_dims[x_dimension][MomentType.COM].ravel()
        com_y = grain_plot_maps.moments_dims[y_dimension][MomentType.COM].ravel()

        self.x_range = x_dimension_range
        self.y_range = y_dimension_range

        if zsum is None:
            zsum = grain_plot_maps.zsum
            zsum = zsum.ravel()
        else:
            zsum = zsum.ravel()

        # automatic bins
        # In darfix<=3.x orientation distribution shape was the size of the dimension
        # A x2 Factor is a little thinner. To see if it needs to be update in the future.
        self.x_bins = grain_plot_maps.dims.get(x_dimension).size * 2
        self.y_bins = grain_plot_maps.dims.get(y_dimension).size * 2

        self.x_label = grain_plot_maps.dims.get(x_dimension).name
        self.y_label = grain_plot_maps.dims.get(y_dimension).name

        x_data = numpy.linspace(-1, 1, self.KEY_IMAGE_SIZE)
        y_data = numpy.linspace(-1, 1, self.KEY_IMAGE_SIZE)
        x_mesh, y_mesh = numpy.meshgrid(x_data, y_data)
        self.rgb_key = hsv_to_rgb(compute_hsv(x_mesh, y_mesh))

        # Histogram in 2D
        histogram, _, _ = numpy.histogram2d(
            com_y,
            com_x,  # note: y first is in purpose : see numpy.histogram2d documentation
            weights=zsum,  # We need to take into account pixel intensity
            bins=[self.y_bins, self.x_bins],
            range=[self.y_range, self.x_range],
        )
        self.data = histogram
        """Orientation distribution data as an histogram 2D of the center of mass in two dimensions"""
        self.smooth_data = medfilt2d(numpy.ascontiguousarray(self.data))
        """ `self.data` filtered with a median filter 2D"""

    def x_data_values(self) -> numpy.ndarray:
        return numpy.linspace(
            self.x_range[0], self.x_range[1], self.x_bins, endpoint=False
        )

    def y_data_values(self) -> numpy.ndarray:
        return numpy.linspace(
            self.y_range[0], self.y_range[1], self.y_bins, endpoint=False
        )

    def x_rgb_key_values(self) -> numpy.ndarray:
        return numpy.linspace(
            self.x_range[0], self.x_range[1], self.KEY_IMAGE_SIZE, endpoint=False
        )

    def y_rgb_key_values(self) -> numpy.ndarray:
        return numpy.linspace(
            self.y_range[0], self.y_range[1], self.KEY_IMAGE_SIZE, endpoint=False
        )

    def origin(
        self,
        origin: AxisType,
    ) -> tuple[float, float]:
        if origin == "dims":
            return (self.x_range[0], self.y_range[0])
        elif origin == "center":
            return (
                -numpy.ptp(self.x_range) / 2,
                -numpy.ptp(self.y_range) / 2,
            )
        else:
            return (0, 0)

    def data_plot_scale(self) -> tuple[float, float]:
        return (
            numpy.ptp(self.x_range) / self.x_bins,
            numpy.ptp(self.y_range) / self.y_bins,
        )

    def rgb_key_plot_scale(self) -> tuple[float, float]:
        return (
            numpy.ptp(self.x_range) / self.KEY_IMAGE_SIZE,
            numpy.ptp(self.y_range) / self.KEY_IMAGE_SIZE,
        )

    def to_motor_coordinates(
        self,
        points_x: numpy.ndarray,
        points_y: numpy.ndarray,
        origin: AxisType,
    ) -> tuple[numpy.ndarray, numpy.ndarray]:
        """
        Given points_x, points_y in the 2D space of self.data, returns motor coordinates x, y
        """
        x_origin, y_origin = self.origin(origin)
        return (
            points_x * numpy.ptp(self.x_range) / (self.x_bins - 1) + x_origin,
            points_y * numpy.ptp(self.y_range) / (self.y_bins - 1) + y_origin,
        )


class MultiDimMomentType(Enum):
    """Moments that are only computed for datasets with multiple dimensions"""

    ORIENTATION_DIST = "Orientation distribution"
    MOSAICITY = "Mosaicity"


def get_axes(transformation: Transformation | None) -> tuple[
    tuple[numpy.ndarray, numpy.ndarray] | None,
    tuple[str, str] | None,
    tuple[str, str] | None,
]:
    if not transformation:
        return None, None, None

    axes = (transformation.xregular, transformation.yregular)
    axes_names = ("x", "y")
    axes_long_names = (transformation.label, transformation.label)

    return axes, axes_names, axes_long_names


def compute_normalized_component(
    component: numpy.ndarray, dimension_range: DimensionRange
):

    min_component = dimension_range[0]
    max_component = dimension_range[1]

    return 2 * (component - min_component) / (max_component - min_component) - 1


def compute_mosaicity(
    moments: dict[int, numpy.ndarray],
    x_dimension: int,
    y_dimension: int,
    x_dimension_range: DimensionRange,
    y_dimension_range: DimensionRange,
):
    norm_center_of_mass_x = compute_normalized_component(
        moments[x_dimension][MomentType.COM],
        dimension_range=x_dimension_range,
    )
    norm_center_of_mass_y = compute_normalized_component(
        moments[y_dimension][MomentType.COM],
        dimension_range=y_dimension_range,
    )
    return hsv_to_rgb(compute_hsv(norm_center_of_mass_x, norm_center_of_mass_y))


def create_moment_nxdata_groups(
    parent: dict[str, Any],
    moment_data: numpy.ndarray,
    axes,
    axes_names,
    axes_long_names,
):

    for map_type in MomentType:
        map_value = map_type.value
        parent[map_value] = create_nxdata_dict(
            moment_data[map_type],
            map_value,
            axes,
            axes_names,
            axes_long_names,
        )


def generate_grain_maps_nxdict(
    grainPlotMaps: GrainPlotMaps,
    mosaicity: numpy.ndarray | None,
    orientation_dist_image: OrientationDistData | None,
) -> dict:
    moments = grainPlotMaps.moments_dims
    axes, axes_names, axes_long_names = get_axes(grainPlotMaps.transformation)

    nx = {
        "entry": {"@NX_class": "NXentry"},
        "@NX_class": "NXroot",
        "@default": "entry",
    }

    if mosaicity is not None:
        nx["entry"][MultiDimMomentType.MOSAICITY.value] = create_nxdata_dict(
            mosaicity,
            MultiDimMomentType.MOSAICITY.value,
            axes,
            axes_names,
            axes_long_names,
            rgba=True,
        )
        nx["entry"]["@default"] = MultiDimMomentType.MOSAICITY.value
    else:
        nx["entry"]["@default"] = MomentType.COM.value

    if orientation_dist_image is not None:
        nx["entry"][MultiDimMomentType.ORIENTATION_DIST.value] = {
            "key": create_nxdata_dict(
                orientation_dist_image.rgb_key,
                "image",
                (
                    orientation_dist_image.y_rgb_key_values(),
                    orientation_dist_image.x_rgb_key_values(),
                ),
                (orientation_dist_image.y_label, orientation_dist_image.x_label),
                rgba=True,
            ),
            "data": create_nxdata_dict(
                orientation_dist_image.data,
                "orientation distribution",
                (
                    orientation_dist_image.y_data_values(),
                    orientation_dist_image.x_data_values(),
                ),
                (orientation_dist_image.y_label, orientation_dist_image.x_label),
            ),
            "@default": "data",
        }

    if grainPlotMaps.dims.ndim <= 1:
        create_moment_nxdata_groups(
            nx["entry"],
            moments[0],
            axes,
            axes_names,
            axes_long_names,
        )
    else:
        for axis, dim in grainPlotMaps.dims.items():
            nx["entry"][dim.name] = {"@NX_class": "NXcollection"}
            create_moment_nxdata_groups(
                nx["entry"][dim.name],
                moments[axis],
                axes,
                axes_names,
                axes_long_names,
            )

    return nx
