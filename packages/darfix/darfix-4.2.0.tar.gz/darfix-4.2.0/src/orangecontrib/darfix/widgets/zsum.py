from __future__ import annotations

from ewokscore.missing_data import MISSING_DATA

from darfix.gui.zSumWidget import ZSumWidget
from darfix.tasks.zsum import ZSum
from orangecontrib.darfix.widgets.datasetWidgetBase import DatasetWidgetBase


class ZSumWidgetOW(DatasetWidgetBase, ewokstaskclass=ZSum):
    """
    Widget that compute and display the Z-sum of a dataset
    """

    name = "z sum"
    icon = "icons/zsum.svg"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("indices", "selected_axis")

    def __init__(self):
        super().__init__()

        self._widget = ZSumWidget(parent=self)
        self.mainArea.layout().addWidget(self._widget)
        # connect signal / slot
        self._widget.sigAxisChanged.connect(self._onAxisChanged)
        self._widget.sigResetFiltering.connect(self._onUncheckFiltering)

        self.datasetChanged.connect(self.onDatasetChanged)
        self.datasetChanged.connect(self._widget.setDataset)

    def onDatasetChanged(self) -> None:
        self.set_dynamic_input("selected_axis", None)
        self.execute_ewoks_task()

    def task_output_changed(self):
        z_sum = self.get_task_output_value("zsum", MISSING_DATA)
        if z_sum is not MISSING_DATA:
            self._widget.setZSum(z_sum)

    def _onAxisChanged(self, selectedAxis: int):
        self.set_default_input("indices", self._widget.indices)
        self.set_dynamic_input("selected_axis", selectedAxis)
        self.execute_ewoks_task_without_propagation()

    def _onUncheckFiltering(self):
        self.set_default_input("indices", None)
        self.set_dynamic_input("selected_axis", None)
        self.execute_ewoks_task_without_propagation()
