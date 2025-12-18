import json
import logging
from pathlib import Path

import numpy
import pytest
import scipy.io

from ..app.integrate.mainwindow import MainWindow
from ..app.integrate.utils import ScanEntry
from .conftest import DETECTOR_SHAPE

PONI = {
    "application": "pyfai-integrate",
    "version": 3,
    "wavelength": 1.6531226457760035e-11,
    "dist": 1.014612139238891,
    "poni1": 0.21340662994315895,
    "poni2": 0.13912764384981186,
    "rot1": -0.004822100080733148,
    "rot2": 0.0005542810978441514,
    "rot3": 0.0,
    "detector": "Pilatus_CdTe_2M",
}


def _create_flats(flat_dir: Path, n=5):
    energy = numpy.linspace(0, 10, n)
    flat = numpy.ones((*DETECTOR_SHAPE, n))
    scipy.io.savemat(flat_dir / "flats.mat", mdict={"E": energy, "F": flat})
    scipy.io.savemat(flat_dir / "flats_old.mat", mdict={"Eold": energy, "Fold": flat})


def test_integrate(qtbot, tmp_path, tomo_scans, caplog):
    window = MainWindow()
    qtbot.addWidget(window)

    with open(tmp_path / "config.json", "w") as cfg:
        json.dump(PONI, cfg)
    window.setConfigFilePath(str(tmp_path / "config.json"))

    _create_flats(tmp_path)
    window.setFlatFieldDirName(tmp_path)

    window._processingGroupBox.get2ThCheckBox().click()

    output_dir = tmp_path / "PROCESSED_DATA"
    output_dir.mkdir()
    window._outputWidget.setOutputDirName(output_dir)

    # Launch processing manually (could be done via the GUI later)
    with qtbot.waitSignal(window._executor.finished, timeout=20000):
        window._processScans([ScanEntry(str(tomo_scans), 2)], local=True)

    # Overwrite the files just created

    with caplog.at_level(logging.INFO, logger="ewokscore"):
        with qtbot.waitSignal(window._executor.finished, timeout=20000):
            window._processScans([ScanEntry(str(tomo_scans), 2)], local=True)
        assert (
            "Unable to synchronously create group (name already exists)"
            not in caplog.text
        )

    integration_output_file = output_dir / f"{tomo_scans.stem}.h5"
    assert integration_output_file.exists()


def test_detector_error(qtbot, tmp_path, tomo_scans):
    window = MainWindow()
    qtbot.addWidget(window)

    with open(tmp_path / "config.json", "w") as cfg:
        json.dump(PONI, cfg)
    window.setConfigFilePath(str(tmp_path / "config.json"))

    _create_flats(tmp_path)
    window.setFlatFieldDirName(tmp_path)

    window._processingGroupBox.get2ThCheckBox().click()

    output_dir = tmp_path / "PROCESSED_DATA"
    output_dir.mkdir()
    window._outputWidget.setOutputDirName(output_dir)

    # Launch processing manually (could be done via the GUI later)
    with qtbot.waitSignals(
        [window._executor.jobSubmitted, window._executor.finished],
        order="strict",
        timeout=20000,
    ) as blocker:
        window._processScans([ScanEntry(str(tomo_scans), 3)], local=True)

    # See https://pytest-qt.readthedocs.io/en/latest/signals.html#getting-emitted-signals-and-arguments
    job_item = blocker.all_signals_and_args[0].args[0]
    with pytest.raises(
        RuntimeError,
        match="Execution failed for ewoks task 'integrate' .*: '/3.1/instrument/p4/data'",
    ):
        job_item.getFuture().result()
