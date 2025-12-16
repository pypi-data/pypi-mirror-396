from __future__ import annotations

import logging

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.io.dictdump import dicttonx

from darfix.core.moment_types import MomentType

from ...core.grainplot import GrainPlotMaps
from ...core.grainplot import generate_grain_maps_nxdict
from ..utils.utils import select_output_hdf5_file_with_dialog
from .mosaicityWidget import MosaicityWidget
from .utils import MapType
from .utils import add_image_with_transformation

_logger = logging.getLogger(__file__)


class GrainPlotWidget(qt.QMainWindow):
    """
    Widget to show a series of maps for the analysis of the data.
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self._grainPlotMaps: GrainPlotMaps | None = None
        self._plots: list[Plot2D] = []

        self._mapTypeComboBox = qt.QComboBox()
        self._mapTypeComboBox.addItems([map_type.value for map_type in MapType])
        self._mapTypeComboBox.currentTextChanged.connect(self._updatePlot)

        self._plotWidget = qt.QWidget()
        plotsLayout = qt.QHBoxLayout()
        self._plotWidget.setLayout(plotsLayout)
        widget = qt.QWidget(parent=self)
        layout = qt.QVBoxLayout()

        self._mosaicity_widget = MosaicityWidget()

        self._exportButton = qt.QPushButton("Export maps")
        self._exportButton.setDefault(False)
        self._exportButton.clicked.connect(self.exportMaps)

        self._messageWidget = qt.QLabel("No dataset in input.")

        layout.addWidget(self._mapTypeComboBox)
        layout.addWidget(self._plotWidget)
        layout.addWidget(self._mosaicity_widget)
        layout.addWidget(self._messageWidget)
        layout.addWidget(self._exportButton)
        self._plotWidget.hide()
        self._mosaicity_widget.hide()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self._mapTypeComboBox.setDisabled(True)
        self._exportButton.setDisabled(True)

    def setMessage(self, message: str):
        self._messageWidget.setText(message)

    def setGrainPlotMaps(self, grainPlotMaps: GrainPlotMaps):

        self._grainPlotMaps = grainPlotMaps

        for i in reversed(range(self._plotWidget.layout().count())):
            self._plotWidget.layout().itemAt(i).widget().setParent(None)

        self._plots.clear()
        for dim in self._grainPlotMaps.dims.values():
            plot = Plot2D(parent=self)
            plot.setKeepDataAspectRatio(True)
            plot.setGraphTitle(self._grainPlotMaps.title + "\n" + dim.name)
            plot.setDefaultColormap(Colormap(name="viridis"))
            self._plots.append(plot)
            self._plotWidget.layout().addWidget(plot)

        # Enable mosaicity if ndim >= 2
        if self._grainPlotMaps.dims.ndim >= 2:
            self._mosaicity_widget.setGrainPlotMaps(self._grainPlotMaps)
            self._mapTypeComboBox.model().item(4).setEnabled(True)
            self._mapTypeComboBox.setCurrentText(MapType.MOSAICITY.value)
        else:
            self._mapTypeComboBox.model().item(4).setEnabled(False)
            self._mapTypeComboBox.setCurrentText(MapType.COM.value)
        # Force plot update since setCurrentText does not fire currentTextChanged if the text is the same
        # https://doc.qt.io/qt-6/qcombobox.html#currentTextChanged
        self._updatePlot(self._mapTypeComboBox.currentText())

        self._messageWidget.hide()
        self._mapTypeComboBox.setEnabled(True)
        self._exportButton.setEnabled(True)
        self._exportButton.setDefault(False)

    def _updatePlot(self, raw_map_type: str):
        """
        Update shown plots in the widget
        """

        map_type = MapType(raw_map_type)
        if map_type == MapType.MOSAICITY:
            self._mosaicity_widget.show()
            self._plotWidget.hide()
            return

        if self._grainPlotMaps is None:
            return

        moment_type = MomentType(raw_map_type)

        moments = self._grainPlotMaps.moments_dims
        self._mosaicity_widget.hide()
        self._plotWidget.show()
        for i, plot in enumerate(self._plots):
            self._addImage(plot, moments[i][moment_type])

    def _generate_maps_nxdict(self) -> dict:
        orientation_dist_data = self._mosaicity_widget.getOrientationDist()

        return generate_grain_maps_nxdict(
            self._grainPlotMaps,
            self._mosaicity_widget.getMosaicity(),
            orientation_dist_data,
        )

    def exportMaps(self):
        """
        Creates dictionary with maps information and exports it to a nexus file
        """
        nx = self._generate_maps_nxdict()

        filename = select_output_hdf5_file_with_dialog()
        if filename:
            dicttonx(nx, filename)

    def _addImage(self, plot, image):
        if self._grainPlotMaps is None:
            transformation = None
        else:
            transformation = self._grainPlotMaps.transformation
        add_image_with_transformation(plot, image, transformation)
