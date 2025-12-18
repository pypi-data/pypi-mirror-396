import enum
import os
from dataclasses import dataclass
from typing import Any

from ewoksutils.task_utils import task_inputs
from silx.gui import qt


@dataclass(frozen=True, order=True)
class ScanEntry:
    filename: str
    number: int


class ExportMode(enum.IntEnum):
    DISABLED = 1
    ASCII_SINGLE_DIR = 2
    ASCII_ONE_DIR_PER_SCAN = 3
    HDF5_TOMO = 4


def generateInputs(
    scan: ScanEntry,
    newFlat: str,
    oldFlat: str,
    pyfaiConfigFile: str,
    pyfaiMethod: str,
    monitorName: str | None,
    referenceCounts: int,
    detectorName: str,
    outputDirectory: str,
    sigmaClippingThreshold: float | None,
    exportMode: ExportMode,
    unit: str,
    rotName: str = "",
    yName: str = "",
) -> dict:
    """
    Generate input parameters for the EWOKS workflow, including optional tomo export.
    """
    baseDirName = os.path.splitext(os.path.basename(scan.filename))[0]
    outputUnitSuffix = unit.split("_")[0]
    outputFilePathH5 = os.path.join(outputDirectory, f"{baseDirName}.h5")

    nxProcessName = f"{detectorName}_{outputUnitSuffix}_integrate"
    nxMeasurementName = f"{detectorName}_{outputUnitSuffix}_integrated"

    exportOutputDirectory = os.path.join(outputDirectory, "export")

    asciiBasenameTemplate = (
        f"{baseDirName}_{scan.number:04d}_{detectorName}_{outputUnitSuffix}_%04d.xye"
    )
    if exportMode == ExportMode.ASCII_ONE_DIR_PER_SCAN:
        outputAsciiFileTemplate = os.path.join(
            exportOutputDirectory,
            f"{baseDirName}_{scan.number:04d}",
            asciiBasenameTemplate,
        )
    else:
        outputAsciiFileTemplate = os.path.join(
            exportOutputDirectory, asciiBasenameTemplate
        )

    tomoOutputFilename = os.path.join(
        exportOutputDirectory,
        f"{baseDirName}_{scan.number:04d}_{detectorName}_{outputUnitSuffix}_tomo.h5",
    )

    integrationOptions: dict[str, Any] = {
        "method": pyfaiMethod,
        "unit": unit,
    }
    if sigmaClippingThreshold is not None:
        integrationOptions["extra_options"] = {
            "thres": sigmaClippingThreshold,
            "max_iter": 10,
            "error_model": "azimuthal",
        }
        integrationOptions["integrator_name"] = "sigma_clip_ng"

    inputs = [{"name": "overwrite", "value": True, "all": True}]
    inputs += task_inputs(
        task_identifier="FlatFieldFromEnergy",
        inputs={
            "newflat": newFlat,
            "oldflat": oldFlat,
            "energy": f"{scan.filename}::/{scan.number}.1/instrument/positioners/energy",
            "enabled": detectorName == "p3",
        },
    )
    inputs += task_inputs(
        task_identifier="PyFaiConfig",
        inputs={
            "filename": pyfaiConfigFile,
            "integration_options": integrationOptions,
        },
    )
    inputs += task_inputs(
        task_identifier="IntegrateBlissScan",
        inputs={
            "filename": scan.filename,
            "scan": scan.number,
            "output_filename": outputFilePathH5,
            "monitor_name": monitorName,
            "reference": referenceCounts,
            "maximum_persistent_workers": 2,
            "retry_timeout": 3600,
            "detector_name": detectorName,
            "nxprocess_name": nxProcessName,
            "nxmeasurement_name": nxMeasurementName,
        },
    )
    inputs += task_inputs(
        task_identifier="SaveNexusPatternsAsAscii",
        inputs={
            "enabled": exportMode
            in (ExportMode.ASCII_SINGLE_DIR, ExportMode.ASCII_ONE_DIR_PER_SCAN),
            "output_filename_template": outputAsciiFileTemplate,
        },
    )
    inputs += task_inputs(
        task_identifier="SaveNexusPatternsAsId31TomoHdf5",
        inputs={
            "enabled": exportMode == ExportMode.HDF5_TOMO,
            "scan_entry_url": f"{scan.filename}::/{scan.number}.1",
            "rot_name": rotName,
            "y_name": yName,
            "output_filename": tomoOutputFilename,
        },
    )

    return {
        "inputs": inputs,
        "convert_destination": os.path.join(
            outputDirectory,
            f"{baseDirName}_{scan.number}_{detectorName}_{outputUnitSuffix}.json",
        ),
    }


def extractScanNumber(h5path: str) -> int:
    """
    Extracts the scan number from the h5path from a selected node.

    Example: '/2.1/measurement/p4" -> returns 2'
    """
    parts = h5path.split("/")
    if len(parts) > 1:
        scanNumberPart = parts[1].split(".")[0]
        try:
            return int(scanNumberPart)
        except ValueError:
            pass
    return -1


def generateUniquePath(basePath: str) -> str:
    """
    Generates a unique path by adding an incremantal suffix if necessary.

    Args:
        basePath: Base path (file or directory)

    Returns:
        unique path
    """
    isFile = os.path.isfile(basePath)
    dirName = os.path.dirname(basePath)
    baseName, ext = (
        os.path.splitext(os.path.basename(basePath)) if isFile else (basePath, "")
    )

    parts = baseName.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        baseName, counter = parts[0], int(parts[1]) + 1
    else:
        counter = 1

    generatedName = os.path.join(dirName, f"{baseName}_{counter}{ext}")
    while os.path.exists(generatedName):
        counter += 1
        generatedName = os.path.join(dirName, f"{baseName}_{counter}{ext}")
    return generatedName


class FilenameCompleterLineEdit(qt.QLineEdit):
    """
    Heritage from QLineEdit widget that provides autocompletion for file paths.

    This widget uses a QFileSystemModel to suggest file and directory paths,
    starting from the root of the filesystem.
    """

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)

        completer = qt.QCompleter()
        model = qt.QFileSystemModel(completer)
        model.setOption(qt.QFileSystemModel.Option.DontWatchForChanges, True)
        model.setRootPath("/")

        completer.setModel(model)
        completer.setCompletionRole(qt.QFileSystemModel.Roles.FileNameRole)
        self.setCompleter(completer)


def get_scan_url(workflow_parameters):
    datasetFilename = None
    scanNumber = None
    for item in workflow_parameters["inputs"]:
        if item.get("task_identifier") != "IntegrateBlissScan":
            continue
        if item["name"] == "filename":
            datasetFilename = item["value"]
        if item["name"] == "scan":
            scanNumber = item["value"]

    return datasetFilename, scanNumber
