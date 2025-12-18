from datetime import datetime
from pathlib import Path

import h5py
import numpy
import pytest
from silx.io.dictdump import dicttonx

DETECTOR_SHAPE = (1679, 1475)


@pytest.fixture()
def tomo_scans(tmpdir, n_frames=10):
    scan_dir = Path(tmpdir / "RAW_DATA")
    scan_dir.mkdir()
    scan_file = scan_dir / "scan.h5"
    with h5py.File(scan_file, "w") as h5f:
        scan_group = h5f.create_group("/2.1")
        dicttonx(
            {
                "end_time": str(datetime.now()),
                "instrument": {
                    "nth": {
                        "data": numpy.linspace(90, 45, n_frames),
                        "data@units": "deg",
                    },
                    "ny": {"data": numpy.linspace(0, 2, n_frames), "data@units": "mm"},
                    "p4": {"data": numpy.zeros((n_frames, *DETECTOR_SHAPE))},
                    "positioners": {"energy": 75.0},
                },
                "measurement": {
                    ">nth": "../instrument/nth/data",
                    ">ny": "../instrument/ny/data",
                    ">p4": "../instrument/p4/data",
                    "scaled_mondio": numpy.ones((n_frames,)),
                },
            },
            scan_group,
        )
        scan_group = h5f.create_group("/3.1")
        dicttonx(
            {
                "end_time": str(datetime.now()),
                "instrument": {
                    "nth": {
                        "data": numpy.linspace(90, 45, n_frames),
                        "data@units": "deg",
                    },
                    "ny": {"data": numpy.linspace(0, 2, n_frames), "data@units": "mm"},
                    "perkin": {"data": numpy.zeros((n_frames, *DETECTOR_SHAPE))},
                    "positioners": {"energy": 75.0},
                },
                "measurement": {
                    ">nth": "../instrument/nth/data",
                    ">ny": "../instrument/ny/data",
                    ">perkin": "../instrument/perkin/data",
                    "scaled_mondio": numpy.ones((n_frames,)),
                },
            },
            scan_group,
        )

    return scan_file


@pytest.fixture
def integrated_scan(tmp_path) -> Path:
    intensities = numpy.ones((6, 100))
    q = numpy.arange(100)

    # Create integrated.h5
    integrated_patterns_file = tmp_path / "integrated.h5"
    with h5py.File(integrated_patterns_file, "w") as h5f:
        dicttonx(
            {
                "integrated": {
                    "@NX_class": "NXdata",
                    "@signal": "intensity",
                    "@axes": ["points", "q"],
                    "intensity": intensities,
                    "points": numpy.arange(6),
                    "q": q,
                    "q@units": "nm^-1",
                },
            },
            h5f,
        )

    return integrated_patterns_file
