from __future__ import annotations

import logging
import queue

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from darfix import config
from darfix import dtypes
from darfix.core.noiseremoval import BackgroundType
from darfix.core.noiseremoval import NoiseRemovalOperation
from darfix.core.noiseremoval import add_background_data_into_operation
from darfix.core.noiseremoval import apply_noise_removal_operation
from darfix.core.noiseremoval import operation_to_str
from darfix.core.state_of_operation import Operation
from darfix.gui.operationThread import OperationThread

from .operation_list_widget import OperationListWidget
from .parameters_widget import ParametersWidget

_logger = logging.getLogger(__name__)


class PreviewThread(qt.QThread):
    """Execute on the fly computation when plot is updated in order to preview the noise removal for that frame"""

    sigDataReady = qt.Signal(numpy.ndarray)
    """
    Emitted when one processed frame data has been computed. This might not be the current frame displayed but the latest computed one.
    Can be emitted several times during one run.
    """

    QUEUE_TIMEOUT = 0.2

    def __init__(self, parent):
        super().__init__(parent)
        self.queue = queue.Queue()

    def _onTheFlyComputation(self):
        """
        Process operations in image and emit `sigDataReady` signals while the queue is NOT empty for at least `QUEUE_TIMEOUT` sec.
        The Queue will continue growing until the user release the slider and the processing is done.

        raise queue.Empty when exit
        """
        while True:
            img, ops = self.queue.get(timeout=self.QUEUE_TIMEOUT)
            if self.queue.qsize() > 1:
                # skip this image : process is too slow
                continue
            for op in ops:
                apply_noise_removal_operation(img, op)
            self.sigDataReady.emit(img)

    def run(self):
        try:
            self._onTheFlyComputation()
        except queue.Empty:
            # Thread will finish as timeout reached
            pass


