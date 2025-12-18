import argparse
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Literal

import matplotlib
from ewoks import execute_graph
from ewoksutils.task_utils import task_inputs

try:
    from ewoksjob.client import submit
except ImportError:
    submit = None

from .utils import (
    NEWFLAT_FILENAME,
    OLDFLAT_FILENAME,
    print_inputs,
)


@dataclass
class Defaults:
    calibrant: str
    max_rings: list[int]
    sample: str


Kinds = Literal["PDF", "XRD", "SAXS"]


DEFAULTS: dict[Kinds, Defaults] = {
    "PDF": Defaults(
        calibrant="LaB6_SRM660c",
        max_rings=[1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 35],
        sample="ESRF_HR_01",
    ),
    "XRD": Defaults(
        calibrant="LaB6_SRM660c",
        max_rings=[1, 4, 7, 10, 13, 16, 19, 20],
        sample="ESRF_HR_01",
    ),
    "SAXS": Defaults(
        calibrant="AgBh",
        max_rings=[1, 4],
        sample="ESRF_HR_16",
    ),
}


def streamline_autocalib_workflow_inputs(
    output_dir: str,
    kind: Kinds,
    detector: str,
    pyfai_config: str,
    energy: float,
    newflat: str,
    oldflat: str,
    bliss_scan_url: str,
    input_image_url: str,
    calibrant: str | None = None,
    max_rings: int | list[int] | None = None,
    isinteractive: bool = False,
) -> list[dict[str, Any]]:
    """Generate the list of inputs for the streamline_autocalib workflow"""
    if calibrant is None:
        calibrant = DEFAULTS[kind].calibrant

    if max_rings is None:
        max_rings = DEFAULTS[kind].max_rings

    inputs = []
    inputs += task_inputs(
        task_identifier="FlatFieldFromEnergy",
        inputs={"energy": energy, "newflat": newflat, "oldflat": oldflat},
    )
    inputs += task_inputs(
        task_identifier="PyFaiConfig",
        inputs={
            "filename": pyfai_config,
            "calibrant": calibrant,
        },
    )
    inputs += task_inputs(
        task_identifier="CalibrateSingle",
        inputs={"image": input_image_url, "max_rings": max_rings},
    )
    inputs += task_inputs(  # Both 1D and 2D
        task_identifier="IntegrateSinglePattern",
        inputs={"image": input_image_url},
    )
    inputs += task_inputs(
        task_identifier="SaveNexusPattern1D",
        inputs={
            "url": os.path.join(output_dir, f"result_{kind}.h5"),
            "bliss_scan_url": bliss_scan_url,
            "nxprocess_name": f"{detector}_integrate_q",
            "nxmeasurement_name": f"{detector}_integrate_q",
        },
    )
    inputs += task_inputs(  # Save 2D
        task_identifier="SaveNexusIntegrated",
        inputs={
            "url": os.path.join(output_dir, f"result_{kind}.h5"),
            "bliss_scan_url": bliss_scan_url,
            "nxprocess_name": f"{detector}_integrate2d_q",
        },
    )
    inputs += task_inputs(
        task_identifier="DiagnoseCalibrateSingleResults",
        inputs={
            "image": input_image_url,
            "show": isinteractive,
            "filename": os.path.join(output_dir, f"plot_ring_detection_{kind}.svg"),
        },
    )
    inputs += task_inputs(
        task_identifier="DiagnoseIntegrate1D",
        inputs={
            "show": isinteractive,
            "filename": os.path.join(output_dir, f"plot_calibration_{kind}.svg"),
        },
    )
    inputs += task_inputs(
        task_identifier="SavePyFaiPoniFile",
        inputs={
            "output_filename": os.path.join(output_dir, f"calibration_{kind}.poni"),
        },
    )
    inputs += task_inputs(
        task_identifier="SavePyFaiConfig",
        inputs={
            "output_filename": os.path.join(output_dir, f"{kind}.json"),
        },
    )
    return inputs


