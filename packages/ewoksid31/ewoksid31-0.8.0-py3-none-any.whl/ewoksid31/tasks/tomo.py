import logging
import os
from dataclasses import dataclass

import h5py
import numpy
from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewoksxrpd.tasks.utils.ascii_utils import ensure_parent_folder
from pydantic import Field
from silx.io import h5py_utils
from silx.io.nxdata import NXdata
from silx.io.url import DataUrl

logger = logging.getLogger(__name__)


class Inputs(BaseInputModel):
    scan_entry_url: str = Field(
        description="HDF5 URL to the NXentry group containing the 'measurement' group",
        examples=["/path/to/raw_data/file.f5::/2.1"],
    )
    rot_name: str = Field(
        description="Dataset name in 'measurement' for rotation angles",
        examples=["nth"],
    )
    y_name: str = Field(
        description="Dataset name in 'measurement' for horizontal positions",
        examples=["ny"],
    )
    nxdata_url: str = Field(
        description="HDF5 URL to the NXdata group containing integrated patterns",
        examples=["/path/to/processed_data/file.f5::/2.1/p4_integrate/integrated"],
    )
    output_filename: str = Field(
        description="Path to the output HDF5 file",
        examples=["/path/to/processed_data/tomo.f5"],
    )
    enabled: bool = True
    overwrite: bool = False
    retry_timeout: float | None = Field(
        default=None,
        description="Duration in seconds for which to try to open HDF5 files",
    )
    retry_period: float | None = Field(
        default=None,
        description="Amount of time in seconds between each attempt to open HDF5 files",
    )


@dataclass
class IntegratedPatterns:
    """Store multiple pyFAI integrated patterns"""

    radial: numpy.ndarray
    radial_name: str
    radial_units: str
    intensities: numpy.ndarray


class SaveNexusPatternsAsId31TomoHdf5(Task, input_model=Inputs, output_names=["filename"]):  # type: ignore[call-arg]
    """Save integrated XRD patterns into an HDF5 file compatible with ID31 tomography workflow.

    Output:

    - filename (str): Path to the written HDF5 file, or empty string if skipped.
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())

        if not inputs.enabled:
            logger.info(
                f"Task {self.__class__.__qualname__} is disabled: No file is saved"
            )
            self.outputs.filename = ""
            return

        ensure_parent_folder(inputs.output_filename)

        scan_entry_url = DataUrl(inputs.scan_entry_url)
        with h5py_utils.open_item(
            scan_entry_url.file_path(),
            scan_entry_url.data_path(),
            retry_timeout=inputs.retry_timeout,
            retry_period=inputs.retry_period,
        ) as scan_entry:
            measurement = scan_entry["measurement"]

            th_angles_dataset = measurement[inputs.rot_name]
            th_angles = th_angles_dataset[()]
            th_angles_units = th_angles_dataset.attrs.get("units", None)

            y_positions_dataset = measurement[inputs.y_name]
            y_positions = y_positions_dataset[()]
            y_positions_units = y_positions_dataset.attrs.get("units", None)

        nxdata_url = DataUrl(inputs.nxdata_url)
        with h5py_utils.open_item(
            nxdata_url.file_path(),
            nxdata_url.data_path(),
            retry_timeout=inputs.retry_timeout,
            retry_period=inputs.retry_period,
        ) as group:
            patterns = _read_nexus_integrated_patterns(group)

        if inputs.overwrite:
            mode = "w"
        else:
            mode = "a"

        if os.path.exists(inputs.output_filename) and not inputs.overwrite:
            raise FileExistsError(
                f"{inputs.output_filename} already exists. Use overwrite=True to replace it."
            )

        with h5py.File(inputs.output_filename, mode) as h5f:
            h5f["XRD"] = patterns.intensities

            h5f[patterns.radial_name] = patterns.radial
            if patterns.radial_units:
                h5f[patterns.radial_name].attrs["units"] = patterns.radial_units

            h5f["y"] = y_positions
            if y_positions_units is not None:
                h5f["y"].attrs["units"] = y_positions_units

            h5f["th"] = th_angles
            if th_angles_units is not None:
                h5f["th"].attrs["units"] = th_angles_units

        self.outputs.filename = inputs.output_filename


def _read_nexus_integrated_patterns(group: h5py.Group) -> IntegratedPatterns:
    """Read integrated patterns from a HDF5 NXdata group.

    It reads from both single (1D signal) or multi (2D signal) NXdata.
    """
    nxdata = NXdata(group)
    if not nxdata.is_valid:
        raise RuntimeError(
            f"Cannot parse NXdata group: {group.file.filename}::{group.name}"
        )
    if not (nxdata.signal_is_1d or nxdata.signal_is_2d):
        raise RuntimeError(
            f"Signal is not a 1D or 2D dataset: {group.file.filename}::{group.name}"
        )

    if nxdata.axes[-1] is None:
        radial = numpy.arange(nxdata.signal.shape[-1])
        radial_name = "radial"
        radial_units = ""
    else:
        axis_dataset = nxdata.axes[-1]
        radial = axis_dataset[()]
        radial_name = nxdata.axes_dataset_names[-1]
        radial_units = axis_dataset.attrs.get("units", "")

    intensities = numpy.atleast_2d(nxdata.signal)

    return IntegratedPatterns(radial, radial_name, radial_units, intensities)
