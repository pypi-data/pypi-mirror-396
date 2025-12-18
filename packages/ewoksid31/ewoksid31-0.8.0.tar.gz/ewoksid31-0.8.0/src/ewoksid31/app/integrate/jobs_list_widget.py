import functools
import logging
import os
from typing import Literal

import qtawesome
from ewoksjob.client.futures import CancelledError, FutureInterface, TimeoutError
from silx.gui import icons, qt

from .utils import get_scan_url
from .workflow_executor import JobItem, WorkflowExecutor

_logger = logging.getLogger(__name__)


_FutureStateStr = Literal["pending", "running", "succeeded", "failed", "cancelled"]


class _RunningIconItems:
    """Set an animated 'running' icon to all contained QListWidgetItems"""

    def __init__(self) -> None:
        self._waitIcon = icons.getWaitIcon()
        self._items: list[qt.QListWidgetItem] = list()

    def add(self, item: qt.QListWidgetItem) -> None:
        if not self._items:
            self._waitIcon.register(self)
            self._waitIcon.iconChanged.connect(self._iconChanged)

        if item not in self._items:
            item.setIcon(self._waitIcon.currentIcon())
            self._items.append(item)

    def discard(self, item: qt.QListWidgetItem) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            return

        if len(self._items) == 0:
            self._waitIcon.unregister(self)
            self._waitIcon.iconChanged.disconnect(self._iconChanged)

    def _iconChanged(self, icon: qt.QIcon) -> None:
        for item in self._items:
            item.setIcon(icon)


class JobsListWidget(qt.QWidget):

    def __init__(
        self, executor: WorkflowExecutor, parent: qt.QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._listWidget = qt.QListWidget()
        self._listWidget.setSelectionMode(
            qt.QAbstractItemView.SelectionMode.MultiSelection
        )
        self._listWidget.setDragDropMode(qt.QAbstractItemView.DragDropMode.NoDragDrop)
        self._listWidget.itemSelectionChanged.connect(self._itemSelectionChanged)

        toolbar = qt.QToolBar()
        toolbar.setToolButtonStyle(qt.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setContentsMargins(0, 0, 0, 0)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self._cancelAction = qt.QAction(self)
        self._cancelAction.setIcon(qtawesome.icon("fa6s.ban", scale_factor=0.75))
        self._cancelAction.setText("Cancel Selected")
        self._cancelAction.setEnabled(False)
        self._cancelAction.triggered.connect(self._cancelSelected)
        toolbar.addAction(self._cancelAction)

        clearAction = qt.QAction(self)
        clearAction.setIcon(qtawesome.icon("fa6s.broom", scale_factor=0.75))
        clearAction.setText("Clear Completed")
        clearAction.setToolTip("Remove all completed/failed jobs")
        clearAction.triggered.connect(self.removeFinishedItems)
        toolbar.addAction(clearAction)

        layout = qt.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(self._listWidget, stretch=1)
        layout.addWidget(toolbar)

        self._runningIconItems = _RunningIconItems()

        executor.jobSubmitted.connect(self._jobSubmitted)
        executor.jobChanged.connect(self._jobChanged)

    def removeFinishedItems(self) -> None:
        # Look for items to remove in reversed order
        # to avoid changing the row of the following items to be checked for removal
        for row in reversed(range(self._listWidget.count())):
            listItem = self._listWidget.item(row)
            if listItem is None:
                continue
            jobItem: JobItem = listItem.data(qt.Qt.UserRole)
            if jobItem.getFuture().done():
                self._listWidget.takeItem(row)

    def _cancelSelected(self) -> None:
        for listItem in self._listWidget.selectedItems():
            jobItem = listItem.data(qt.Qt.UserRole)
            if jobItem is None:
                continue
            jobItem.getFuture().cancel()

    def _itemSelectionChanged(self) -> None:
        self._cancelAction.setEnabled(len(self._listWidget.selectedItems()) > 0)

    def _updateListItem(self, listItem: qt.QListWidgetItem, jobItem: JobItem) -> None:
        state = self._getFutureState(jobItem.getFuture())

        filename, number = get_scan_url(jobItem.getArguments())
        timestamp = jobItem.getTimestamp().time().isoformat("minutes")
        listItem.setText(f"{timestamp} {os.path.basename(filename)}::/{number}.1")
        listItem.setToolTip(
            f"<b>{state.capitalize()}</b><br><b>Scan:</b> {filename}::/{number}.1"
        )

        if state in ("failed", "cancelled"):
            listItem.setForeground(qt.Qt.red)

        if state == "pending":
            listItem.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
        else:
            # Unselect manually since removing the ItemIsSelectable flag does not unselect the item
            if listItem.isSelected():
                listItem.setSelected(False)
            listItem.setFlags(qt.Qt.ItemIsEnabled)

        if state == "running":
            self._runningIconItems.add(listItem)
            return

        self._runningIconItems.discard(listItem)
        listItem.setIcon(self._getStateIcon(state))

    @staticmethod
    @functools.cache
    def _getStateIcon(state: _FutureStateStr) -> qt.QIcon:
        iconNames: dict[_FutureStateStr, str | None] = {
            "pending": "fa6.hourglass-half",
            "succeeded": "fa6s.check",
            "cancelled": "fa6s.ban",
            "failed": "fa6s.exclamation",
            "running": None,
        }
        color = "red" if state in ("cancelled", "failed") else None
        return qtawesome.icon(iconNames[state], color=color, scale_factor=0.75)

    @staticmethod
    def _getFutureState(future: FutureInterface) -> _FutureStateStr:
        if future.running():
            return "running"

        if not future.done():
            return "pending"

        try:
            future.result(0.001)
        except TimeoutError:
            _logger.error("Cannot get workflow results")
            return "failed"
        except CancelledError:
            return "cancelled"
        except Exception:
            return "failed"
        else:
            return "succeeded"

    def _jobSubmitted(self, jobItem: JobItem) -> None:
        listItem = qt.QListWidgetItem()
        listItem.setData(qt.Qt.UserRole, jobItem)
        self._updateListItem(listItem, jobItem)
        self._listWidget.addItem(listItem)
        self._listWidget.scrollToBottom()

    def _jobChanged(self, jobItem: JobItem) -> None:
        listItem = self._findListItem(jobItem)
        if listItem is None:
            return
        self._updateListItem(listItem, jobItem)

    def _findListItem(self, jobItem: JobItem) -> qt.QListWidgetItem | None:
        for row in range(self._listWidget.count()):
            listItem = self._listWidget.item(row)
            if listItem is None:
                continue
            if listItem.data(qt.Qt.UserRole) is jobItem:
                return listItem
        return None
