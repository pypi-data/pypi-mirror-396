from __future__ import annotations

from enum import Enum

from silx.gui import icons
from silx.gui import qt

from ...dtypes import AxisType
from ._oridist_toolbar_buttons import _AxisTypeToolButton
from ._oridist_toolbar_buttons import _ContourConfigToolButton
from ._oridist_toolbar_buttons import _DatatypeToolbutton
from ._oridist_toolbar_buttons import _NormalizationToolButton


class OriDistButtonIds(Enum):
    DATA = 0
    """Data of the orientation distribution histogram 2D"""
    COLOR_KEY = 1
    """ Data as a HSV color map"""


class OriDistToolbar(qt.QToolBar):
    """
    Custom toolbar for the Orientation Distribution plot configuration
    """

    sigContourChanged = qt.Signal()
    sigReplot = qt.Signal()

    def __init__(self):

        super().__init__()

        self.__contourToolButton = _ContourConfigToolButton()

        self.__scaleToolButton = _NormalizationToolButton()

        self.__dataPlotTypeToolButton = _DatatypeToolbutton()

        self.__axisToolButton = _AxisTypeToolButton()

        self.__medianFilterAction = qt.QAction()
        self.__medianFilterAction.setCheckable(True)
        self.__medianFilterAction.setChecked(True)
        self.__medianFilterAction.setIcon(
            icons.getQIcon("darfix:gui/icons/median-filter")
        )
        self.__medianFilterAction.setToolTip("Apply a 2D median filter")

        self.addWidget(self.__scaleToolButton)
        self.addWidget(self.__axisToolButton)
        self.addWidget(self.__dataPlotTypeToolButton)
        self.addWidget(self.__contourToolButton)
        self.addAction(self.__medianFilterAction)

        # connect signal / slot
        self.__contourToolButton.sigChanged.connect(self.sigContourChanged)
        self.__scaleToolButton.sigChanged.connect(self.sigReplot)
        self.__scaleToolButton.sigChanged.connect(self.sigContourChanged)
        self.__axisToolButton.sigChanged.connect(self.sigReplot)
        self.__axisToolButton.sigChanged.connect(self.sigContourChanged)
        self.__dataPlotTypeToolButton.sigChanged.connect(self.sigReplot)
        self.__medianFilterAction.toggled.connect(self.sigReplot)

    def getOriginType(self) -> AxisType:
        return self.__axisToolButton.getCurrentAxisType()

    def getNormalization(self) -> str:
        return self.__scaleToolButton.getNormalization()

    def getLevelCount(self) -> int:
        return self.__contourToolButton.value()

    def isContourEnabled(self) -> bool:
        return self.__contourToolButton.isChecked()

    def getColorKeyOpacityValue(self) -> int:
        return 256 - self.__dataPlotTypeToolButton.value()

    def getDataPlotType(self) -> OriDistButtonIds:
        if self.__dataPlotTypeToolButton.isChecked():
            return OriDistButtonIds.COLOR_KEY
        else:
            return OriDistButtonIds.DATA

    def medianFilterEnabled(self) -> bool:
        return self.__medianFilterAction.isChecked()
