import numpy
from silx.gui import qt


def createCustomDoubleSpinBox(initialValue: float = 0.0) -> qt.QDoubleSpinBox:
    """
    Custom double spin box with :
    - No button
    - No min / max limits
    - 4 decimals
    - an optional `initialValue` (0.0 by default)
    """
    spinBox = qt.QDoubleSpinBox()
    spinBox.setValue(initialValue)
    spinBox.setDecimals(4)
    spinBox.setMaximum(numpy.inf)
    spinBox.setMinimum(-numpy.inf)
    spinBox.setButtonSymbols(qt.QAbstractSpinBox.ButtonSymbols.NoButtons)
    return spinBox
