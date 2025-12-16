from __future__ import annotations

from enum import Enum

from silx.gui import icons
from silx.gui import qt

from ...dtypes import AxisType
from ..utils.axis_type_combobox import AXIS_TYPES


class OriDistButtonIds(Enum):
    DATA = 0
    """Data of the orientation distribution histogram 2D"""
    COLOR_KEY = 1
    """ Data as a HSV color map"""


class _AxisTypeToolButton(qt.QToolButton):
    """Select axis from `AXIS_TYPES` with a menu"""

    sigChanged = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setText("Axis")
        self.setToolTip("Select axis type")
        self.setPopupMode(qt.QToolButton.InstantPopup)

        self._actionGroup = qt.QActionGroup(self)
        self._actionGroup.setExclusive(True)

        for key in AXIS_TYPES.keys():
            action = qt.QAction(key, self)
            action.setCheckable(True)
            action.triggered.connect(self.sigChanged)
            self._actionGroup.addAction(action)
            self.addAction(action)

        self._actionGroup.actions()[0].setChecked(True)

    def getCurrentAxisType(self) -> AxisType:
        return AXIS_TYPES[self._actionGroup.checkedAction().text()]


class _NormalizationToolButton(qt.QToolButton):
    """Select normalization (Log or Linear) with a menu"""

    sigChanged = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setText("Normalization")
        self.setToolTip("Select normalization for plot and contours")
        self.setPopupMode(qt.QToolButton.InstantPopup)

        self._actionGroup = qt.QActionGroup(self)
        self._actionGroup.setExclusive(True)

        for normalization in ["log", "linear"]:
            action = qt.QAction(normalization, self)
            action.setCheckable(True)
            action.triggered.connect(self.sigChanged)
            self._actionGroup.addAction(action)
            self.addAction(action)

        self._actionGroup.actions()[0].setChecked(True)

    def getNormalization(self) -> str:
        return self._actionGroup.checkedAction().text()


class _SliderToolButton(qt.QToolButton):
    """base class for a checkable toolbutton with a slider popup"""

    sigChanged = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setPopupMode(qt.QToolButton.MenuButtonPopup)
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self.sigChanged)

        self._slider = qt.QSlider(qt.Qt.Orientation.Horizontal)
        self._slider.setRange(0, 255)
        self._slider.valueChanged.connect(self.sigChanged)

        self._description = qt.QLabel()

        w = qt.QWidget()
        w.setLayout(qt.QVBoxLayout())
        w.layout().addWidget(self._description)
        w.layout().addWidget(self._slider)

        # embed the slider into the menu
        action = qt.QWidgetAction(self)
        action.setDefaultWidget(w)
        self.addAction(action)

    def value(self) -> int:
        return self._slider.value()


class _ContourConfigToolButton(_SliderToolButton):
    """Configure the contours"""

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setIcon(icons.getQIcon("darfix:gui/icons/contour"))
        self._slider.setRange(0, 30)
        self._slider.setValue(10)
        self.setToolTip("Contours count configuration. Disable contours if unchecked.")
        self._description.setText("Contours count")


class _DatatypeToolbutton(_SliderToolButton):
    """Select plot to show between data or color key. Configure transparency of color key"""

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setIcon(icons.getQIcon("darfix:gui/icons/hsv"))
        self._slider.setRange(0, 255)
        self._slider.setValue(127)
        self.setToolTip(
            "Tune color key layer opacity. Show underlying data if unchecked."
        )
        self._description.setText("Tune color key layer opacity")
