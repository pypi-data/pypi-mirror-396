import h5py
import numpy as np
import pytest

from ewoksid31.tasks.tomo import SaveNexusPatternsAsId31TomoHdf5


def test_SaveNexusPatternsAsId31TomoHdf5(
    tmp_path,
    tomo_scans,
    integrated_scan,
):

    output_filename = str(tmp_path / "result.h5")
    inputs = {
        "scan_entry_url": f"{tomo_scans}::/2.1",
        "rot_name": "nth",
        "y_name": "ny",
        "nxdata_url": f"{integrated_scan}::/integrated",
        "output_filename": output_filename,
    }

    task = SaveNexusPatternsAsId31TomoHdf5(inputs=inputs)
    task.execute()
    assert task.outputs.filename == output_filename

    with h5py.File(integrated_scan, "r") as integrated_file:
        q = integrated_file["integrated/q"][()]
        intensity = integrated_file["integrated/intensity"][()]

    with h5py.File(tomo_scans, "r") as raw_data_file:
        nth = raw_data_file["2.1/measurement/nth"][()]
        ny = raw_data_file["2.1/measurement/ny"][()]

    with h5py.File(output_filename) as h5f:
        assert np.array_equal(h5f["XRD"][()], intensity)
        assert np.array_equal(h5f["q"][()], q)
        assert h5f["q"].attrs["units"] == "nm^-1"
        assert np.array_equal(h5f["th"][()], nth)
        assert h5f["th"].attrs["units"] == "deg"
        assert np.array_equal(h5f["y"][()], ny)
        assert h5f["y"].attrs["units"] == "mm"


def test_overwrite_SaveNexusPatternsAsId31TomoHdf5(
    tmp_path,
    tomo_scans,
    integrated_scan,
):

    output_filename = str(tmp_path / "result.h5")

    # Create output file to simulate conflict
    with h5py.File(output_filename, "w") as h5f:
        h5f.create_group("dummy")

    inputs = {
        "scan_entry_url": f"{tomo_scans}::/2.1",
        "rot_name": "nth",
        "y_name": "ny",
        "nxdata_url": f"{integrated_scan}::/integrated",
        "output_filename": output_filename,
    }

    # Check that it fails without overwrite
    task_without_overwrite = SaveNexusPatternsAsId31TomoHdf5(inputs=inputs)
    with pytest.raises(RuntimeError) as exc:
        task_without_overwrite.execute()
    original_exc = exc.value.__cause__
    assert isinstance(original_exc, FileExistsError)
    assert (
        str(original_exc)
        == f"{output_filename} already exists. Use overwrite=True to replace it."
    )

    # Check that it pass with overwrite=True
    task_with_overwrite = SaveNexusPatternsAsId31TomoHdf5(
        inputs={
            **inputs,
            "overwrite": True,
        }
    )
    task_with_overwrite.execute()
    assert task_with_overwrite.outputs.filename == output_filename
