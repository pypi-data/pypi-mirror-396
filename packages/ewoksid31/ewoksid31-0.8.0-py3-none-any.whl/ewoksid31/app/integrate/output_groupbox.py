import logging
import os

from silx.gui import icons, qt

from .utils import ExportMode, FilenameCompleterLineEdit

_logger = logging.getLogger(__name__)


class OutputWidget(qt.QGroupBox):
    def __init__(self):
        super().__init__("Output")

        self._outputLineEdit = FilenameCompleterLineEdit()
        self._outputLineEdit.setPlaceholderText("/path/to/output/directory")

        self._defaultDirectory = os.getcwd()

        outputDirButton = qt.QPushButton("Select...")
        outputDirButton.setToolTip("Define a new output directory.")
        outputDirButton.setIcon(icons.getQIcon("folder"))
        outputDirButton.clicked.connect(self._outputDirButtonClicked)

        exportDisableRadioButton = qt.QRadioButton("Disabled")
        exportAsciiRadioButton = qt.QRadioButton("ASCII (.xye)")
        self._exportAsciiScanFoldersCheckbox = qt.QCheckBox("Grouped per scan")

        exportHdf5TomoRadioButton = qt.QRadioButton("HDF5 Tomo (.h5):")
        self._exportButtonGroup = qt.QButtonGroup()

        self._exportButtonGroup.addButton(exportDisableRadioButton, 1)
        self._exportButtonGroup.addButton(exportAsciiRadioButton, 2)
        self._exportButtonGroup.addButton(exportHdf5TomoRadioButton, 3)

        exportDisableRadioButton.setChecked(True)
        self._exportAsciiScanFoldersCheckbox.setEnabled(False)
        exportAsciiRadioButton.toggled.connect(
            self._exportAsciiScanFoldersCheckbox.setEnabled
        )

        self._rotNameLineEdit = qt.QLineEdit()
        self._rotNameLineEdit.setPlaceholderText("rot_motor_name")
        self._rotNameLineEdit.setToolTip(
            "Specify the Rotation angle dataset (e.g., nth)."
        )

        self._yNameLineEdit = qt.QLineEdit()
        self._yNameLineEdit.setPlaceholderText("y_motor_name")
        self._yNameLineEdit.setToolTip(
            "Specify the radial position dataset (e.g., ny)."
        )

        self._tomoMotorWidget = qt.QWidget(self)
        self._tomoMotorWidget.setEnabled(False)
        exportHdf5TomoRadioButton.toggled.connect(self._tomoMotorWidget.setEnabled)

        tomoMotorLayout = qt.QHBoxLayout(self._tomoMotorWidget)
        tomoMotorLayout.setContentsMargins(0, 0, 0, 0)
        tomoMotorLayout.addWidget(qt.QLabel("Rot name:"))
        tomoMotorLayout.addWidget(self._rotNameLineEdit)
        tomoMotorLayout.addWidget(qt.QLabel("Y name:"))
        tomoMotorLayout.addWidget(self._yNameLineEdit)
        tomoMotorLayout.addStretch(1)

        gridLayout = qt.QGridLayout(self)
        gridLayout.setColumnStretch(2, 1)

        gridLayout.addWidget(qt.QLabel("Directory:"), 0, 0, 1, 1, qt.Qt.AlignLeft)
        gridLayout.addWidget(self._outputLineEdit, 0, 1, 1, 2)
        gridLayout.addWidget(outputDirButton, 0, 3, 1, 1, qt.Qt.AlignRight)

        gridLayout.addWidget(qt.QLabel("Export:"), 1, 0, 1, 1, qt.Qt.AlignLeft)
        gridLayout.addWidget(exportDisableRadioButton, 1, 1, 1, 1, qt.Qt.AlignLeft)
        gridLayout.addWidget(exportAsciiRadioButton, 2, 1, 1, 1, qt.Qt.AlignLeft)
        gridLayout.addWidget(
            self._exportAsciiScanFoldersCheckbox, 2, 2, 1, 1, qt.Qt.AlignLeft
        )
        gridLayout.addWidget(exportHdf5TomoRadioButton, 3, 1, 1, 1, qt.Qt.AlignLeft)
        gridLayout.addWidget(self._tomoMotorWidget, 3, 2, 1, 2, qt.Qt.AlignLeft)

    def getDefaultDirectory(self) -> str:
        """
        Return the default directory used when no output directory is set.
        """
        return self._defaultDirectory

    def setDefaultDirectory(self, path: str) -> None:
        """
        Set the default directory used when no output directory is set.
        """
        self._defaultDirectory = path

    def getOutputDirName(self) -> str:
        """
        Returns the current output directory path from the line edit.
        """
        return self._outputLineEdit.text().strip()

    def setOutputDirName(self, path: str) -> None:
        """
        Update the output directory path in the line edit.
        """
        self._outputLineEdit.setText(os.path.abspath(path))

    def _outputDirButtonClicked(self) -> None:
        """
        Choose an output directory using a dialog and set it in the line edit.
        """
        currentPath = self.getOutputDirName()
        # if not currentPath or not os.path.exists(currentPath):
        #     currentPath = self._defaultDirectory()
        if not currentPath or not os.path.exists(currentPath):
            currentPath = self.getDefaultDirectory()

        newPath = qt.QFileDialog.getExistingDirectory(
            self,
            "Choose output directory",
            currentPath,
        )
        if newPath:
            self.setOutputDirName(newPath)

    def getExportMode(self) -> ExportMode:
        checkedId = self._exportButtonGroup.checkedId()
        if checkedId == 1:
            return ExportMode.DISABLED
        elif checkedId == 2:
            if self._exportAsciiScanFoldersCheckbox.isChecked():
                return ExportMode.ASCII_ONE_DIR_PER_SCAN
            else:
                return ExportMode.ASCII_SINGLE_DIR
        elif checkedId == 3:
            return ExportMode.HDF5_TOMO
        else:
            _logger.warning(f"Unknown buttonId: {checkedId}")
            return ExportMode.DISABLED

    def setExportMode(self, mode: ExportMode):
        if mode == ExportMode.DISABLED:
            self._exportButtonGroup.button(1).setChecked(True)
        elif mode == ExportMode.ASCII_SINGLE_DIR:
            self._exportButtonGroup.button(2).setChecked(True)
        elif mode == ExportMode.ASCII_ONE_DIR_PER_SCAN:
            self._exportButtonGroup.button(2).setChecked(True)
        elif mode == ExportMode.HDF5_TOMO:
            self._exportButtonGroup.button(3).setChecked(True)
        self._exportAsciiScanFoldersCheckbox.setChecked(
            mode == ExportMode.ASCII_ONE_DIR_PER_SCAN
        )

    def getTomoRotName(self) -> str:
        return self._rotNameLineEdit.text().strip()

    def setTomoRotName(self, value: str):
        self._rotNameLineEdit.setText(value)

    def getTomoYName(self) -> str:
        return self._yNameLineEdit.text().strip()

    def setTomoYName(self, value: str):
        self._yNameLineEdit.setText(value)
