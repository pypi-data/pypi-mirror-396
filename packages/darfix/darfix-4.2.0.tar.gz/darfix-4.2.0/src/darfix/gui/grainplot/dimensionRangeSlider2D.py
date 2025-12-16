from __future__ import annotations

from functools import partial

from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt

from darfix.core.dimension import AcquisitionDims
from darfix.core.dimension import Dimension
from darfix.gui.utils.rangeSlider import RangeSliderWithSpinBox


class _DimensionRangeSlider(qt.QWidget):
    """
    RangeSlider for a darfix dimension
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dimCB = qt.QComboBox()
        self.range = RangeSliderWithSpinBox()

        layout = qt.QHBoxLayout()
        layout.addWidget(self.dimCB)
        layout.addWidget(self.range)
        self.setLayout(layout)

    def setCurrentDimension(self, dims: AcquisitionDims, index: int):
        dim = dims.get(index)
        self.setDimensionRange(dim)
        with block_signals(self.dimCB):
            self.dimCB.clear()
            self.dimCB.addItems(dims.get_names())
            self.dimCB.setCurrentIndex(index)

    def setDimensionRange(self, dim: Dimension):
        self.range.setRange(dim.min(), dim.max())

    def currentDimensionIndex(self) -> int:
        return self.dimCB.currentIndex()

    def setDimensionIndex(self, idx: int):
        self.dimCB.setCurrentIndex(idx)


class DimensionRangeSlider2D(qt.QWidget):
    """
    Two dimension sliders and two combo boxes to select dimension in the mosaicity plot
    """

    sigChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__dims: None | AcquisitionDims = None

        layout = qt.QHBoxLayout()

        self.__sliders = _DimensionRangeSlider(), _DimensionRangeSlider()

        for slider in self.__sliders:
            layout.addWidget(slider)
            slider.range.sigValueChanged.connect(self.sigChanged)
        self.__sliders[0].dimCB.currentIndexChanged.connect(
            partial(self._onDimensionChanged, self.__sliders[0], self.__sliders[1])
        )
        self.__sliders[1].dimCB.currentIndexChanged.connect(
            partial(self._onDimensionChanged, self.__sliders[1], self.__sliders[0])
        )

        self.setLayout(layout)

    def indexDimX(self) -> int:
        return self.__sliders[0].currentDimensionIndex()

    def indexDimY(self) -> int:
        return self.__sliders[1].currentDimensionIndex()

    def rangeDimX(self) -> tuple[float, float]:
        return self.__sliders[0].range.getValues()

    def rangeDimY(self) -> tuple[float, float]:
        return self.__sliders[1].range.getValues()

    def setDimensions(self, dims: AcquisitionDims):
        self.__dims = dims
        for idx, slider in enumerate(self.__sliders):
            slider.setCurrentDimension(dims, idx)

    def _onDimensionChanged(
        self, slider: _DimensionRangeSlider, other: _DimensionRangeSlider
    ):

        slider.setDimensionRange(self.__dims.get(slider.currentDimensionIndex()))

        if slider.currentDimensionIndex() == other.currentDimensionIndex():
            if other.currentDimensionIndex() == 0:
                other.setDimensionIndex(1)
            else:
                other.setDimensionIndex(0)
            # Signal emitted by the second slider
        else:
            self.sigChanged.emit()
