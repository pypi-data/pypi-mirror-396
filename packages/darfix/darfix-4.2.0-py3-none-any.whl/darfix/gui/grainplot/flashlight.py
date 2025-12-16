from __future__ import annotations

import weakref

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import PlotWidget
from silx.gui.plot.actions.control import KeepAspectRatioAction
from silx.gui.plot.items.image import ImageBase
from silx.gui.plot.items.marker import Marker
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.tools import InteractiveModeToolBar
from silx.gui.plot.tools import OutputToolBar
from silx.gui.plot.tools.roi import RegionOfInterestManager

from .flashlight_mode_action import FlashlightModeAction


def _toImgCoord(img: ImageBase, coord: tuple[float, float]) -> tuple[int, int] | None:
    if img is None:
        # Not init
        return None
    origin = numpy.asarray(img.getOrigin())
    scale = numpy.asarray(img.getScale())

    i, j = tuple(((numpy.asarray(coord) - origin) / scale).astype(int))

    if 0 > i or i >= img.getData(False).shape[1]:
        # out of bound
        return None
    if 0 > j or j >= img.getData(False).shape[0]:
        # out of bound
        return None
    return i, j


class RectangleImageROI(RectangleROI):
    def __init__(self, plot: PlotWidget):
        super().__init__()
        self.__plotRef = weakref.ref(plot)
        self.__centerPositionLabel: Marker = self.addLabelHandle()
        self.__centerPositionLabel.setBackgroundColor([1.0, 1.0, 1.0, 0.5])
        self.sigRegionChanged.connect(self._onRegionChanged)

    @property
    def plot(self) -> PlotWidget:
        """The :class:`PlotWidget` this roi is attached."""
        plot = self.__plotRef()
        if plot is None:
            raise ValueError("The attached plot was already destroyed")
        return plot

    def _onRegionChanged(self):

        x, y = self.getOrigin()
        self.__centerPositionLabel.setPosition(x, y)
        x, y = self.getCenter()
        sizeX, sizeY = self.getSize()
        self.__centerPositionLabel.setText(
            f"Center: {x:.3f}, {y:.3f} \n(Size : {sizeX:.3f}, {sizeY:.3f})"
        )

    def getCenterIJ(self) -> tuple[int, int]:
        """ROI center as indices i,j in the underlying image data"""
        coordinates_ij = _toImgCoord(self.plot.getActiveImage(), self.getCenter())
        if coordinates_ij is None:
            raise ValueError("ROI center outside of the plot or no active image")
        return coordinates_ij

    def getSlices(self) -> tuple:
        """ROI slices give the image data array selection as a tuple of two slices over i and j axis"""

        if self.plot.getImage() is None:
            raise ValueError(
                "At least one image should be added in InteractiveMaskPlotWithFlashlight"
            )
        scale = self.plot.getActiveImage().getScale()

        coordinates_ij = _toImgCoord(self.plot.getActiveImage(), self.getCenter())
        if coordinates_ij is not None:
            i, j = coordinates_ij
        else:
            raise ValueError("ROI center outside of the plot or no active image")

        w = int(self.getSize()[0] / scale[0])
        h = int(self.getSize()[1] / scale[1])

        return (slice(max(0, j - h), j + h), slice(max(0, i - w), i + w))


