from __future__ import annotations

from silx.gui import qt

from darfix import dtypes
from darfix.core.utils import OperationAborted
from darfix.gui.utils.message import missing_dataset_msg
from darfix.gui.utils.standardButtonBox import StandardButtonBox
from orangecontrib.darfix.widgets.datasetWidgetBase import DatasetWidgetBase


class OperationWidgetBase(DatasetWidgetBase, openclass=True):
    """
    Base class for an Orange Ewoks Widget that can run one or more operations
    and that manage a 'Reset' and an 'Abort' button.

    Note that the 'Abort' button will work only if ewoks task implement
    the `cancel` abstract method.
    """

    want_main_area = True
    want_control_area = False

    sigOperationApplied = qt.Signal(dtypes.Dataset)

    def __init__(
        self,
        buttonTypes: qt.QDialogButtonBox.StandardButton = qt.QDialogButtonBox.StandardButton.NoButton,
    ):
        super().__init__()

        # buttons
        self.__buttons = StandardButtonBox(parent=self, additionalButtons=buttonTypes)
        self.__buttons.okButton.setEnabled(False)

        self.__widget = self.createMainWidget(self.get_default_input_values())
        self.mainArea.layout().addWidget(self.__widget)
        self.layout().addWidget(self.__buttons)

        self.set_dynamic_input("copy_dataset", True)

        self.__saveAction = self.getDatasetMenu().addAction("Save")
        self.__saveAction.setDisabled(True)
        self.__saveAction.setShortcut("Ctrl+Shift+S")

        # connect signal / slot
        self.__buttons.applyButton.clicked.connect(self.__onApplyClicked)
        self.__buttons.okButton.clicked.connect(self.__onOkClicked)
        self.__buttons.resetButton.clicked.connect(self.__onResetClicked)
        self.__buttons.abortButton.clicked.connect(self.__onAbortClicked)
        self.__saveAction.triggered.connect(self.__onSaveDataset)
        self.datasetChanged.connect(self.__onDatasetChanged)

    @property
    def buttons(self) -> StandardButtonBox:
        return self.__buttons

    @property
    def mainWidget(self) -> qt.QWidget:
        return self.__widget

    @property
    def __backupDataset(self) -> dtypes.Dataset | None:
        return self.get_task_input_value("dataset", None)

    def saveMainWidget(self) -> None:
        """
        inherited class need to override this method.

        Save parameters as default inputs with `set_default_input` here.
        """
        raise NotImplementedError("This is an abstract method.")

    def createMainWidget(self, default_inputs: dict) -> qt.QWidget:
        """
        inherited class need to override this method.

        Instantiate and setup main widget here.

        :param default_inputs: Dictionary containing the default inputs that are set.
        :return : An instance of the created main widget
        """
        raise NotImplementedError("This is an abstract method.")

    def __onOkClicked(self) -> None:
        if len(self.get_task_outputs()) == 0:
            # if no output at all this is an unexpected behaviour
            raise RuntimeError("Cannot go to next step because outputs are empty.")
        self.close()
        self.propagate_downstream()

    def __onResetClicked(self):
        self.reset()

    def __onAbortClicked(self):
        self.cancel_running_task()

    def __onApplyClicked(self):
        self.__buttons.applyButton.setDisabled(True)
        self.saveMainWidget()
        self.__buttons.setIsComputing(True)
        self.execute_ewoks_task_without_propagation()

    def __onSaveDataset(self):
        dataset = self.get_task_output_value("dataset", None)
        # All exception below are unexpected as save action is disabled if no successful output
        assert dataset is not None, "output dataset should not be None"
        assert isinstance(
            dataset, dtypes.Dataset
        ), f"Dataset bad type : {type(dataset)}"
        assert dataset.dataset is not None, "output image stack should not be None"
        imgDataset = dataset.dataset
        if imgDataset is not None:
            filename, _ = qt.QFileDialog().getSaveFileName(
                None,
                "Save Darfix dataset",
                filter="Darfix HDF5 file (*.h5)",
            )
            if filename:
                imgDataset.save(filename)
        else:
            missing_dataset_msg()

    def __onDatasetChanged(self):
        self.__buttons.okButton.setDisabled(True)
        self.__buttons.applyButton.setEnabled(True)
        self.__saveAction.setDisabled(True)

    def reset(self):
        self.setDataset(self.__backupDataset)

    def task_output_changed(self) -> None:
        self.__buttons.setIsComputing(False)
        if self.task_succeeded:
            self.__buttons.okButton.setEnabled(True)

            output = self.get_task_output_value("dataset", None)
            if output is None:
                raise RuntimeError(
                    "Unexpected error : Task succeeded but output is None"
                )
            if output is self.get_task_input_value("dataset", None):
                raise RuntimeError("Unexpected error : Input and Output are the same.")

            self.__saveAction.setEnabled(True)

            self.sigOperationApplied.emit(output)
        else:
            self.__buttons.applyButton.setEnabled(True)

    def isAborted(self) -> bool:
        return isinstance(self.task_exception, OperationAborted)

    def closeEvent(self, evt) -> None:
        super().closeEvent(evt)
        self.saveMainWidget()
