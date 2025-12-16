from __future__ import annotations

import logging
from typing import Any

from ewokscore.missing_data import is_missing_data
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt

from darfix import dtypes
from darfix.core.dataset import ImageDataset
from darfix.core.dimension import Dimension
from darfix.core.dimension import find_dimensions_from_metadata
from darfix.core.fscan_parser import fscan_get_dimensions
from darfix.gui.dimensionsWidget import DimensionItem
from darfix.gui.dimensionsWidget import DimensionWidget
from darfix.tasks.dimensiondefinition import DimensionDefinition
from darfix.tasks.dimensiondefinition import get_dimensions_error
from orangecontrib.darfix.widgets.datasetWidgetBase import DatasetWidgetBase

_logger = logging.getLogger(__file__)

NO_DATASET_ERROR_MSG = "No dataset. Please run data selection widget."


class DimensionWidgetOW(DatasetWidgetBase, ewokstaskclass=DimensionDefinition):
    """
    Widget used to define the calibration of the experimentation (select motor
    positions...)
    """

    name = "Dimension definition"
    id = "orange.widgets.darfix.dimensiondefinition"
    description = "Define the motor axes used during the acquisition"
    icon = "icons/param_dims.svg"

    _ewoks_inputs_to_hide_from_orange = ("dims", "tolerance", "is_zigzag")

    priority = 4
    keywords = ["dataset", "calibration", "motor", "angle", "geometry"]
    want_main_area = False

    def __init__(self):
        super().__init__()
        self._widget = DimensionWidget(parent=self)
        self.controlArea.layout().addWidget(self._widget)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self.buttons = qt.QDialogButtonBox(parent=self)
        self.buttons.setStandardButtons(types)
        self.controlArea.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self._execute_fit)
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(False)

        # connect Signal/SLOT
        self._widget.sigFindDimensions.connect(self._findDimensions)
        self._widget.sigUpdateDimensions.connect(self.onUpdateDimensions)
        # set up
        self._initDims()

        tolerance = self.get_task_input_value("tolerance")
        if not is_missing_data(tolerance):
            with block_signals(self._widget):
                self._widget.setTolerance(tolerance)

        self.datasetChanged.connect(self.onDatasetChanged)

    def onUpdateDimensions(self):
        dataset = self.get_task_input_value("dataset")
        if is_missing_data(dataset):
            return

        err_msg = get_dimensions_error(
            dataset.dataset,
            (dim.toDimension() for dim in self._widget.dims.values()),
        )
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled((err_msg is None))
        if err_msg is None:
            self._widget.setTipsLabelText(
                "\u2705 Dimensions are good. Confirm with 'OK' button to go to next step."
            )
        else:
            self._widget.setTipsLabelText("\u274c " + err_msg)

    def onDatasetChanged(self, dataset: dtypes.Dataset):
        """
        Input signal to set the dataset.
        """

        # TODO : How we handle zigzag mode need to be review somehow because as we change the dataset and metadata
        # but we do not make a copy, i cannot rerun twice the task
        # So that's a patch for now
        self.Information.clear()
        self.controlArea.setEnabled(True)

        fscan_parameters = fscan_get_dimensions(dataset.dataset)
        if fscan_parameters is not None:
            is_zigzag, dims = fscan_parameters
            self._widget.setDims(dims)
            self._widget.setZigzagMode(is_zigzag)

            fscan_err_msg = get_dimensions_error(dataset.dataset, dims.values())
            if fscan_err_msg is None:
                self._widget.setTipsLabelText(
                    "\u2705 Dimensions are defined in metadata. All is good ! Confirm with 'OK' button to go to next step."
                )
                # Disable inputs only when the dim rows are added
                self._widget.setEnableInputs(False)
            else:
                self._widget.setEnableInputs(True)
                _logger.error(
                    f"Find fscan_parameters in hdf5 file but validation failed : {fscan_err_msg}"
                )
        else:
            err_msg = get_dimensions_error(
                dataset.dataset,
                (dim.toDimension() for dim in self._widget.dims.values()),
            )
            self._widget.setEnableInputs(True)

            if err_msg is None:
                self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(True)
                self._widget.setTipsLabelText(
                    "\u2705 Dimensions are good. Confirm with 'OK' button to go to next step."
                )
            else:
                self._widget.setZigzagMode(False)
                self._widget.setDims({})
                self._widget.setTipsLabelText(
                    "\U0001f4a1 Adjust tolerance and click on 'Find dimensions'."
                )

    def closeEvent(self, event):
        self._save()

    def _initDims(self):
        try:
            # dims values are Dimension provided as dict (to save settings in a readable manner).
            # So when loading them we must convert them back to Dimension
            raw_dims = self.get_task_input_value("dims")
            if not is_missing_data(raw_dims):
                dims = convert_dim_from_dict_to_Dimension(raw_dims)
                with block_signals(self._widget):
                    self._widget.setDims(dims)
            self._widget.setZigzagMode(self.get_task_input_value("is_zigzag", False))
            self._widget.setEnableInputs(False)
        except ValueError as e:
            qt.QMessageBox.warning(self, "Fail to setup dimension definition", str(e))

    def _save(self):
        pickable_dims = make_dims_picklable(self._widget.dims)
        self.set_default_input("dims", pickable_dims)
        self.set_default_input("is_zigzag", self._widget.isZigzagMode)
        self.set_default_input("tolerance", self._widget.getTolerance())

    def _execute_fit(self):
        if not is_missing_data(self.get_task_input_value("dataset")):
            self._save()
            self.execute_ewoks_task_without_propagation()
        else:
            self._provideFitFeedback(
                False,
                error=NO_DATASET_ERROR_MSG,
                dataset=None,
            )

    def task_output_changed(self) -> None:
        dataset = self.get_task_output_value("dataset")
        if is_missing_data(dataset):
            darfix_dataset = None
        else:
            if not isinstance(dataset, dtypes.Dataset):
                raise dtypes.DatasetTypeError(dataset)
            darfix_dataset = dataset.dataset
        self._provideFitFeedback(
            success=self.task_succeeded,
            error=self.task_exception,
            dataset=darfix_dataset,
        )

        return super().task_output_changed()

    def _provideFitFeedback(self, success: bool, error: str, dataset):
        msg = qt.QMessageBox()
        if success:

            # TODO : How we handle zigzag mode need to be review somehow because as we change the dataset and metadata
            # but we do not make a copy, i cannot rerun twice the task
            # So that's a patch for now
            self.controlArea.setDisabled(True)
            self.information(
                "Dimension can be defined only once. If you want to redo, re-run previous data selection widget."
            )

            self.propagate_downstream()
            self.accept()
        else:
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText(f"Error: {error}")
            msg.setWindowTitle("Dimension fit failed!")
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec()

    def _findDimensions(
        self,
    ):
        dataset = self.get_task_input_value("dataset")
        if is_missing_data(dataset):
            _logger.error(NO_DATASET_ERROR_MSG)
            return
        assert isinstance(dataset.dataset, ImageDataset)

        metadata = dataset.dataset.metadata_dict
        dims = find_dimensions_from_metadata(metadata, self._widget.getTolerance())
        self._widget.setDims(dims)


def make_dims_picklable(dims: dict[DimensionItem]):
    if not isinstance(dims, dict):
        raise TypeError("dims should be an instance of dict")
    # convert AcquisitionDims to dict if necessary
    return {value.axis: make_dim_picklable(value) for key, value in dims.items()}


def make_dim_picklable(dim: DimensionItem) -> dict:
    return dim.toDimension().to_dict()


def convert_dim_from_dict_to_Dimension(
    dims: dict[int, dict[int, Any]],
) -> dict[int, Dimension]:
    return {key: Dimension.from_dict(value) for key, value in dims.items()}
