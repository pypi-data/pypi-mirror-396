from __future__ import annotations

import numpy
import pytest
from ewoksorange.tests.conftest import qtapp  # noqa F811
from silx.gui import qt
from silx.gui.data.test.test_dataviewer import SignalListener
from silx.gui.widgets.RangeSlider import RangeSlider

from darfix.gui.utils.rangeSlider import RangeSliderWithSpinBox


@pytest.fixture
def widget(qtapp) -> RangeSliderWithSpinBox:  # noqa F811
    w = RangeSliderWithSpinBox()
    return w


@pytest.fixture
def min_spin_box(widget) -> qt.QDoubleSpinBox:
    return widget._RangeSliderWithSpinBox__spinBoxMin


@pytest.fixture
def max_spin_box(widget) -> qt.QDoubleSpinBox:
    return widget._RangeSliderWithSpinBox__spinBoxMax


@pytest.fixture
def slider(widget) -> RangeSlider:
    return widget._RangeSliderWithSpinBox__slider


def test_set_range_updates_spins_and_slider(widget, slider, min_spin_box, max_spin_box):
    vmin, vmax = -10.0, 10.0
    widget.setRange(vmin, vmax)

    # Check spin boxes
    assert min_spin_box.value() == pytest.approx(vmin)
    assert max_spin_box.value() == pytest.approx(vmax)

    # Check slider
    assert slider.getMinimum() == pytest.approx(vmin)
    assert slider.getMaximum() == pytest.approx(vmax)
    smin, smax = slider.getValues()
    assert smin == pytest.approx(vmin)
    assert smax == pytest.approx(vmax)


def test_min_spin_box(widget, min_spin_box, qtapp):  # noqa F811
    widget.setRange(-2.0, 2.0)
    listener = SignalListener()
    widget.sigValueChanged.connect(listener)

    min_spin_box.setValue(0.0)
    min_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(0)
    numpy.testing.assert_allclose(listener.arguments(0), widget.getValues())
    assert vmin == pytest.approx(0.0)
    assert vmax == pytest.approx(2.0)

    min_spin_box.setValue(-20.0)
    min_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(1)
    numpy.testing.assert_allclose(listener.arguments(1), widget.getValues())
    assert vmin == pytest.approx(-20.0)
    assert vmax == pytest.approx(2.0)
    assert widget.getRange()[0] == pytest.approx(-20.0)

    min_spin_box.setValue(20.0)
    min_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(2)
    assert vmin == pytest.approx(2.0)  # max value is maxspin value
    assert vmax == pytest.approx(2.0)


def test_max_spin_box(widget, max_spin_box, qtapp):  # noqa F811
    widget.setRange(-2.0, 2.0)
    listener = SignalListener()
    widget.sigValueChanged.connect(listener)

    max_spin_box.setValue(1.0)
    max_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(0)
    numpy.testing.assert_allclose(listener.arguments(0), widget.getValues())
    assert vmin == pytest.approx(-2.0)
    assert vmax == pytest.approx(1.0)

    max_spin_box.setValue(20.0)
    max_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(1)
    numpy.testing.assert_allclose(listener.arguments(1), widget.getValues())
    assert vmin == pytest.approx(-2.0)
    assert vmax == pytest.approx(20.0)
    assert widget.getRange()[1] == pytest.approx(20.0)

    max_spin_box.setValue(-20.0)
    max_spin_box.editingFinished.emit()
    qtapp.processEvents()

    vmin, vmax = listener.arguments(2)
    assert vmin == pytest.approx(-2.0)  # max value is maxspin value
    assert vmax == pytest.approx(-2.0)  # min value is minspin value


def test_slider(widget, slider, min_spin_box, max_spin_box, qtapp):  # noqa F811
    widget.setRange(0.0, 10.0)
    listener = SignalListener()
    widget.sigValueChanged.connect(listener)

    slider.setValues(3.0, 7.0)
    qtapp.processEvents()

    smin, smax = listener.arguments(0)
    assert smin == pytest.approx(3.0)
    assert smax == pytest.approx(7.0)
    assert smin == pytest.approx(min_spin_box.value())
    assert smax == pytest.approx(max_spin_box.value())


def test_invalid_range_raises(widget):
    with pytest.raises(ValueError):
        widget.setRange(10.0, 5.0)
