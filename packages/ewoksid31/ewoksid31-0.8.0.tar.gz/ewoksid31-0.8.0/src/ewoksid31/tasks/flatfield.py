import logging

import ewoksdata.data.bliss
import numpy
from ewokscore import Task
from ewokscore.model import BaseInputModel
from pydantic import Field
from scipy.io import loadmat

_logger = logging.getLogger(__name__)


class Inputs(BaseInputModel):
    newflat: str = Field(
        description="Filename of ID31 P3 detector flatfield",
        examples=["/data/id31/inhouse/P3/flats.mat"],
    )
    oldflat: str = Field(
        description="Filename of ID31 P3 detector 'old' flatfield",
        examples=["/data/id31/inhouse/P3/flats_old.mat"],
    )
    energy: float | str = Field(
        description="X-ray energy in KeV or URL of hdf5 dataset storing its value",
        examples=[75.0, "/path/to/file.f5::/2.1/instrument/positioners/energy"],
    )
    enabled: bool = True


class FlatFieldFromEnergy(Task, input_model=Inputs, output_names=["flatfield"]):  # type: ignore[call-arg]
    """Interpolate an energy-stack of flat-field images.

    The resulting flat-field image can be used as follows
    to correct diffraction patterns for flat field:

    .. code::

        Icor = I / flatfield

    Output:

    - flatfield: 2D numpy.ndarray
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())

        if not inputs.enabled:
            _logger.info(
                f"Task {self.__class__.__qualname__} is disabled: No flatfield"
            )
            self.outputs.flatfield = None
            return

        if isinstance(inputs.energy, str):
            energy = ewoksdata.data.bliss.get_data(inputs.energy)
        else:
            energy = inputs.energy

        new_flat = _interpolated_flatfield(inputs.newflat, "E", "F", energy)
        old_flat = _interpolated_flatfield(inputs.oldflat, "Eold", "Fold", energy)
        flatfield = old_flat / new_flat
        flatfield[~numpy.isfinite(flatfield)] = 1
        flatfield[flatfield < 0] = 1
        self.outputs.flatfield = flatfield


def _interpolated_flatfield(
    matlab_filename: str, energy_key: str, flatfield_key: str, energy: float
) -> numpy.ndarray:
    """
    :param matlab_filename: matlab file from ID31 that contains an energy-stack of images
    :param energy_key:
    :param flatfield_key:
    :param energy:
    :return: interpolated image (nrow, ncol)
    """
    m = loadmat(matlab_filename)
    flatfields = m[flatfield_key]
    energies = numpy.squeeze(m[energy_key]).astype(float)
    return _interpolate_flatfields(energies, flatfields, energy)


def _interpolate_flatfields(
    energies: numpy.ndarray, flatfields: numpy.ndarray, energy: float
) -> numpy.ndarray:
    """
    :param energies: array of energies (nenergies,)
    :param flatfields: stack of images (nrow, ncol, nenergies)
    :param energy:
    :return: interpolated image (nrow, ncol)
    """
    j = numpy.argsort(abs(energies - energy))[0:2]
    j.sort()
    j_before, j_after = j
    e_before = energies[j_before]
    e_after = energies[j_after]
    w_before = (e_after - energy) / (e_after - e_before)
    w_after = (energy - e_before) / (e_after - e_before)
    f_before = flatfields[..., j_before]
    f_after = flatfields[..., j_after]
    return w_before * f_before + w_after * f_after
