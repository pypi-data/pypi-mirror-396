import logging
import os
from collections.abc import Sequence
from importlib.metadata import version

import PyQt5.QtCore  # noqa: F401; Needed to force PyQt5
import qtawesome
from silx.gui import icons, qt

from ..utils import (
    FLATFIELD_DEFAULT_DIR,
    NEWFLAT_FILENAME,
    OLDFLAT_FILENAME,
)
from .constants import FILE_EXTENSIONS
from .execution_groupbox import ExecutionGroupBox
from .hdf5_widget import Hdf5Widget
from .jobs_list_widget import JobsListWidget
from .jobs_progressbar import JobsProgressBar
from .output_groupbox import OutputWidget
from .processing_groupbox import ProcessingGroupBox
from .utils import (
    ExportMode,
    FilenameCompleterLineEdit,
    ScanEntry,
    generateInputs,
    get_scan_url,
)
from .workflow_executor import WorkflowExecutor

_logger = logging.getLogger(__name__)


class MainWindow(qt.QMainWindow):
    """
    This GUI is designed for reprocessing HDF5 scans data with fast azimuthal
    integration using Ewoks workflows (ewoksXRPD)
    """

    _SETTINGS_VERSION_STR: str = "2"
    _WORKFLOW: str = "integrate_with_saving_with_flat.json"
    _WORKFLOW_LOAD_OPTIONS: dict[str, str] = {"root_module": "ewoksid31.workflows"}

    def __init__(self, parent: qt.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("pyFAI with EWOKS - ID31")
        self.resize(1000, 800)

        self._executor = WorkflowExecutor()
        self._executor.finished.connect(self._executorFinished)

        self.statusBar().addPermanentWidget(JobsProgressBar(self._executor))

        self._executionDockWidget = qt.QDockWidget("Processing Queue")
        self._executionDockWidget.setFeatures(
            qt.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        )
        self._executionDockWidget.setWidget(JobsListWidget(self._executor))
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._executionDockWidget)

        # Set paths
        self._outputWidget = OutputWidget()
        self._defaultDirectory = os.getcwd()
        self._flatFieldDirName = FLATFIELD_DEFAULT_DIR

        # Central Layout setup
        centralWidget = qt.QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = qt.QVBoxLayout(centralWidget)

        # HDF5 Viewer
        self._hdf5Widget = Hdf5Widget()
        mainLayout.addWidget(self._hdf5Widget)

        # Menu and Toolbar setup
        self._setupMenuAndToolBar()
        configLayout = qt.QVBoxLayout()

        # pyFAI Config Section
        pyFaiGroupBox = qt.QGroupBox("PyFAI Configuration")
        pyFaiLayout = qt.QGridLayout()

        self._configFileLineEdit = FilenameCompleterLineEdit()
        self._configFileLineEdit.setPlaceholderText("/path/to/pyfai_config.json")

        loadConfigFileButton = qt.QPushButton("Open...")
        loadConfigFileButton.setIcon(icons.getQIcon("document-open"))
        loadConfigFileButton.clicked.connect(self._loadConfigFileButtonClicked)

        pyFaiLayout.addWidget(self._configFileLineEdit, 0, 0, 1, 1)
        pyFaiLayout.addWidget(loadConfigFileButton, 0, 1, 1, 1)

        pyFaiGroupBox.setLayout(pyFaiLayout)
        configLayout.addWidget(pyFaiGroupBox)

        # Processing Options Section
        self._processingGroupBox = ProcessingGroupBox()
        configLayout.addWidget(self._processingGroupBox)

        # Output Section
        configLayout.addWidget(self._outputWidget)

        # Execution Section
        self._executionGroupBox = ExecutionGroupBox()

        configLayout.addWidget(self._executionGroupBox)
        configWidget = qt.QWidget()
        configWidget.setLayout(configLayout)
        configWidget.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed)

        scrollArea = qt.QScrollArea()
        scrollArea.setWidget(configWidget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(
            qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scrollArea.setMaximumHeight(configWidget.sizeHint().height() + 2)

        mainLayout.addWidget(scrollArea)

        runButton = qt.QPushButton("Run")
        runButton.setIcon(icons.getQIcon("next"))
        runButton.clicked.connect(self._runButtonClicked)
        runButton.setToolTip("Run the processing workflow on the selected host.")
        runButton.setMinimumSize(runButton.sizeHint() * 2)
        runButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        mainLayout.addWidget(runButton, alignment=qt.Qt.AlignCenter)

    def getDefaultDirectory(self) -> str:
        """
        Return the default directory defined by the user.
        """
        return self._defaultDirectory

    def setDefaultDirectory(self, path: str) -> None:
        """
        Sets the default directory used when opening the QFileDialog.
        """
        self._defaultDirectory = path

    def _showHelpDialogClicked(self):
        """
        Display the Help dialog when the Help button is clicked.
        """
        helpDialog = qt.QMessageBox(self)
        helpDialog.setWindowTitle("Help")
        helpDialog.setIcon(qt.QMessageBox.Information)

        helpDialog.setTextFormat(qt.Qt.RichText)
        helpDialog.setText(
            f"<b>Welcome to the pyFAI with EWOKS application help (version {version('ewoksid31')}).</b><br>"
            "<br>How to get started?<br>"
            "<ul>"
            f"<li>Load raw data files {FILE_EXTENSIONS}.</li>"
            "<li>Load the pyFAI configuration file.</li>"
            "<li>Select an output directory to save the processed data.</li>"
            "<li>Click Run to execute the workflow.</li>"
            "</ul>"
            "<br>For more information, visit:<br>"
            '<a href="https://ewoksid31.readthedocs.io/en/latest/">Ewoksid31 Documentation</a><br>'
            '<a href="https://confluence.esrf.fr/display/ID31KB/GUI+for+reprocessing+XRPD+data">ID31 GUI Confluence Page</a>'
        )

        helpDialog.setStandardButtons(qt.QMessageBox.Ok)
        helpDialog.exec_()

    def _setupMenuAndToolBar(
        self,
    ) -> None:
        """
        Setup of the main menu and toolbar with actions for file handling.
        """
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")

        openAction = qt.QAction(icons.getQIcon("document-open"), "Open...", self)
        openAction.triggered.connect(self._openActionTriggered)
        openAction.setShortcut(qt.QKeySequence.StandardKey.Open)
        reloadAction = qt.QAction(icons.getQIcon("view-refresh"), "Reload", self)
        reloadAction.triggered.connect(self._hdf5Widget.reloadSelected)
        reloadAction.setShortcut(qt.QKeySequence.StandardKey.Refresh)
        clearAction = qt.QAction(icons.getQIcon("remove"), "Clear", self)
        clearAction.triggered.connect(self._hdf5Widget.clearFiles)
        clearAction.setShortcut(qt.QKeySequence.StandardKey.Delete)

        fileMenu.addActions([openAction, reloadAction, clearAction])

        toolBar = self.addToolBar("File Actions")
        toolBar.addActions([openAction, reloadAction, clearAction])
        toolBar.setMovable(False)
        self.setContextMenuPolicy(qt.Qt.PreventContextMenu)
        toolBar.setFloatable(False)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Preferred)
        toolBar.addWidget(spacer)

        helpAction = qt.QAction(
            self.style().standardIcon(qt.QStyle.SP_TitleBarContextHelpButton), "", self
        )
        font = helpAction.font()
        font.setBold(True)
        helpAction.setFont(font)
        helpAction.setToolTip("About this app")
        helpAction.triggered.connect(self._showHelpDialogClicked)
        toolBar.addAction(helpAction)

        jobsListVisibleAction = qt.QAction(
            qtawesome.icon("fa6s.list-check", scale_factor=0.75), "", self
        )
        jobsListVisibleAction.setToolTip("Show/Hide the processing queue panel")
        jobsListVisibleAction.setCheckable(True)
        jobsListVisibleAction.setChecked(self._executionDockWidget.isVisibleTo(self))
        jobsListVisibleAction.toggled.connect(self._executionDockWidget.setVisible)
        self._executionDockWidget.visibilityChanged.connect(
            jobsListVisibleAction.setChecked
        )
        toolBar.addAction(jobsListVisibleAction)

    def addRawDataFile(self, fileName: str) -> None:
        """
        Proxy method to add a new file to the HDF5 tree viewer.
        """
        if not fileName or not os.path.isfile(fileName):
            qt.QMessageBox.warning(
                self, "Invalid File Format", "The selected file does not exist."
            )
            return
        if not fileName.endswith(FILE_EXTENSIONS):
            qt.QMessageBox.warning(
                self,
                "Invalid File Format",
                f"Please select a valid HDF5 or NEXUS file {FILE_EXTENSIONS}.",
            )
            return
        self._hdf5Widget.addFile(fileName)
        self.setDefaultDirectory(os.path.dirname(fileName))

    def _openActionTriggered(self) -> None:
        """
        Add Raw data as HDF5 file without cleaning the tree viewer.
        """
        nameFilter = " ".join(f"*{ext}" for ext in FILE_EXTENSIONS)
        fileName, _ = qt.QFileDialog.getOpenFileName(
            self,
            "Add RAW data file",
            self.getDefaultDirectory(),
            f"HDF5 files ({nameFilter});;All files (*)",
        )
        if fileName:
            self.addRawDataFile(fileName)

    def _loadConfigFileButtonClicked(self) -> None:
        """
        Choose and import JSON or PONI config file.
        """
        currentDir = (
            os.path.dirname(self.getConfigFilePath()) or self.getDefaultDirectory()
        )
        filePath, _ = qt.QFileDialog.getOpenFileName(
            self,
            "Open config file",
            currentDir,
            "JSON or PONI files (*.json *.poni);;All files (*)",
        )
        if filePath:
            self.setConfigFilePath(filePath)
        else:
            self.setConfigFilePath("")
            _logger.info("No config file chosen.")

    def isWorkflowRunning(self) -> bool:
        return self._executor.isJobRunning()

    def getFlatFieldDirName(self) -> str:
        """Returns the flat-field directory where to find flats.mat and oldflats.mat"""
        return self._flatFieldDirName

    def setFlatFieldDirName(self, path: str):
        """Set the directory where to find flats.mat and oldflats.mat"""
        self._flatFieldDirName = os.path.abspath(path)

    def getConfigFilePath(self) -> str:
        """
        Returns the current configuration file path from the line edit.
        """
        return self._configFileLineEdit.text().strip()

    def setConfigFilePath(self, path: str) -> None:
        """
        Update the configuration file path in the line edit.
        """
        self._configFileLineEdit.setText(path)

    def _getParameters(self, scan: ScanEntry, unit: str) -> dict | None:
        """
        Generates parameters to execute workflow for a given scan.

        Args:
            datasetFilename: Filename of the HDF5 file containing the scan
            scanNumber: Number of the scan.
            unit: Selected unit.

        Returns:
            Dictionnary of parameters for the workflow, or None if failed.
        """

        return generateInputs(
            scan=scan,
            newFlat=os.path.join(self.getFlatFieldDirName(), NEWFLAT_FILENAME),
            oldFlat=os.path.join(self.getFlatFieldDirName(), OLDFLAT_FILENAME),
            pyfaiConfigFile=self.getConfigFilePath(),
            pyfaiMethod=self._processingGroupBox.getIntegrationMethod(),
            monitorName=self._processingGroupBox.getMonitorName(),
            referenceCounts=1,
            detectorName=self._processingGroupBox.getDetectorName(),
            outputDirectory=self._outputWidget.getOutputDirName(),
            sigmaClippingThreshold=self._processingGroupBox.getSigmaClippingThreshold(),
            exportMode=self._outputWidget.getExportMode(),
            unit=unit,
            rotName=self._outputWidget.getTomoRotName(),
            yName=self._outputWidget.getTomoYName(),
        )

    def _prepareScans(self, scans: Sequence[ScanEntry]) -> list[dict]:
        """
        Prepares parameters for each unique selected scan and selected unit.
        """
        inputParameters = list()
        selectedUnits = self._processingGroupBox.getSelectedUnits()
        for scan in scans:
            for unit in selectedUnits:
                workflowParameters = self._getParameters(scan, unit)
                if not workflowParameters:
                    _logger.warning(
                        f"Skipping scan {scan.filename}::{scan.number} due to missing parameters."
                    )
                    continue

                inputParameters.append(workflowParameters)

        return inputParameters

    def _processScans(self, scans: Sequence[ScanEntry], local: bool = True) -> None:
        """
        Execute workflow and save HDF5 data and JSON workflow ewoks file from a single selected scan
        and selected unit.

        Executing in a separate thread.

        Args:
            scans: Selected scans filename and number
            local: Whether to execute locally or submit to Ewoks worker.
        """
        if not scans:
            return

        self.statusBar().showMessage("Processing selected scans...")

        for inputParameters in self._prepareScans(scans):
            scanFilename, scanNumber = get_scan_url(inputParameters)
            _logger.info(f"Submit workflow for {scanFilename}::{scanNumber}")
            self._executor.submit(
                local,
                graph=self._WORKFLOW,
                load_options=self._WORKFLOW_LOAD_OPTIONS,
                **inputParameters,
            )

    def _executorFinished(self) -> None:
        self.statusBar().showMessage("Processing finished")

    def _runButtonClicked(self) -> None:
        """
        Handle the run button click. Validate inputs, adjust output directory and process scans based on the selected execution mode.
        """
        selectedScans = self._hdf5Widget.getFilteredSelectedScans(
            self._processingGroupBox.getDetectorName()
        )
        userSelectedScans = self._hdf5Widget.getUserSelectedScans()
        invalidScans = userSelectedScans - selectedScans

        if invalidScans:
            for invalidScan in sorted(invalidScans):
                _logger.warning(
                    f"Ignoring scan {os.path.basename(invalidScan.filename)}::/{invalidScan.number}.1"
                )

        if not self._validateInputParameters(selectedScans):
            return

        if not self._adjustOutputDirectory():
            self.statusBar().showMessage("Process canceled by user.")
            return

        self._processScans(
            tuple(sorted(selectedScans)),
            local=self._executionGroupBox.isLocalExecution(),
        )

    def _getValidationErrors(
        self,
        rawDataLoaded: bool,
        selectedScans: set[ScanEntry],
        configFileLoaded: bool,
        unitSelected: bool,
    ) -> list[str]:
        """
        Generate a list of validation error messages based on the current state.

        Args:
            rawDataLoaded: Whether raw data is loaded.
            selectedScans: List of selected scans.
            configFileLoaded: Whether a configuration file is loaded.
            unitSelected: Whether at least one radial unit is selected.

        Returns:
            A list of error messages if validation fails, otherwise an empty list.
        """
        errors = list()

        if not rawDataLoaded:
            errors.append("No raw data file loaded.")
        if not selectedScans:
            errors.append("No scan selected for processing.")
        if not configFileLoaded:
            errors.append("No pyFAI config file loaded.")
        if not unitSelected:
            errors.append("No radial unit selected.")
        return errors

    def _showWarningMessage(self, errorMessages: list[str]) -> None:
        """
        Show a warning message box if prerequisites for processing are not met.
        """
        warningMessageBox = qt.QMessageBox(self)
        warningMessageBox.setWindowTitle("Workflow cannot be excecuted")
        warningMessageBox.setIcon(qt.QMessageBox.Warning)
        warningMessageBox.setText("\n".join(errorMessages))
        warningMessageBox.exec_()

    def _validateInputParameters(self, selectedScans: set) -> bool:
        """
        Validates that all necessary inputs are present before starting processing.

        Returns:
            True if inputs are valid, False otherwise.
        """
        rawDataLoaded = not self._hdf5Widget.isEmpty()
        configFileLoaded = bool(self.getConfigFilePath())
        unitSelected = len(self._processingGroupBox.getSelectedUnits()) != 0

        errorMessages = self._getValidationErrors(
            rawDataLoaded, selectedScans, configFileLoaded, unitSelected
        )

        if errorMessages:
            self.statusBar().showMessage(" ".join(errorMessages))
            _logger.warning(f"Processing cannot start: {' '.join(errorMessages)}")
            self._showWarningMessage(errorMessages)
            return False
        return True

    def _showConfirmationMessage(self, outputDirectory: str) -> bool:
        """
        Show a confirmation message box when creating a new directory for output file.

        Returns True is the user confirms, otherwise False.
        """
        confirmationMessageBox = qt.QMessageBox(self)
        confirmationMessageBox.setWindowTitle("Overwrite Output Files")
        confirmationMessageBox.setIcon(qt.QMessageBox.Question)
        confirmationMessageBox.setText("The selected output directory already exists.")
        confirmationMessageBox.setInformativeText(
            f"Do you want to overwrite existing files in: {outputDirectory} ?\nUnchanged files will be preserved."
        )
        confirmationMessageBox.setStandardButtons(
            qt.QMessageBox.Ok | qt.QMessageBox.Cancel
        )
        userResponse = confirmationMessageBox.exec_()
        return userResponse == qt.QMessageBox.Ok

    def _adjustOutputDirectory(self) -> bool:
        """
        Use the selected output directory directly, without creating a new one.
        Ask for confirmation if the folder already exists.

        Returns:
            True if the process should continue, False if canceled.
        """
        currentOutputDir = self._outputWidget.getOutputDirName()
        if os.path.exists(currentOutputDir):
            if not self._showConfirmationMessage(currentOutputDir):
                _logger.info("Process canceled by the user.")
                return False
            _logger.info(
                f"Processed data will be written in existing directory: {currentOutputDir}"
            )

        return True

    def loadSettings(self) -> None:
        """
        Load user settings.
        """
        settings = qt.QSettings()

        if settings.value("version") != self._SETTINGS_VERSION_STR:
            _logger.info("Setting version mismatch. Clearing settings.")
            settings.clear()
            return

        geometry = settings.value("mainWindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        defaultDirectory = settings.value("input/inputDirectory", None)
        if defaultDirectory and os.path.isdir(defaultDirectory):
            self.setDefaultDirectory(defaultDirectory)
        self.setConfigFilePath(settings.value("config/configFile", ""))
        self._outputWidget.setOutputDirName(
            settings.value("output/outputDirectory", "")
        )

        self._processingGroupBox.loadSettings()

        self._outputWidget.setTomoRotName(settings.value("output/tomo/rot_name", "nth"))
        self._outputWidget.setTomoYName(settings.value("output/tomo/y_name", "ny"))

        self._outputWidget.setExportMode(
            ExportMode(
                settings.value("output/exportMode", ExportMode.DISABLED.value, type=int)
            )
        )

        self._executionGroupBox.setLocalExecution(
            settings.value("run/localExecution", True, type=bool)
        )

        self._hdf5Widget.loadSettings()

    def closeEvent(self, event: qt.QCloseEvent) -> None:
        """
        Save user settings on application close.
        """
        if self.isWorkflowRunning():
            button = qt.QMessageBox.warning(
                self,
                "Processing is running",
                "<b>Do you want to quit anyway?</b><br><br>This might corrupt local output files.",
                qt.QMessageBox.Yes | qt.QMessageBox.No,
                qt.QMessageBox.No,
            )
            if button != qt.QMessageBox.Yes:
                event.ignore()
                return
            self._executor.shutdown(wait=False, cancelFutures=True)

        settings = qt.QSettings()

        settings.setValue("version", self._SETTINGS_VERSION_STR)
        settings.setValue("mainWindow/geometry", self.saveGeometry())

        settings.setValue("input/inputDirectory", self.getDefaultDirectory())

        settings.setValue("config/configFile", self.getConfigFilePath())

        self._processingGroupBox.saveSettings()

        settings.setValue("output/tomo/rot_name", self._outputWidget.getTomoRotName())
        settings.setValue("output/tomo/y_name", self._outputWidget.getTomoYName())

        settings.setValue(
            "output/outputDirectory", self._outputWidget.getOutputDirName()
        )
        settings.setValue("output/exportMode", self._outputWidget.getExportMode().value)

        settings.setValue(
            "run/localExecution", self._executionGroupBox.isLocalExecution()
        )

        self._hdf5Widget.saveSettings()
