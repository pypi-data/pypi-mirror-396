from silx.gui import qt

from .constants import DETECTOR_NAMES, INTEGRATION_METHODS, MONITOR_NAMES


class ProcessingGroupBox(qt.QGroupBox):
    def __init__(self):
        super().__init__("Processing")

        layout = qt.QGridLayout(self)

        spacer = qt.QSpacerItem(
            20, 10, qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )
        layout.addItem(spacer, 0, 4, 2, 4)

        detectorLabel = qt.QLabel("Detector:")
        self._detectorComboBox = qt.QComboBox()
        self._detectorComboBox.addItems(DETECTOR_NAMES)
        self._detectorComboBox.setCurrentText("p4")
        self._detectorComboBox.setToolTip("Select the detector type.")
        self._detectorComboBox.activated.connect(self._onDetectorChanged)

        layout.addWidget(detectorLabel, 0, 0, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._detectorComboBox, 0, 1, 1, 2)

        monitorNameLabel = qt.QLabel("Monitor:")
        self._monitorNameComboBox = qt.QComboBox()
        self._monitorNameComboBox.addItem("-")
        self._monitorNameComboBox.addItems(MONITOR_NAMES)
        self._monitorNameComboBox.setCurrentText("scaled_mondio")
        self._monitorNameComboBox.setToolTip(
            "Select the monitor name for normalization."
        )
        self._monitorNameComboBox.setItemData(
            0, "Disable normalization", qt.Qt.ToolTipRole
        )

        layout.addWidget(monitorNameLabel, 1, 0, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._monitorNameComboBox, 1, 1, 1, 2)

        self._sigmaClipCheckBox = qt.QCheckBox("Sigma clipping threshold:")
        self._sigmaClipCheckBox.setChecked(False)
        self._sigmaClipCheckBox.setToolTip(
            "Check to enable sigma clipping and set threshold."
        )

        self._sigmaClipThresholdSpinBox = qt.QDoubleSpinBox()
        self._sigmaClipThresholdSpinBox.setSingleStep(0.1)
        self._sigmaClipThresholdSpinBox.setRange(0.1, 10.0)
        self._sigmaClipThresholdSpinBox.setValue(3.0)
        self._sigmaClipThresholdSpinBox.setDecimals(1)
        self._sigmaClipThresholdSpinBox.setEnabled(False)

        self._sigmaClipCheckBox.toggled.connect(
            self._sigmaClipThresholdSpinBox.setEnabled
        )
        self._sigmaClipCheckBox.toggled.connect(self._sigmaClipCheckBoxToggled)

        layout.addWidget(self._sigmaClipCheckBox, 2, 0, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._sigmaClipThresholdSpinBox, 2, 1, 1, 2, qt.Qt.AlignLeft)

        integrationMethodLabel = qt.QLabel("Integration method:")
        self._integrationMethodComboBox = qt.QComboBox()
        self._integrationMethodComboBox.addItems(INTEGRATION_METHODS)
        self._integrationMethodComboBox.setCurrentText("no_histogram_cython")
        self._integrationMethodComboBox.setToolTip(
            "Select the pyFAI integration method."
        )

        layout.addWidget(integrationMethodLabel, 3, 0, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._integrationMethodComboBox, 3, 1, 1, 2)

        radialUnitLabel = qt.QLabel("Radial unit:")
        self._qCheckBox = qt.QCheckBox("q (scattering vector)")
        self._qUnitsComboBox = qt.QComboBox()
        self._qUnitsComboBox.addItems(("Å⁻¹", "nm⁻¹"))
        self._2thCheckBox = qt.QCheckBox("2theta (degree)")
        self._qUnitsComboBox.setEnabled(False)
        self._qCheckBox.toggled.connect(self._qUnitsComboBox.setEnabled)

        layout.addWidget(radialUnitLabel, 4, 0, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._qCheckBox, 4, 1, 1, 1, qt.Qt.AlignLeft)
        layout.addWidget(self._qUnitsComboBox, 4, 2, 1, 1, qt.Qt.AlignRight)
        layout.addWidget(self._2thCheckBox, 5, 1, 1, 1, qt.Qt.AlignLeft)

    def getDetectorName(self) -> str:
        return self._detectorComboBox.currentText()

    def setDetectorName(self, value: str):
        self._detectorComboBox.setCurrentText(value)

    def _onDetectorChanged(self) -> None:
        """
        Prompt the user to verify the configuration file after changing the detector.

        Ensures that the selected config file in the 'pyFAI config' section is compatible with the newly selected detector.
        """

        selectedDetector = self._detectorComboBox.currentText()

        message = (
            f"You just changed the detector to <b><i>{selectedDetector}</i></b>.<br><br>"
            "Please ensure that the <b>config file</b> in the <i>pyFAI config</i> section is correct.<br>"
            "If necessary, load the appropriate <b>JSON</b> or <b>PONI</b> file."
        )

        qt.QMessageBox.information(self, "Configuration file verification", message)

    def getMonitorName(self) -> str | None:
        if self._monitorNameComboBox.currentText() == "-":
            return None
        return self._monitorNameComboBox.currentText()

    def setMonitorName(self, value: str | None):
        if value is None:
            self._monitorNameComboBox.setCurrentText("-")
        else:
            self._monitorNameComboBox.setCurrentText(value)

    def getSigmaClippingThreshold(self) -> float | None:
        """
        Return threshold if sigma clipping is enabled, else None.
        """
        if self._sigmaClipCheckBox.isChecked():
            return self._sigmaClipThresholdSpinBox.value()
        return None

    def _sigmaClipCheckBoxToggled(self, toggled: bool) -> None:
        """
        Update integration methods combo box according to sigma clipping.

        - Change selected method if not supported by sigma clipping
        - Enable/Disable pixel splitting methods depending on sigma clipping
        """
        noCsrPrefix = "no_csr"

        if toggled and not self._integrationMethodComboBox.currentText().startswith(
            noCsrPrefix
        ):
            self._integrationMethodComboBox.setCurrentText("no_csr_ocl_gpu")

        model = self._integrationMethodComboBox.model()
        for row in range(self._integrationMethodComboBox.count()):
            item = model.item(row)
            if not item.text().startswith(noCsrPrefix):
                flags = item.flags()
                if toggled:
                    item.setFlags(flags & ~qt.Qt.ItemIsEnabled)
                    item.setToolTip("Not available with sigma clipping")
                else:
                    item.setFlags(flags | qt.Qt.ItemIsEnabled)
                    item.setToolTip("")

    def getIntegrationMethod(self) -> str:
        return self._integrationMethodComboBox.currentText()

    def setIntegrationMethod(self, value: str):
        self._integrationMethodComboBox.setCurrentText(value)

    def getSelectedUnits(self) -> list[str]:
        """
        Return a list of selected radial units: 'q_A^-1', 'q_nm^-1' and/or '2th_deg'.
        """
        units = list()
        if self._qCheckBox.isChecked():
            unit = self._qUnitsComboBox.currentText()
            if unit == "Å⁻¹":
                units.append("q_A^-1")
            elif unit == "nm⁻¹":
                units.append("q_nm^-1")
        if self._2thCheckBox.isChecked():
            units.append("2th_deg")
        return units

    def get2ThCheckBox(self) -> qt.QCheckBox:
        """
        Return the 2theta checkbox (for test purposes).
        """
        return self._2thCheckBox

    def loadSettings(self) -> None:
        settings = qt.QSettings()

        detectorName = settings.value("options/detectorName", None)
        if detectorName in DETECTOR_NAMES:
            self._detectorComboBox.setCurrentText(detectorName)

        monitorName = settings.value("options/monitorName", None)
        if monitorName == "-" or monitorName in MONITOR_NAMES:
            self._monitorNameComboBox.setCurrentText(monitorName)

        integrationMethod = settings.value("options/integrationMethod", None)
        if integrationMethod in INTEGRATION_METHODS:
            self._integrationMethodComboBox.setCurrentText(integrationMethod)

        self._sigmaClipCheckBox.setChecked(
            settings.value("options/sigmaClipping/enabled", False, type=bool)
        )
        self._sigmaClipThresholdSpinBox.setValue(
            settings.value("options/sigmaClipping/threshold", 3, type=float)
        )

        self._qCheckBox.setChecked(settings.value("options/units/q", False, type=bool))
        selectedQUnit = settings.value("options/units/q_unit", "Å⁻¹")
        if selectedQUnit in ["Å⁻¹", "nm⁻¹"]:
            self._qUnitsComboBox.setCurrentText(selectedQUnit)

        self._2thCheckBox.setChecked(
            settings.value("options/units/2th", False, type=bool)
        )

    def saveSettings(self) -> None:
        settings = qt.QSettings()

        settings.setValue("options/detectorName", self._detectorComboBox.currentText())

        settings.setValue(
            "options/monitorName", self._monitorNameComboBox.currentText()
        )

        settings.setValue(
            "options/sigmaClipping/enabled", self._sigmaClipCheckBox.isChecked()
        )
        settings.setValue(
            "options/sigmaClipping/threshold",
            float(self._sigmaClipThresholdSpinBox.value()),
        )

        settings.setValue(
            "options/integrationMethod", self._integrationMethodComboBox.currentText()
        )

        settings.setValue("options/units/q", self._qCheckBox.isChecked())
        settings.setValue("options/units/q_unit", self._qUnitsComboBox.currentText())
        settings.setValue("options/units/2th", self._2thCheckBox.isChecked())
