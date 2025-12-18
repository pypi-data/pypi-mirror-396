from silx.gui import qt


class ExecutionGroupBox(qt.QGroupBox):

    _LOCAL_HOST = "Local"
    _REMOTE_HOST = "Ewoks worker"

    def __init__(self, parent: qt.QWidget | None = None):
        super().__init__("Execution", parent)

        executionModeLayout = qt.QHBoxLayout(self)

        executionModeLabel = qt.QLabel("Host:")
        self._executionModeComboBox = qt.QComboBox()
        self._executionModeComboBox.addItems((self._LOCAL_HOST, self._REMOTE_HOST))
        self._executionModeComboBox.setCurrentText(self._LOCAL_HOST)
        self._executionModeComboBox.setToolTip(
            "Select where the process will be executed: locally or on an Ewoks worker."
        )

        executionModeLayout.addWidget(executionModeLabel)
        executionModeLayout.addWidget(self._executionModeComboBox)
        executionModeLayout.addStretch(1)

    def setLocalExecution(self, local: bool):
        if local:
            self._executionModeComboBox.setCurrentText(self._LOCAL_HOST)
        else:
            self._executionModeComboBox.setCurrentText(self._REMOTE_HOST)

    def isLocalExecution(self) -> bool:
        return self._executionModeComboBox.currentText() == self._LOCAL_HOST
