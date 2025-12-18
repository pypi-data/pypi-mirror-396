import h5py
import numpy

from ..tasks.flatfield import FlatFieldFromEnergy
from .resources import resource_filename


def test_flatfield():
    inputs = {
        "newflat": resource_filename("flats.mat"),
        "oldflat": resource_filename("flats_old.mat"),
        "energy": 90.0,
    }
    task = FlatFieldFromEnergy(inputs=inputs)
    task.execute()
    # Flat-field correction:
    #  Icor = I * 0.8115191925457376 = I / flatfield
    numpy.testing.assert_allclose(1 / task.outputs.flatfield[0, 0], 0.8115191925457376)


def test_flatfield_energy_url(tmp_path):
    filepath = tmp_path / "flatfield.h5"
    datapath = "/1.1/instrument/energy"
    with h5py.File(filepath, "w") as h5f:
        h5f[datapath] = 90

    inputs = {
        "newflat": resource_filename("flats.mat"),
        "oldflat": resource_filename("flats_old.mat"),
        "energy": f"{str(filepath)}::{datapath}",
    }

    task = FlatFieldFromEnergy(inputs=inputs)
    task.execute()
    # Flat-field correction:
    #  Icor = I * 0.8115191925457376 = I / flatfield
    numpy.testing.assert_allclose(1 / task.outputs.flatfield[0, 0], 0.8115191925457376)


def test_flatfield_disabled():
    inputs = {
        "newflat": resource_filename("flats.mat"),
        "oldflat": resource_filename("flats_old.mat"),
        "energy": 90.0,
        "enabled": False,
    }
    task = FlatFieldFromEnergy(inputs=inputs)
    task.execute()
    assert task.outputs.flatfield is None