class NoiseRemovalWidget(qt.QWidget):
    """
    Widget to apply noise removal from a dataset.

    Background computation is done in a dedicated thread.

    All operations are done "on the fly" in the main thread on the current active image of the stack.

    For now it can apply both background subtraction and hot pixel removal and mask.
    For background subtraction the user can choose the background to use:
    dark frames, low intensity data or all the data. From these background
    frames, an image is computed either using the mean or the median.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._incomingOperations: list[NoiseRemovalOperation] = []
        self._dataset: dtypes.Dataset | None = None
        self.setWindowFlags(qt.Qt.WindowType.Widget)

        self._parametersWidget = ParametersWidget()
        self._plot = Plot2D(self)

        self._browser = HorizontalSliderWithBrowser(self)
        self._browser.setRange(0, 0)
        self._browser.setEnabled(False)

        self._plot.setKeepDataAspectRatio(True)

        self._operationList = OperationListWidget()

        layout = qt.QVBoxLayout()
        layout.addWidget(self._plot)
        layout.addWidget(self._browser)
        layout.addWidget(self._parametersWidget)
        layout.addWidget(self._operationList)
        self.setLayout(layout)

        self._backgroundComputationThread: OperationThread | None = None
        self._previewThread = PreviewThread(self)

        # Add connections
        self._parametersWidget.computeBS.clicked.connect(
            self._launchBackgroundSubtraction
        )
        self._parametersWidget.computeHP.clicked.connect(self._launchHotPixelRemoval)
        self._parametersWidget.computeTP.clicked.connect(self._launchThresholdRemoval)
        self._parametersWidget.computeMR.clicked.connect(self._launchMaskRemoval)
        self._browser.valueChanged.connect(self.refreshPlot)
        self._operationList.sigOneOperationRemoved.connect(self.refreshPlot)
        self._previewThread.sigDataReady.connect(self._onOneFramePreviewReady)
        self._previewThread.finished.connect(self._onPreviewFinished)

    def setAppliedState(self, outputDataset: dtypes.Dataset):
        """
        Put widget on a state where every controls and operation list are disabled.
        Update dataset to `outputDataset`
        Operations are not applied online because we considere the input dataset was updated

        Call `setDataset` to exit from applied mode.
        """
        self._dataset = outputDataset
        self._operationList.setDisabled(True)
        self._parametersWidget.setDisabled(True)

    def setDataset(self, dataset: dtypes.Dataset):
        """Saves the dataset and updates the stack with the dataset data."""

        self._plot.clear()

        self._dataset = dataset

        if self._imgDataset.title != "":
            self._plot.setTitleCallback(lambda idx: self._imgDataset.title)

        self._initPlot()

        self._parametersWidget.computeBS.show()
        self._parametersWidget.computeHP.show()
        self._parametersWidget.computeTP.show()
        self._parametersWidget.computeMR.show()

        self._parametersWidget.setEnabled(True)
        self._operationList.setEnabled(True)

        """
        Sets the available background for the user to choose.
        """
        self._parametersWidget.bsBackgroundCB.clear()
        if dataset.bg_dataset is not None:
            self._parametersWidget.bsBackgroundCB.addItem(
                BackgroundType.DARK_DATA.value
            )
        if dataset.bg_indices is not None:
            self._parametersWidget.bsBackgroundCB.addItem(
                BackgroundType.UNUSED_DATA.value
            )
        self._parametersWidget.bsBackgroundCB.addItem(BackgroundType.DATA.value)

        opersations = self._operationList.getOperations()

        if (
            len(opersations) > 0
            and qt.QMessageBox.question(
                self,
                "Keep operation list ?",
                "Do you want to restore these operations ?\n\n - "
                + "\n - ".join([operation_to_str(op) for op in opersations]),
            )
            == qt.QMessageBox.StandardButton.Yes
        ):
            for operation in opersations:
                if operation["type"] is Operation.BS:
                    self._computeBackgroundAsync(operation)
        else:
            self._operationList.clear()

    def _launchBackgroundSubtraction(self):
        operation = NoiseRemovalOperation(
            type=Operation.BS,
            parameters={
                "method": self._parametersWidget.bsMethodsCB.currentText(),
                "background_type": self._parametersWidget.bsBackgroundCB.currentText(),
            },
        )
        self._operationList.append(operation)
        self._computeBackgroundAsync(operation)

    def _computeBackgroundAsync(self, operation: NoiseRemovalOperation):

        assert (
            self._backgroundComputationThread is None
        ), "Computation thread is expected to be None."

        self._parametersWidget.setDisabled(True)
        self._browser.setDisabled(True)
        self._parametersWidget.computeBS.setWaiting(True)

        # Here the background image data is computed.
        self._backgroundComputationThread = OperationThread(
            self, add_background_data_into_operation
        )
        self._backgroundComputationThread.setArgs(self._dataset, operation)
        self._backgroundComputationThread.finished.connect(
            self._onBackgroundComputationFinish
        )
        self._backgroundComputationThread.start()

    def _onBackgroundComputationFinish(self):
        self._parametersWidget.setEnabled(True)
        self._browser.setEnabled(True)
        self._parametersWidget.computeBS.setWaiting(False)

        self._backgroundComputationThread = None

        self.refreshPlot()

    def _launchHotPixelRemoval(self):
        size = self._parametersWidget.hpSizeCB.currentText()

        operation = NoiseRemovalOperation(
            type=Operation.HP,
            parameters={
                "kernel_size": int(size),
            },
        )
        self._operationList.append(operation)
        self.refreshPlot()

    def _launchThresholdRemoval(self):
        bottom_threshold = self._parametersWidget.bottomLE.text()
        top_threshold = self._parametersWidget.topLE.text()
        try:
            bottom_threshold = int(bottom_threshold)
        except ValueError:
            bottom_threshold = None
        try:
            top_threshold = int(top_threshold)
        except ValueError:
            top_threshold = None

        operation = NoiseRemovalOperation(
            type=Operation.THRESHOLD,
            parameters={
                "bottom": bottom_threshold,
                "top": top_threshold,
            },
        )
        self._operationList.append(operation)
        self.refreshPlot()

    def _launchMaskRemoval(self):
        mask = self._plotWidget.getSelectionMask()
        if mask is None:
            return
        operation = NoiseRemovalOperation(
            type=Operation.MASK,
            parameters={"mask": mask},
        )
        self._operationList.append(operation)
        self.refreshPlot()

    def refreshPlot(self):
        frameNumber = self._browser.value()
        img = self._plot.getActiveImage()
        if img is None:
            # No active image -> nothing to refresh
            return

        if (
            self._operationList.isEnabled()
            and len(self._operationList.getOperations()) > 0
        ):
            # processing on the fly
            data = self._imgDataset.as_array3d()[frameNumber].copy()
            self._previewThread.queue.put((data, self._operationList.getOperations()))
            if not self._previewThread.isRunning():
                # Re-start work if timeout reached
                self._previewThread.start()
        else:
            # show unprocessed images
            img.setData(self._imgDataset.as_array3d()[frameNumber], copy=False)

    def _onPreviewFinished(self):
        self._plot.clearMarkers()

    def _onOneFramePreviewReady(self, data):
        img = self._plot.getActiveImage()
        if img is None:
            return
        self._plot.clearMarkers()
        marker = self._plot.addMarker(
            self._plot.getGraphXLimits()[0],
            self._plot.getGraphYLimits()[1],
            symbol="",
            text="processing...",
            color="white",
        )
        marker.setBackgroundColor([0.0, 0.0, 0.0, 0.5])
        img.setData(data, copy=False)

    def _initPlot(self):
        if self._imgDataset is None:
            self._plot.clear()
            self._browser.setDisabled(True)
            return
        self._browser.setRange(0, self._imgDataset.nframes - 1)
        self._browser.setEnabled(True)
        self._plot.addImage(
            self._imgDataset.as_array3d()[0],
            colormap=Colormap(
                name=config.DEFAULT_COLORMAP_NAME,
                normalization=config.DEFAULT_COLORMAP_NORM,
            ),
        )

    def setDefaultParameters(self, operations: list[NoiseRemovalOperation]):
        """
        Set default values un widget parameters based on operations list

        """
        self._parametersWidget.set_default_values(operations)

    def getOperationList(self):
        return self._operationList.getOperations()

    def setOperationList(self, operations: list[NoiseRemovalOperation]):
        self._operationList.clear()
        self._operationList.extend(operations)

    def hasIncomingOperations(self) -> bool:
        return len(self._incomingOperations) > 0

    def getIncomingOperations(self) -> tuple[NoiseRemovalOperation]:
        return self._incomingOperations

    @property
    def _imgDataset(self) -> dtypes.ImageDataset:
        return self._dataset.dataset

    @property
    def _plotWidget(self):
        return self._plot
