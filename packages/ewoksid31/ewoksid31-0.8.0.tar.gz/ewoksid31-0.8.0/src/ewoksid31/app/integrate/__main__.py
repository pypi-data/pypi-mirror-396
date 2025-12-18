import argparse
import ctypes
import logging
import os
import signal
import sys

# Environment variable HDF5_USE_FILE_LOCKING must be set *before* importing HDF5 libraries
# This prevents file locking issues, especially in shared filesystems (e.g., NFS).
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

import hdf5plugin  # noqa: F401, E402 - Imported but unused
from silx.gui import qt  # noqa: E402

from ..utils import FLATFIELD_DEFAULT_DIR  # noqa: E402
from .constants import FILE_EXTENSIONS  # noqa: E402
from .mainwindow import MainWindow  # noqa: E402

_logger = logging.getLogger(__name__)


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description="",
    )
    parser.add_argument(
        "-f",
        "--fresh",
        action="store_true",
        help="Start without loading previous user preferences",
    )
    parser.add_argument(
        "default_dir",
        nargs="?",
        type=str,
        help="Default directory for raw/config/output dialogs (ex: /data/visitor/in1176/id31/20250412)",
        default=None,
        metavar="FOLDER",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=False,
        help="Dataset file to process (HDF5 format)",
        default="",
        metavar="FILE",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=False,
        help="Folder where to store the results",
        default="",
        metavar="FOLDER",
    )
    parser.add_argument(
        "-c",
        "--pyfai-config",
        type=str,
        default=None,
        help="PyFAI config file (.json)",
        metavar="FILE",
    )
    parser.add_argument(
        "--flat-dir",
        type=str,
        required=False,
        help=f"Folder containing flat-field files: flats.mat and old_flats.mat (default: {FLATFIELD_DEFAULT_DIR})",
        default=FLATFIELD_DEFAULT_DIR,
        metavar="FOLDER",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v: INFO, -vv:DEBUG)",
    )
    return parser


def main() -> int:
    logging.basicConfig(level=logging.WARNING)

    parser = create_argument_parser()
    args = parser.parse_args()

    logging.captureWarnings(True)

    if args.verbose == 0:
        logging.getLogger().setLevel(logging.ERROR)
        _logger.setLevel(logging.INFO)

    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.WARNING)
        _logger.setLevel(logging.INFO)

    else:
        logging.getLogger().setLevel(logging.DEBUG)

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ESRF.id31pyfaiewoks"
        )

    app = qt.QApplication([])
    app.setOrganizationName("ESRF")
    app.setOrganizationDomain("esrf.fr")
    app.setApplicationName("id31pyfaiewoks")

    app.setWindowIcon(
        qt.QIcon(os.path.join(os.path.dirname(__file__), "integrate.svg"))
    )

    window = MainWindow()
    window.setAttribute(qt.Qt.WA_DeleteOnClose)

    window.setFlatFieldDirName(args.flat_dir)

    if not args.fresh:
        _logger.debug("Loading settings from previous session.")
        window.loadSettings()

    if args.default_dir:
        default_dir = os.path.abspath(args.default_dir)
        if os.path.isdir(default_dir):
            window.setDefaultDirectory(default_dir)
            window.setConfigFilePath("")
            window._outputWidget.setDefaultDirectory(default_dir)
            window._outputWidget.setOutputDirName(default_dir)
            _logger.info(f"Set default directory: {default_dir}")
        else:
            _logger.warning(f"Invalid default directory provided: {default_dir}")

    if args.input:
        raw_data = os.path.abspath(args.input)
        if os.path.isfile(raw_data) and raw_data.endswith(FILE_EXTENSIONS):
            window.addRawDataFile(raw_data)
        else:
            _logger.error(f"Invalid raw data file path or format: {raw_data}")

    if args.output_dir:
        window._outputWidget.setOutputDirName(args.output_dir)

    if args.pyfai_config:
        config_file = os.path.abspath(args.pyfai_config)
        if os.path.isfile(config_file):
            window.setConfigFilePath(config_file)
        else:
            _logger.error(f"Invalid config file path: {config_file}")

    window.show()

    result = app.exec_()
    if window.isWorkflowRunning():
        # Running local threads cannot be cancelled, kill the application
        os.kill(os.getpid(), signal.SIGKILL)
    return result
