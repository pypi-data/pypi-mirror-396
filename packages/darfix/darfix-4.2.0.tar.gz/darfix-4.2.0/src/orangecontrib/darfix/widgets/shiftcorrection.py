from __future__ import annotations

import numpy
from silx.gui import qt

from darfix.gui.shiftcorrection.shiftCorrectionWidget import ShiftCorrectionWidget
from darfix.tasks.shiftcorrection import ShiftCorrection
from orangecontrib.darfix.widgets.operationWidgetBase import OperationWidgetBase


class ShiftCorrectionWidgetOW(OperationWidgetBase, ewokstaskclass=ShiftCorrection):
    """
    Widget to make the shift correction of a dataset.
    """

    name = "shift correction"
    description = "A widget to perform shift correction"
    icon = "icons/shift_correction.svg"

    _ewoks_inputs_to_hide_from_orange = (
        "shift",
        "selected_axis",
        "selected_index",
        "copy_dataset",
    )

    def __init__(self):
        super().__init__()
        qt.QLocale.setDefault(qt.QLocale("en_US"))
        self.datasetChanged.connect(self.mainWidget.setDataset)
        self.sigOperationApplied.connect(self.mainWidget.updateDataset)

    def createMainWidget(self, default_inputs: dict) -> ShiftCorrectionWidget:
        widget = ShiftCorrectionWidget()
        widget.setCorrectionInputs(
            default_inputs.get("shift", (0, 0)),
            default_inputs.get("selected_axis", None),
        )
        return widget

    def saveMainWidget(self) -> dict:
        inputs = self.mainWidget.getCorrectionInputs()
        for key, value in inputs.items():
            if isinstance(value, numpy.ndarray):
                value = value.tolist()
            self.set_default_input(key, value)

    @property
    def mainWidget(self) -> ShiftCorrectionWidget:
        return super().mainWidget
