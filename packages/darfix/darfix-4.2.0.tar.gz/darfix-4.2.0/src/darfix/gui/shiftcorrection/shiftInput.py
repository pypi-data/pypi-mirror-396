from __future__ import annotations

from typing import Tuple

from silx.gui import qt

from ..utils.vspacer import VSpacer


class ShiftInput(qt.QWidget):
    """
    Widget used to obtain the double parameters for the shift correction.
    """

    shiftChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.findShiftB = qt.QPushButton("Find shift")
        self.abortShiftB = qt.QPushButton("Abort")
        # First dim is displayed on vertical axis, second on horizontal
        firstDimLabel = qt.QLabel("Vertical shift per frame (pixels)")
        secondDimLabel = qt.QLabel("Horizontal shift per frame (pixels)")
        self._firstDimSB = qt.QDoubleSpinBox()
        self._secondDimSB = qt.QDoubleSpinBox()

        for spinbox in (self._firstDimSB, self._secondDimSB):
            spinbox.setMinimum(-1000)
            spinbox.setMaximum(1000)
            spinbox.setButtonSymbols(qt.QAbstractSpinBox.ButtonSymbols.NoButtons)

        self._firstDimSB.editingFinished.connect(self.shiftChanged.emit)
        self._secondDimSB.editingFinished.connect(self.shiftChanged.emit)

        layout = qt.QGridLayout()

        layout.addWidget(self.findShiftB, 0, 0, 1, 1)
        layout.addWidget(self.abortShiftB, 0, 1, 1, 1)
        layout.addWidget(firstDimLabel, 1, 0)
        layout.addWidget(secondDimLabel, 2, 0)
        layout.addWidget(self._firstDimSB, 1, 1)
        layout.addWidget(self._secondDimSB, 2, 1)

        layout.addWidget(VSpacer())

        self.setLayout(layout)

    def getShift(self) -> Tuple[float, float]:
        return float(self._firstDimSB.value()), float(self._secondDimSB.value())

    def setShift(self, shift: Tuple[float, float]):
        first_dim_shift, second_dim_shift = shift
        self._firstDimSB.setValue(first_dim_shift)
        self._secondDimSB.setValue(second_dim_shift)
