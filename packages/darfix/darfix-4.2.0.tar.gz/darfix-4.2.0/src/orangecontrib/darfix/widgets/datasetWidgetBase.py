from __future__ import annotations

from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from silx.gui import qt

from darfix import dtypes
from darfix.core.dataset import ImageDataset
from darfix.gui.utils.message import show_error_msg


class DatasetWidgetBase(OWEwoksWidgetOneThread, openclass=True):
    """
    Orange Ewoks Widget with a "dataset" dynamic input.

    Base class manage

    - mainArea enable / disable when a task is running.
    - load / save dataset menu
    - `setDataset()` public method
    - `datasetChanged` signal : Children should use this signal instead of `handleNewSignals`
    """

    datasetChanged = qt.Signal(dtypes.Dataset)

    def __init__(self):
        super().__init__()
        self.task_executor.finished.connect(self.__onFinishTask)
        self.task_executor.started.connect(self.__onStartEwoksTask)

        self.__datasetMenu: qt.QMenu = self.menuBar().addMenu("&Dataset")

        loadAction = self.__datasetMenu.addAction("Load")
        loadAction.setShortcut("Ctrl+O")

        loadAction.triggered.connect(self._onLoadDataset)

    def handleNewSignals(self) -> None:
        self._updateDataset(True)
        # super().handleNewSignals() is not called because we do not want to trigger workflow

    def setDataset(self, dataset: dtypes.Dataset | None, pop_up: bool = False) -> None:
        self.set_dynamic_input("dataset", dataset)
        self._updateDataset(pop_up)

    def _updateDataset(self, pop_up: bool) -> None:
        dataset = self._getDatasetTaskInput()
        if dataset is None:
            return
        if not isinstance(dataset, dtypes.Dataset):
            show_error_msg(f"Bad dataset type : {type(dataset)}")
            return
        self.datasetChanged.emit(dataset)
        if pop_up:
            self.open()

    def _getDatasetTaskInput(self) -> dtypes.Dataset | None:
        return self.get_task_input_value("dataset", None)

    def _onLoadDataset(self):
        filename, _ = qt.QFileDialog().getOpenFileName(
            None, "Open Darfix dataset save", filter="Darfix HDF5 file (*.h5)"
        )
        if filename:
            dataset = dtypes.Dataset(ImageDataset.load(filename))
            self.setDataset(dataset)

    def __onFinishTask(self):
        if self.mainArea is not None:
            self.mainArea.setEnabled(True)

    def __onStartEwoksTask(self):
        if self.mainArea is not None:
            self.mainArea.setDisabled(True)

    def getDatasetMenu(self) -> qt.QMenu:
        return self.__datasetMenu
