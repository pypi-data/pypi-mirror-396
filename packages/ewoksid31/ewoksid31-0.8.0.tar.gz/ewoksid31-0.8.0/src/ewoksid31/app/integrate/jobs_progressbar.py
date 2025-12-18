from silx.gui import qt

from .workflow_executor import JobItem, WorkflowExecutor


class JobsProgressBar(qt.QProgressBar):
    def __init__(
        self, executor: WorkflowExecutor, parent: qt.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setFormat("%v / %m")
        self.setMaximumWidth(self.sizeHint().width() * 2)
        self.setEnabled(False)

        executor.finished.connect(self._finished)
        executor.jobSubmitted.connect(self._jobSubmitted)
        executor.jobChanged.connect(self._jobChanged)

    def _finished(self) -> None:
        self.setEnabled(False)

    def _jobSubmitted(self) -> None:
        if self.isEnabled():
            self.setMaximum(self.maximum() + 1)
            return

        self.setRange(0, 1)
        self.setValue(0)
        self.setEnabled(True)

    def _jobChanged(self, jobItem: JobItem) -> None:
        future = jobItem.getFuture()
        if future.cancelled():
            self.setMaximum(max(0, self.maximum() - 1))
        elif future.done():
            self.setValue(self.value() + 1)
