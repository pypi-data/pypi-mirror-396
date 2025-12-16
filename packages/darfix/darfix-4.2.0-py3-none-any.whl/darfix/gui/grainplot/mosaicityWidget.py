from __future__ import annotations

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.items import ImageBase
from silx.image.marchingsquares import find_contours

from darfix.gui.grainplot.dimensionRangeSlider2D import DimensionRangeSlider2D

from ...core.grainplot import GrainPlotMaps
from ...core.grainplot import MultiDimMomentType
from ...core.grainplot import OrientationDistData
from ...core.grainplot import compute_mosaicity
from ...core.moment_types import MomentType
from .flashlight import PlotWithFlashlight
from .oridist_toolbar import OriDistButtonIds
from .oridist_toolbar import OriDistToolbar
from .utils import MapType
from .utils import add_image_with_transformation


class MosaicityWidget(qt.QWidget):
    """Widget to display and explore mosaicity plots"""

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)

        self._grainPlotMaps: GrainPlotMaps | None = None
        self._orientation_dist_data: OrientationDistData | None = None
        self._mosaicity: numpy.ndarray | None = None
        self.contours = {}

        layout = qt.QGridLayout()

        #
        # Mosaicity plot (left) and Orientation Distribution (Ori Dist) plot (Right)
        # Row 0
        #

        self._mosaicityPlot = PlotWithFlashlight(parent=self)
        self._mosaicityPlot.setKeepDataAspectRatio(True)

        layout.addWidget(self._mosaicityPlot, 0, 0)

        self._oriDistPlot = PlotWithFlashlight(parent=self)
        self._oriDistPlot.setKeepDataAspectRatio(True)

        layout.addWidget(self._oriDistPlot, 0, 1)

        self._mosaicityPlot.sigFlashlightMove.connect(self._onMoveInMosaPlot)
        self._mosaicityPlot.sigFlashlightHide.connect(self._oriDistPlot.clearPlotMask)

        self._oriDistPlot.sigFlashlightMove.connect(
            self._onMoveInOrientationDistribPlot
        )
        self._oriDistPlot.sigFlashlightHide.connect(self._mosaicityPlot.clearPlotMask)

        #
        # Orientation Distribution (Ori Dist) Configuration dock widget as an action
        # in the `_oriDistPlot` tool bar.`
        #

        self._oriDistToolbar = OriDistToolbar()

        self._oriDistPlot.addToolBar(self._oriDistToolbar)

        self._oriDistToolbar.sigContourChanged.connect(self._computeContours)
        self._oriDistToolbar.sigReplot.connect(self._plotOrientationData)

        #
        # info label then separator
        # Row 1 and 2
        #
        infoLayout = qt.QHBoxLayout()
        infoLayout.addWidget(qt.QLabel("Dimension values:"))
        self._infosLabel1 = qt.QLabel()
        self._infosLabel2 = qt.QLabel()
        infoLayout.addWidget(self._infosLabel1)
        infoLayout.addWidget(self._infosLabel2)
        layout.addLayout(infoLayout, 1, 0, 1, 2)

        separator = qt.QFrame()
        separator.setFrameShape(qt.QFrame.HLine)
        separator.setFrameShadow(qt.QFrame.Sunken)
        layout.addWidget(separator, 2, 0, 1, 2)

        #
        # zsum threshold
        # Row 3
        #

        thresholdLayout = qt.QHBoxLayout()

        self._zsum: None | numpy.ndarray = None
        """Keep zsum to avoid compute each time we update plots"""
        self._thresholdSB = qt.QSpinBox()
        """ Discard mosa values below this threshold """
        self._thresholdSB.setButtonSymbols(qt.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._thresholdSB.editingFinished.connect(self._computeMosaicityAndOriDist)
        thresholdLayout.addWidget(qt.QLabel("ZSum Threshold : "))
        thresholdLayout.addWidget(self._thresholdSB)
        thresholdLayout.addStretch(1)
        layout.addLayout(thresholdLayout, 3, 0)

        #
        # Dimension range sliders
        # Row 4
        #

        self._sliders = DimensionRangeSlider2D()
        self._sliders.sigChanged.connect(self._computeMosaicityAndOriDist)
        layout.addWidget(self._sliders, 4, 0, 1, 2)

        self.setLayout(layout)

    @property
    def dimension1(self) -> int:
        return self._sliders.indexDimX()

    @property
    def dimension2(self) -> int:
        return self._sliders.indexDimY()

    def getMosaicity(self):
        return self._mosaicity

    def getContoursImage(self):
        return self._oriDistPlot.getImage()

    def getOrientationDist(self):
        return self._orientation_dist_data

    def setGrainPlotMaps(self, grainPlotMaps: GrainPlotMaps):
        self._grainPlotMaps = grainPlotMaps
        self._thresholdSB.setMaximum(int(self._grainPlotMaps.zsum.max()))

        self._mosaicityPlot.setGraphTitle(
            self._grainPlotMaps.title + "\n" + MapType.MOSAICITY.value
        )
        self._oriDistPlot.setGraphTitle(
            self._grainPlotMaps.title + "\n" + MultiDimMomentType.ORIENTATION_DIST.value
        )

        self._sliders.setDimensions(self._grainPlotMaps.dims)

        self._computeMosaicityAndOriDist()

    def _plotMosaicity(self):
        if self._grainPlotMaps is None:
            return

        if self._mosaicity is not None:
            add_image_with_transformation(
                self._mosaicityPlot, self._mosaicity, self._grainPlotMaps.transformation
            )

    def _plotOrientationData(self, state=None):
        if self._grainPlotMaps is None or self._orientation_dist_data is None:
            return

        self._oriDistPlot.resetZoom()

        origin = self._orientation_dist_data.origin(
            self._oriDistToolbar.getOriginType()
        )

        self._oriDistPlot.addImage(
            self._orientation_dist_data.rgb_key,
            legend="Color key",
            xlabel=self._orientation_dist_data.x_label,
            ylabel=self._orientation_dist_data.y_label,
            origin=origin,
            scale=self._orientation_dist_data.rgb_key_plot_scale(),
        )
        maxOpacityValue = self._oriDistToolbar.getColorKeyOpacityValue()
        colors = numpy.zeros(shape=(maxOpacityValue, 4), dtype=numpy.uint8)
        colors[..., -1] = numpy.arange(maxOpacityValue - 1, -1, -1)

        self._oriDistPlot.addImage(
            (
                self._orientation_dist_data.smooth_data
                if self._oriDistToolbar.medianFilterEnabled()
                else self._orientation_dist_data.data
            ),
            legend="Data",
            xlabel=self._orientation_dist_data.x_label,
            ylabel=self._orientation_dist_data.y_label,
            origin=origin,
            colormap=Colormap(
                colors=colors,
                normalization=self._oriDistToolbar.getNormalization(),
                vmax=(
                    1
                    if self._oriDistToolbar.getDataPlotType()
                    == OriDistButtonIds.COLOR_KEY
                    else None
                ),
            ),
            scale=self._orientation_dist_data.data_plot_scale(),
        )
        if self._oriDistToolbar.getDataPlotType() == OriDistButtonIds.COLOR_KEY:
            self._oriDistPlot.setActiveImage("Color key")
        else:
            self._oriDistPlot.setActiveImage("Data")

    def _computeContours(self):
        """
        Compute contours map based on orientation distribution.
        """
        self._oriDistPlot.remove(kind="curve")

        if not self._oriDistToolbar.isContourEnabled():
            return

        orientationImagePlot: ImageBase | None = self._oriDistPlot.getImage()

        if self._orientation_dist_data is None or orientationImagePlot is None:
            return

        min_orientation = numpy.min(self._orientation_dist_data.smooth_data)
        max_orientation = numpy.max(self._orientation_dist_data.smooth_data)

        polygons = []
        levels = []

        normalization = self._oriDistToolbar.getNormalization()

        if normalization == "log":
            isoValues = numpy.logspace(
                numpy.log10(max(min_orientation, 1)),
                numpy.log10(max_orientation),
                int(self._oriDistToolbar.getLevelCount()),
            )
        elif normalization == "linear":
            isoValues = numpy.linspace(
                min_orientation,
                max_orientation,
                int(self._oriDistToolbar.getLevelCount()),
            )
        else:
            raise ValueError(f"Unhandled normalization value `{normalization}`")
        for isoValue in isoValues:
            polygons.append(
                find_contours(self._orientation_dist_data.smooth_data, isoValue)
            )
            levels.append(isoValue)

        colormap = Colormap(
            name="temperature",
            vmin=min_orientation,
            vmax=max_orientation,
            normalization=normalization,
        )
        colors = colormap.applyToData(levels)
        self.contours = {}
        for ipolygon, polygon in enumerate(polygons):
            # iso contours
            for icontour, contour in enumerate(polygon):
                if len(contour) == 0:
                    continue

                x = contour[:, 1]
                y = contour[:, 0]
                x_pts, y_pts = self._orientation_dist_data.to_motor_coordinates(
                    x, y, self._oriDistToolbar.getOriginType()
                )
                legend = f"poly{icontour}.{ipolygon}"
                self.contours[legend] = {
                    "points": (x_pts.copy(), y_pts.copy()),
                    "color": colors[ipolygon],
                    "value": levels[ipolygon],
                    "pixels": (x, y),
                }
                self._oriDistPlot.addCurve(
                    x=x_pts,
                    y=y_pts,
                    linestyle="-",
                    linewidth=2.0,
                    legend=legend,
                    resetzoom=False,
                    color=colors[ipolygon],
                )

    def _updatePositionInfoLabel(self, firstDimValue: float, secondDimValue: float):
        dim1Name = self._grainPlotMaps.dims.get(self.dimension1).name
        dim2Name = self._grainPlotMaps.dims.get(self.dimension2).name
        self._infosLabel1.setText(f"{dim1Name} = {firstDimValue:.4}")
        self._infosLabel2.setText(f"{dim2Name} = {secondDimValue:.4}")

    def _onMoveInMosaPlot(self):

        slices = self._mosaicityPlot.getRoi().getSlices()
        i, j = self._mosaicityPlot.getRoi().getCenterIJ()

        com_x_range = self._grainPlotMaps.moments_dims[self.dimension1][MomentType.COM][
            slices
        ].ravel()
        com_y_range = self._grainPlotMaps.moments_dims[self.dimension2][MomentType.COM][
            slices
        ].ravel()
        com_x_range = com_x_range[numpy.isfinite(com_x_range)]
        com_y_range = com_y_range[numpy.isfinite(com_y_range)]

        self._updatePositionInfoLabel(
            self._grainPlotMaps.moments_dims[self.dimension1][MomentType.COM][j, i],
            self._grainPlotMaps.moments_dims[self.dimension2][MomentType.COM][j, i],
        )

        currentImg = self._oriDistPlot.getActiveImage()

        scale_x, scale_y = currentImg.getScale()
        origin_x, origin_y = currentImg.getOrigin()
        indices_i = ((com_x_range - origin_x) / scale_x).astype(int)
        indices_j = ((com_y_range - origin_y) / scale_y).astype(int)
        indices_ji = numpy.stack([indices_j, indices_i])

        shape = self._oriDistPlot.getPlotMaskShape()

        mask = numpy.ones(shape, dtype=bool)
        discardOutOfBoundsMask = numpy.all(
            (indices_ji >= 0)
            & (indices_ji < numpy.asarray(mask.shape)[:, numpy.newaxis]),
            axis=0,
        )
        indices_ji = indices_ji[:, discardOutOfBoundsMask]
        indices_j, indices_i = indices_ji

        mask[indices_j, indices_i] = False
        self._oriDistPlot.createPlotMask(mask)

    def _onMoveInOrientationDistribPlot(self):

        x, y = self._oriDistPlot.getRoi().getCenter()

        self._updatePositionInfoLabel(x, y)

        com_x = self._grainPlotMaps.moments_dims[self.dimension1][MomentType.COM]
        com_y = self._grainPlotMaps.moments_dims[self.dimension2][MomentType.COM]

        w, h = self._oriDistPlot.getRoi().getSize() / 2

        iso_x = numpy.isclose(com_x, x, atol=w)
        iso_y = numpy.isclose(com_y, y, atol=h)
        mask = ~numpy.all(numpy.stack((iso_x, iso_y)), axis=0)
        self._mosaicityPlot.createPlotMask(mask)

    def _computeMosaicityAndOriDist(self):
        """
        Compute mosaicity and orientation distribution.

        Called when dimensions are changed (by setting the dataset or user interaction).
        """

        if self._grainPlotMaps is None:
            return

        maskZsum = self._grainPlotMaps.zsum <= self._thresholdSB.value()

        zsum = self._grainPlotMaps.zsum.copy()
        zsum[maskZsum] = 0

        self._mosaicity = compute_mosaicity(
            self._grainPlotMaps.moments_dims,
            x_dimension=self.dimension1,
            y_dimension=self.dimension2,
            x_dimension_range=self._sliders.rangeDimX(),
            y_dimension_range=self._sliders.rangeDimY(),
        )
        self._mosaicity[maskZsum] = 0, 0, 0  # Black

        self._orientation_dist_data = OrientationDistData(
            self._grainPlotMaps,
            x_dimension=self.dimension1,
            y_dimension=self.dimension2,
            x_dimension_range=self._sliders.rangeDimX(),
            y_dimension_range=self._sliders.rangeDimY(),
            zsum=zsum,
        )
        self._plotMosaicity()
        self._plotOrientationData()
        self._computeContours()
