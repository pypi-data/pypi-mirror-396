from silx.gui.plot.actions import PlotAction


class FlashlightModeAction(PlotAction):
    """QAction controlling the the Flashlight Mode to highlight a portion of the mosaicity.

    :param plot: :class:`.PlotWidget` instance on which to operate
    :param parent: See :class:`QAction`
    """

    INTERACTION_MODE = "select"

    def __init__(self, plot, parent=None):
        super().__init__(
            plot,
            icon="darfix:gui/icons/flashlight",
            text="Flashlight mode",
            tooltip="Highlight a portion of the mosaicity",
            triggered=self._actionTriggered,
            checkable=True,
            parent=parent,
        )
        # Listen to mode change
        self.plot.sigInteractiveModeChanged.connect(self._modeChanged)
        # Init the state
        self._modeChanged(None)

    def _modeChanged(self, source):
        modeDict = self.plot.getInteractiveMode()
        self.setChecked(modeDict["mode"] == self.INTERACTION_MODE)

    def _actionTriggered(self, checked=False):
        plot = self.plot
        if plot is not None:
            plot.setInteractiveMode(self.INTERACTION_MODE, source=self)
