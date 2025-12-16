from __future__ import annotations

from darfix.core.noiseremoval import clean_operation_dict
from darfix.gui.noiseremoval.noise_removal_widget import NoiseRemovalWidget
from darfix.tasks.noiseremoval import NoiseRemoval
from orangecontrib.darfix.widgets.operationWidgetBase import OperationWidgetBase


class NoiseRemovalWidgetOW(OperationWidgetBase, ewokstaskclass=NoiseRemoval):
    name = "noise removal"
    description = "A widget to perform various noise removal operations"
    icon = "icons/noise_removal.png"

    _ewoks_inputs_to_hide_from_orange = ("operations", "copy_dataset")

    def __init__(self):
        super().__init__()
        self.datasetChanged.connect(self.mainWidget.setDataset)
        self.sigOperationApplied.connect(self.mainWidget.setAppliedState)

    def createMainWidget(self, inputs: dict) -> NoiseRemovalWidget:
        widget = NoiseRemovalWidget()
        incomingOperations = inputs.get("operations", [])
        widget.setDefaultParameters(incomingOperations)
        widget.setOperationList(self.get_task_input_value("operations", []))
        return widget

    def saveMainWidget(self):
        self.set_default_input(
            "operations",
            [
                clean_operation_dict(operation)
                for operation in self.mainWidget.getOperationList()
            ],
        )

    @property
    def mainWidget(self) -> NoiseRemovalWidget:
        return super().mainWidget