class PlotWithFlashlight(PlotWidget):
    """
    A plot with a roi that follow mouse. Shape of the ROI can be modified with button left pressed.
    """

    DEFAULT_FLASHLIGHT_SIZE = 0.1

    sigFlashlightHide = qt.Signal()
    sigFlashlightMove = qt.Signal()

    def __init__(self, **kwarks):
        super().__init__(**kwarks)
        self.__selectionStart = None

        self.__roiManager = RegionOfInterestManager(parent=self)
        self.__roi = RectangleImageROI(self)

        self.__roiManager.addRoi(self.__roi)
        self.__roi.setSize((self.DEFAULT_FLASHLIGHT_SIZE, self.DEFAULT_FLASHLIGHT_SIZE))
        self.__roi.setVisible(False)
        self.__roi.setColor([0.2, 0.2, 0.2])
        self.__roi.setLineStyle("--")

        self.__interactiveToolBar = InteractiveModeToolBar(plot=self)
        self.__interactiveToolBar.addAction(
            FlashlightModeAction(parent=self, plot=self)
        )

        outputToolBar = OutputToolBar(plot=self)
        outputToolBar.addAction(KeepAspectRatioAction(parent=self, plot=self))

        self.addToolBar(self.__interactiveToolBar)
        self.addToolBar(outputToolBar)

        self.setInteractiveMode(FlashlightModeAction.INTERACTION_MODE)

        self.setMouseTracking(True)

        self.sigPlotSignal.connect(self._onPlotSignal)

    def getRoi(self) -> RectangleImageROI:
        """Get the current ROI"""
        return self.__roi

    def isFlashlightEnabled(self) -> bool:
        """Is flashlight mode enabled"""
        return (
            self.getInteractiveMode()["mode"] == FlashlightModeAction.INTERACTION_MODE
        )

    def _onPlotSignal(self, evt: dict):
        if evt["event"] != "mouseMoved":
            return
        dataCoordinates = (evt["x"], evt["y"])
        imgCoordinates = _toImgCoord(self.getActiveImage(), dataCoordinates)
        if imgCoordinates is not None:
            self.__onMove(*imgCoordinates, *dataCoordinates)
        else:
            self._leave()

    def _leave(self):
        if self.__roi.isVisible():
            self.sigFlashlightHide.emit()
            self.setCursor(qt.Qt.CursorShape.ArrowCursor)
            self.__roi.setVisible(False)

    def __onMove(self, i: int, j: int, x: float, y: float):
        if not self.isFlashlightEnabled():
            return
        if not self.__roi.isVisible():
            self.__roi.setVisible(True)
        if self.__selectionStart is not None:
            newRoiSize = numpy.abs(numpy.subtract((x, y), self.__selectionStart)) * 2
            self.__roi.setSize(newRoiSize)
        self.setCursor(qt.Qt.CursorShape.CrossCursor)
        self.__roi.setCenter((x, y))
        self.sigFlashlightMove.emit()

    def onMousePress(self, xPixel, yPixel, btn):
        super().onMousePress(xPixel, yPixel, btn)
        if not self.isFlashlightEnabled():
            return
        dataCoordinates = self.pixelToData(xPixel, yPixel, check=True)
        if dataCoordinates is not None:
            self.__selectionStart = dataCoordinates

    def onMouseRelease(self, xPixel, yPixel, btn):
        self.__selectionStart = None
        super().onMouseRelease(xPixel, yPixel, btn)

    def onMouseLeaveWidget(self):
        self._leave()
        super().onMouseLeaveWidget()

    def _getMaskImage(self, legend: str, alpha_value=127):
        img = self.getImage(legend)
        if img is None:
            active = self.getActiveImage()
            data = numpy.zeros(self.getPlotMaskShape(), numpy.uint8)
            img = self.addImage(
                data,
                legend,
                scale=active.getScale(),
                origin=active.getOrigin(),
                colormap=Colormap(colors=[[0, 0, 0, 0], [0, 0, 0, alpha_value]]),
            )
        return img

    def clearPlotMask(self, legend: str = "__MASK__"):
        """in the plot, clear image mask with legend `legend`"""
        if self.getImage(legend) is not None:
            self.removeImage(legend)

    def createPlotMask(self, mask: numpy.ndarray, legend: str = "__MASK__"):
        """in the plot, create image mask with legend `legend`"""
        self._getMaskImage(legend).setData(mask, copy=False)

    def getPlotMaskShape(self) -> tuple[int, int]:
        """Get desired 2D shape to fit shape of active image in the plot"""
        return self.getActiveImage().getData(False).shape[:2]
