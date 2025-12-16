from __future__ import annotations

from silx.gui import qt

from ...core.noiseremoval import NoiseRemovalOperation
from ...core.noiseremoval import operation_to_str


class OperationListWidget(qt.QWidget):
    """Keeps the history of noise removal operations and displays them in a QListWidget"""

    sigOneOperationRemoved = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = qt.QVBoxLayout()
        assert layout is not None
        self._listWidget = qt.QListWidget()
        self._listWidget.setSelectionMode(
            qt.QAbstractItemView.SelectionMode.SingleSelection
        )
        self._listWidget.hide()
        self._checkbox = qt.QCheckBox("Show operations")

        layout.addWidget(self._checkbox)
        layout.addWidget(self._listWidget)
        self.setLayout(layout)

        self._checkbox.toggled.connect(self._listWidget.setVisible)
        self._checkbox.setChecked(True)

        self._operations: list[NoiseRemovalOperation] = []

        self._listWidget.setContextMenuPolicy(
            qt.Qt.ContextMenuPolicy.ActionsContextMenu
        )

        deleteAction = qt.QAction("Delete", self)
        deleteAction.setShortcut(qt.QKeySequence.StandardKey.Delete)
        self._listWidget.addAction(deleteAction)

        # Connect Signal / Slot
        deleteAction.triggered.connect(self.__removeSelection)

    def append(self, operation: NoiseRemovalOperation):
        self._operations.append(operation)
        self._listWidget.addItem(operation_to_str(operation))

    def clear(self):
        self._operations.clear()
        self._listWidget.clear()

    def getOperations(self) -> list[NoiseRemovalOperation]:
        return list(self._operations)

    def extend(self, operations: list[NoiseRemovalOperation]):
        self._operations.extend(operations)
        for i_new_op, operation in enumerate(operations):
            self._listWidget.addItem(qt.QListWidgetItem(operation_to_str(operation)))

    def __removeSelection(self):
        """Remove selected operation (triggered by button or Delete key)."""
        row = self._listWidget.currentRow()
        if row < 0:
            return

        # remove from data
        del self._operations[row]
        # remove from list widget
        self._listWidget.removeItemWidget(self._listWidget.takeItem(row))

        self.sigOneOperationRemoved.emit()
