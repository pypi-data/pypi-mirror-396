import copy
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from typing import Any, Literal

import ewoks
import silx.gui.qt.inspect
from ewoksjob.client.futures import FutureInterface
from silx.gui import qt


class JobItem:
    def __init__(
        self, future: Future | FutureInterface, local: bool, kwargs: dict[str, Any]
    ) -> None:
        self._timestamp = datetime.now()
        self._future = future
        self._local = local
        self._kwargs: dict[str, Any] = copy.deepcopy(kwargs)
        self._state: Literal["pending", "running", "done"] = "pending"

    def getFuture(self) -> Future | FutureInterface:
        return self._future

    def isLocal(self) -> bool:
        return self._local

    def getArguments(self) -> dict[str, Any]:
        return copy.deepcopy(self._kwargs)

    def getTimestamp(self) -> datetime:
        return self._timestamp

    def _isStateUpdated(self) -> bool:
        if self._state == "done":
            return False

        if self._state == "pending" and self._future.running():
            self._state = "running"
            return True

        if self._future.done():
            self._state = "done"
            return True
        return False


class WorkflowExecutor(qt.QObject):
    """Execute workflows locally or remotely and reports submitted job activity"""

    jobSubmitted = qt.Signal(JobItem)

    jobChanged = qt.Signal(JobItem)
    """Signal emitted when a job has changed from pending to running or running to done or cancelled"""

    finished = qt.Signal()
    """Signal emitted when all submitted jobs are finished (failed, cancelled or succeeded)"""

    def __init__(self, parent: qt.QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = qt.QTimer(self)
        self._timer.setInterval(1000)  # milliseconds
        self._timer.timeout.connect(self._updateItems)
        self._items: set[JobItem] = set()
        self._localExecutor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix=self.__class__.__name__
        )

    def _remoteShutdown(self, wait: bool, cancelFutures: bool) -> None:
        remoteFutures = set(
            item.getFuture() for item in self._items if not item.isLocal()
        )
        if cancelFutures:
            for future in remoteFutures:
                future.cancel()
        if wait:
            for future in remoteFutures:
                try:
                    future.result()
                except Exception:  # nosec: B110
                    pass

    def shutdown(self, wait: bool = True, *, cancelFutures: bool = False) -> None:
        self._localExecutor.shutdown(wait=wait, cancel_futures=cancelFutures)
        self._remoteShutdown(wait=wait, cancelFutures=cancelFutures)
        self._updateItems()

    def __del__(self):
        self.shutdown(wait=False, cancelFutures=True)

    def submit(self, local: bool, /, **kwargs) -> JobItem:
        # Use a copy: execute_graph modify its graph argument
        kwargs_copy = copy.deepcopy(kwargs)
        if local:
            future = self._localExecutor.submit(ewoks.execute_graph, **kwargs_copy)
        else:
            future = ewoks.submit_graph(**kwargs_copy)

        item = JobItem(future, local, kwargs)
        self._items.add(item)
        if not self._timer.isActive():
            self._timer.start()
        self.jobSubmitted.emit(item)
        return item

    def _updateItems(self):
        for item in self._items.copy():
            if item._isStateUpdated():
                self.jobChanged.emit(item)
            if item.getFuture().done():
                self._items.discard(item)

        if not self._items:
            # Since this is called from __del__, make sure QObjects are valid
            if silx.gui.qt.inspect.isValid(self):
                if silx.gui.qt.inspect.isValid(self._timer):
                    self._timer.stop()
                self.finished.emit()

    def isJobRunning(self) -> bool:
        return bool(self._items)