def create_argument_parser():
    today = time.strftime("%Y%m%d", time.localtime())
    default_session = f"in1176/id31/{today}"
    default_dataset_id = 1
    default_detector = "p4"

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-k",
        "--kind",
        type=str,
        required=True,
        help="Kind of streamline measurment: pdf, xrd, saxs",
    )
    parser.add_argument(
        "--session",
        type=str,
        default=default_session,
        help=f"Session as: <proposal>/<beamline>/<session> (default: {default_session})",
    )
    parser.add_argument(
        "--sample",
        type=str,
        default=None,
        help="Sample name (default depends on kind argument)",
    )
    parser.add_argument(
        "--dataset",
        type=int,
        default=default_dataset_id,
        help=f"Dataset number (default: {default_dataset_id})",
    )
    parser.add_argument(
        "--detector",
        type=str,
        default=default_detector,
        help=f"Detector name (default: {default_detector})",
    )

    calibration_group = parser.add_argument_group("Calibration")
    calibration_group.add_argument(
        "--calibrant",
        type=str,
        default=None,
        help="Name of the calibrant used for calibration image (default depends on kind argument)",
    )
    calibration_group.add_argument(
        "--max-rings",
        type=int,
        required=False,
        nargs="+",
        help="Number of rings to use. Use multiple values to refine over an increasing number of rings (default depends on kind argument)",
        default=None,
    )

    runtime_group = parser.add_argument_group("Runtime")
    runtime_group.add_argument(
        "--worker",
        action="store_true",
        help="Execute workflows on ewoks worker instead of current environment",
    )
    runtime_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity",
    )
    runtime_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not run anything but print which datasets would be processed",
    )

    extra_group = parser.add_argument_group(
        "Extra", "Overrides configuration from session, sample & dataset"
    )
    extra_group.add_argument(
        "-i",
        "--input",
        type=str,
        help="Dataset file to process (HDF5 format)",
        metavar="FILE",
    )
    extra_group.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="Folder where to store the results",
        metavar="FOLDER",
    )
    extra_group.add_argument(
        "-c",
        "--pyfai-config",
        type=str,
        help="PyFAI config file (.json)",
        metavar="FILE",
    )
    extra_group.add_argument(
        "--flat-dir",
        type=str,
        help="Folder containing flat field files: flats.mat and old_flats.mat",
        metavar="FOLDER",
    )

    return parser


def main():
    logging.basicConfig(level=logging.WARNING)

    parser = create_argument_parser()
    options = parser.parse_args()

    if options.verbose != 0:
        logging.getLogger().setLevel(
            logging.INFO if options.verbose == 1 else logging.DEBUG
        )

    kind = options.kind.upper()
    if kind not in DEFAULTS:
        raise ValueError(f"Unsupported kind: {kind}")

    # Use session, sample and dataset to set paths
    session_dir = os.path.join("/data/visitor", options.session)
    sample = options.sample if options.sample is not None else DEFAULTS[kind].sample
    input_filename = os.path.join(
        session_dir,
        "RAW_DATA",
        sample,
        f"{sample}_{options.dataset:04d}",
        f"{sample}_{options.dataset:04d}.h5",
    )
    processed_data_dir = os.path.join(session_dir, "PROCESSED_DATA")
    pyfai_config = os.path.join(processed_data_dir, "calibration", f"{kind}_ref.json")
    flat_dir = os.path.join(processed_data_dir, "extra_files")
    output_dir = os.path.join(processed_data_dir, "calibration", f"{kind}_calibration")

    # Overrides from command line
    if options.input:
        input_filename = os.path.abspath(options.input)
    if options.pyfai_config:
        pyfai_config = options.pyfai_config
    if options.flat_dir:
        flat_dir = os.path.abspath(options.flat_dir)
    if options.output_dir:
        output_dir = os.path.abspath(options.output_dir)

    inputs = streamline_autocalib_workflow_inputs(
        output_dir=output_dir,
        kind=kind,
        detector=options.detector,
        pyfai_config=pyfai_config,
        energy=f"{input_filename}::/1.1/instrument/positioners/energy",
        newflat=os.path.join(flat_dir, NEWFLAT_FILENAME),
        oldflat=os.path.join(flat_dir, OLDFLAT_FILENAME),
        bliss_scan_url=f"{input_filename}::/1.1",
        input_image_url=f"silx://{input_filename}?path=/1.1/measurement/{options.detector}&slice=0",
        calibrant=options.calibrant,
        max_rings=options.max_rings,
        isinteractive=not options.worker,
    )
    print("Worflow inputs:")
    print_inputs(inputs)

    if options.dry_run:
        return

    if os.path.exists(output_dir):
        raise RuntimeError(f"Output directory already exists: {output_dir}")

    os.makedirs(output_dir)

    print("Execute workflow...")
    workflow = "streamline_autocalib.json"
    workflow_load_options = {"root_module": "ewoksid31.workflows"}
    convert_destination = os.path.join(output_dir, "calibration_workflow.json")
    if options.worker:
        if submit is None:
            raise RuntimeError("Cannot submit workflow to worker: Install ewoksjob")
        future = submit(
            args=(workflow,),
            kwargs={
                "inputs": inputs,
                "convert_destination": convert_destination,
                "load_options": workflow_load_options,
            },
        )
        future.get()
    else:
        # Fix backend set by ewoksxrpd for interactive use
        import ewoksxrpd  # noqa

        matplotlib.use("Qt5Agg")

        _ = execute_graph(
            workflow,
            inputs=inputs,
            convert_destination=convert_destination,
            load_options=workflow_load_options,
        )
    print("Done")


if __name__ == "__main__":
    import sys

    sys.exit(main())
