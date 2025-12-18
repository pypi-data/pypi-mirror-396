from silx.gui import qt


class SelectionFilterGroupBox(qt.QGroupBox):
    """GroupBox for configuring the filtering of selected scans"""

    def __init__(self, parent: qt.QWidget | None = None):
        super().__init__("Filter Selection", parent)
        self.setCheckable(True)
        self.setChecked(False)

        layout = qt.QHBoxLayout(self)

        layout.addWidget(qt.QLabel("Scan group name patterns:"))
        self._scanGroupNamePatternsLineEdit = qt.QLineEdit()
        self._scanGroupNamePatternsLineEdit.setToolTip(
            "Comma-separated list of patterns to filter scan group names in selection (e.g. WAXS, SAXS)"
        )
        self._scanGroupNamePatternsLineEdit.setPlaceholderText("scangroupname")
        layout.addWidget(self._scanGroupNamePatternsLineEdit)

        layout.addWidget(qt.QLabel("Scan command patterns:"))
        self._scanCommandPatternsLineEdit = qt.QLineEdit()
        self._scanCommandPatternsLineEdit.setToolTip(
            "Comma-separated list of patterns to filter scan title in selection (e.g. ct, ascan)"
        )
        self._scanCommandPatternsLineEdit.setPlaceholderText("scancommand")
        layout.addWidget(self._scanCommandPatternsLineEdit)

    def getScanGroupNamePatterns(self) -> tuple[str, ...]:
        """Return patterns to match scan group names (e.g. 'WAXS', 'SAXS')."""
        if not self.isChecked():
            return ()
        text = self._scanGroupNamePatternsLineEdit.text()
        patterns = [pattern.strip() for pattern in text.split(",")]
        return tuple(p for p in patterns if p)

    def getScanCommandPatterns(self) -> tuple[str, ...]:
        """Return patterns to match scan commands (e.g. 'ct', 'ascan')."""
        if not self.isChecked():
            return ()
        text = self._scanCommandPatternsLineEdit.text()
        patterns = [pattern.strip() for pattern in text.split(",")]
        return tuple(p for p in patterns if p)

    def loadSettings(self) -> None:
        settings = qt.QSettings()
        self.setChecked(settings.value("filterSelection/checked", False, type=bool))
        self._scanGroupNamePatternsLineEdit.setText(
            settings.value("filterSelection/scanGroupNamePatterns", "", type=str)
        )
        self._scanCommandPatternsLineEdit.setText(
            settings.value("filterSelection/scanCommandPatterns", "", type=str)
        )

    def saveSettings(self) -> None:
        settings = qt.QSettings()
        settings.setValue("filterSelection/checked", self.isChecked())
        settings.setValue(
            "filterSelection/scanGroupNamePatterns",
            self._scanGroupNamePatternsLineEdit.text(),
        )
        settings.setValue(
            "filterSelection/scanCommandPatterns",
            self._scanCommandPatternsLineEdit.text(),
        )
