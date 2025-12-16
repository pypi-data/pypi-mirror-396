from __future__ import annotations

import numpy
import pytest
from ewoksorange.tests.conftest import qtapp  # noqa F811
from silx.gui.data.test.test_dataviewer import SignalListener

from darfix.core.dimension import AcquisitionDims
from darfix.core.dimension import Dimension
from darfix.gui.grainplot.dimensionRangeSlider2D import DimensionRangeSlider2D
from darfix.gui.grainplot.dimensionRangeSlider2D import _DimensionRangeSlider


@pytest.fixture
def widget(qtapp) -> DimensionRangeSlider2D:  # noqa F811
    return DimensionRangeSlider2D()


@pytest.fixture
def dims() -> AcquisitionDims:
    dims = AcquisitionDims()
    dims.add_dim(0, Dimension("A", 30, 0, 10))
    dims.add_dim(1, Dimension("B", 20, 0, 3))
    dims.add_dim(2, Dimension("C", 8, -10, -12))
    return dims


def test_set_dimensions(widget, dims):
    listener = SignalListener()

    widget.sigChanged.connect(listener)
    widget.setDimensions(dims)
    # Dim X is "A"
    assert widget.indexDimX() == 0
    numpy.testing.assert_allclose(widget.rangeDimX(), [0, 10])
    # Dim Y is "B"
    assert widget.indexDimY() == 1
    numpy.testing.assert_allclose(widget.rangeDimY(), [0, 3])
    assert (
        listener.callCount() == 0
    ), "`sigChanged` should not be called by `setDimensions`"


def test_switch_dimensions(widget, dims):

    listener = SignalListener()

    widget.sigChanged.connect(listener)
    widget.setDimensions(dims)
    sliders: tuple[_DimensionRangeSlider, _DimensionRangeSlider] = (
        widget._DimensionRangeSlider2D__sliders
    )

    sliders[0].setDimensionIndex(2)
    assert listener.callCount() == 1
    # Dim X is now "C"
    assert widget.indexDimX() == 2
    numpy.testing.assert_allclose(widget.rangeDimX(), [-12, -10])
    # Dim Y is still "B"
    assert widget.indexDimY() == 1
    numpy.testing.assert_allclose(widget.rangeDimY(), [0, 3])

    sliders[0].setDimensionIndex(1)
    assert listener.callCount() == 2
    # Dim X is now "B"
    assert widget.indexDimX() == 1
    numpy.testing.assert_allclose(widget.rangeDimX(), [0, 3])
    # Dim Y move to "A" as first slider is "B" (ANd we cannot have the same dimension for x and y)
    assert widget.indexDimY() == 0
    numpy.testing.assert_allclose(widget.rangeDimY(), [0, 10])
