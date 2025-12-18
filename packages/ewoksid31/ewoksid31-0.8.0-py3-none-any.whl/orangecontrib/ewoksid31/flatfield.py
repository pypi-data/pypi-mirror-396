from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.gui.parameterform import ParameterForm

from ewoksid31.tasks.flatfield import FlatFieldFromEnergy


class OWFlatFieldFromEnergy(  # type: ignore[call-arg]
    OWEwoksWidgetOneThread,
    ewokstaskclass=FlatFieldFromEnergy,
):
    name = "FlatFieldFromEnergy"
    description = "Interpolate an energy-stack of flat-field images"
    icon = "icons/widget.png"
    want_main_area = False

    def __init__(self):
        super().__init__()
        self._init_control_area()

        self._parameter_form = ParameterForm(parent=self.controlArea)
        self._parameter_form.addParameter(
            "newflat",
            label="New flat filename",
            value_for_type="",
            select="file",
            value_change_callback=self._inputs_changed,
        )
        self._parameter_form.addParameter(
            "oldflat",
            label="Old flat filename",
            value_for_type="",
            select="file",
            value_change_callback=self._inputs_changed,
        )
        self._parameter_form.addParameter(
            "energy",
            label="X-Ray energy in KeV",
            value_for_type=0.0,
            value_change_callback=self._inputs_changed,
        )
        self._update_parameter_values()

        self.controlArea.layout().addStretch(1)

    def _inputs_changed(self):
        new_values = self._parameter_form.get_parameter_values()
        self.update_default_inputs(**new_values)

    def _update_parameter_values(self):
        initial_values = self.get_default_input_values()
        self._parameter_form.set_parameter_values(initial_values)
