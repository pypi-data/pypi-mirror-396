from __future__ import annotations

import numpy
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt
from silx.gui.widgets.RangeSlider import RangeSlider


class RangeSliderWithSpinBox(qt.QWidget):
    """RangeSlider with spin boxes to select a numeric range."""

    sigValueChanged = qt.Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__spinBoxMin = qt.QDoubleSpinBox()
        self.__spinBoxMax = qt.QDoubleSpinBox()
        self.__slider = RangeSlider()

        for slider in self.__spinBoxMin, self.__spinBoxMax:
            slider.setButtonSymbols(qt.QAbstractSpinBox.ButtonSymbols.NoButtons)
            slider.setRange(-numpy.inf, numpy.inf)
            slider.setDecimals(3)

        layout = qt.QHBoxLayout(self)

        layout.addWidget(self.__spinBoxMin)
        layout.addWidget(self.__slider, 1)
        layout.addWidget(self.__spinBoxMax)

        self.__slider.sigValueChanged.connect(self.sigValueChanged)
        self.__slider.sigValueChanged.connect(self._onSliderUpdate)
        self.__spinBoxMin.editingFinished.connect(self._onSpinMinEdited)
        self.__spinBoxMax.editingFinished.connect(self._onSpinMaxEdited)

    def setRange(self, vmin: float, vmax: float):
        if vmax <= vmin:
            raise ValueError(f"max {vmax} <= min {vmin}")

        with block_signals(self.__spinBoxMin):
            self.__spinBoxMin.setMaximum(vmax)
            self.__spinBoxMin.setValue(vmin)

        with block_signals(self.__spinBoxMax):
            self.__spinBoxMax.setMinimum(vmin)
            self.__spinBoxMax.setValue(vmax)

        with block_signals(self.__slider):
            self.__slider.setRange(vmin, vmax)
            self.__slider.setValues(vmin, vmax)

    def getValues(self) -> tuple[float, float]:
        """Return the current selected (min, max) values."""
        return self.__slider.getValues()

    def getRange(self) -> tuple[float, float]:
        return self.__slider.getRange()

    def _onSpinMinEdited(self):
        spinMinValue = self.__spinBoxMin.value()

        # Minimum allowed value of `__spinMax` is `__spinBoxMin` value
        self.__spinBoxMax.setMinimum(spinMinValue)

        with block_signals(self.__slider):
            # Update slider minimum if spinbox min value is below range min
            if spinMinValue < self.__slider.getMinimum():
                self.__slider.setMinimum(spinMinValue)
            # update slider values
            self.__slider.setValues(spinMinValue, self.__spinBoxMax.value())

        self.sigValueChanged.emit(spinMinValue, self.__spinBoxMax.value())

    def _onSpinMaxEdited(self):
        spinMaxValue = self.__spinBoxMax.value()

        # Maximum allowed value of `__spinBoxMin` is `__spinBoxMax` value
        self.__spinBoxMin.setMaximum(spinMaxValue)

        with block_signals(self.__slider):
            # Update slider maximum if spinbox max value is above range max
            if spinMaxValue > self.__slider.getMaximum():
                self.__slider.setMaximum(spinMaxValue)
            # update slider values
            self.__slider.setValues(self.__spinBoxMin.value(), spinMaxValue)

        self.sigValueChanged.emit(self.__spinBoxMin.value(), spinMaxValue)

    def _onSliderUpdate(self):
        v0, v1 = self.__slider.getValues()
        self.__spinBoxMin.setValue(v0)
        self.__spinBoxMax.setValue(v1)
