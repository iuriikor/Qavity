from dash import html, callback, Input, Output, State, MATCH, callback_context
import uuid
import json
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_daq as ddaq
from dash_iconify import DashIconify

from controllers.sinara.run_artiq_script import run_artiq_in_clang64_visible

# All-in-One Components should be suffixed with 'AIO'
class FrequencyGeneratorInterfaceAIO(html.Div):  # html.Div will be the "parent" component

    class ids:
        freq_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'frequencyCtrl',
            'aio_id': aio_id
        }
        amp_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'amp_ctrl',
            'aio_id': aio_id
        }
        phase_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'phase_ctrl',
            'aio_id': aio_id
        }
        output_on = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'output_on',
            'aio_id': aio_id
        }
        output_updated = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'output_updated',
            'aio_id': aio_id
        }
        # Hidden component for update callback
        update_status = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'update_status',
            'aio_id': aio_id
        }

    # Class level storage for device instances
    # Maps aio_id to (device, channel) pairs
    _devices = {}

    # Define the arguments of the All-in-One component
    def __init__(
            self,
            aio_id=None,
            name=None,
            device=None,
            ch = 0,
    ):

        if aio_id is None: # This should normally never be invoked, but I'll leave it here just in case
            aio_id = str(uuid.uuid4())
        self.name=name
        self._device = device
        self._ch = ch
        # Check if this is a Urukul-type generator
        is_urukul = self._device.get_device_info()['type'] == 'UrukulFrequencyGenerator'

        # Store device in class-level storage
        # This is a CLASS variable, not an OBJECT variable, meaning that ALL objects of the same
        # class will share the same variable. This is why we need a way to distinguish between
        # devices that belong to different AIO components by the AIO id.
        FrequencyGeneratorInterfaceAIO._devices[aio_id] = (device, ch)
        print(self._device.get_device_info())

        # Get current output parameters from the generator
        curr_freq = self._device.get_frequency(self._ch)
        curr_amp = self._device.get_amplitude(self._ch)
        try:
            curr_phase = self._device.get_phase(self._ch)
        except Exception as e:
            print(f"Generator does not have this function, {str(e)}")
            curr_phase = 0

        if is_urukul:
            try:
                self.curr_att = self._device.get_att(self._ch)
            except Exception as e:
                print(f'Generator does not have this function, {str(e)}')
                curr_att = 0.0

        output_is_on =  self._device.get_output_state(self._ch)
        output_is_updated = False
        if is_urukul:
            output_is_updated = self._device.is_up_to_date()

        # Define the component's layout
        layout = dmc.Flex([],
                          direction='column', style={'border': 'solid', 'border-radius': '10px',
                                                     'margin': '10px', 'padding': '10px', 'width': '380px'}
                          )
        # Add hidden status div for update callback
        hidden_status = html.Div(id=self.ids.update_status(aio_id), style={'display': 'none'})
        top_row = dmc.Flex([
                dmc.Text(self.name, size='lg', c='blue'),
                dmc.Switch(label="", labelPosition='top', onLabel="ON", offLabel="OFF",
                           size='lg', color="teal", style={'align-self': 'flex-end'},
                           persistence=1, persistence_type='local',
                           id=self.ids.output_on(aio_id))
                ], justify='space-between')
        top_row_urukul = dmc.Flex([
                dmc.Text(self.name, size='lg', c='blue'),
                dmc.Chip("Updated", checked=output_is_updated,
                         persistence=1, persistence_type='local',
                         id=self.ids.output_updated(aio_id)),
                dmc.Switch(label="", labelPosition='top', onLabel="ON", offLabel="OFF",
                           size='lg', color="teal", style={'align-self': 'flex-end'},
                           persistence=1, persistence_type='local',
                           checked=output_is_on, id=self.ids.output_on(aio_id))
                ], justify='space-between')
        info_row = dmc.Flex(
                [
                dmc.NumberInput(value=curr_freq, label='Frequency', thousandSeparator=" ",
                                w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' Hz',
                                debounce=True, radius=3,
                                persistence=1, persistence_type='local',
                                id=self.ids.freq_ctrl(aio_id)),
                dmc.NumberInput(value=curr_amp, label='Power', suffix=' dBm',
                                w=100, debounce=True, radius=3, allowDecimal=True, decimalScale=2,
                                persistence=1, persistence_type='local',
                                id=self.ids.amp_ctrl(aio_id)),
                dmc.NumberInput(value=curr_phase, label='Phase', suffix=u'\N{DEGREE SIGN}',
                                w=80, debounce=True, radius=3, allowDecimal=False,
                                persistence=1, persistence_type='local',
                                id=self.ids.phase_ctrl(aio_id)),
                        ], justify='space-around', style={}, align='flex-end')
        if is_urukul:
            layout.children = [hidden_status, top_row_urukul, info_row]
        else:
            layout.children = [hidden_status, top_row, info_row]

        super().__init__(layout)

    @staticmethod
    def get_aio_id_from_trigger():
        """Extract aio_id from the component that triggered the callback"""
        # Get the ID of the component that triggered the callback
        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        # The ID is a JSON string that we need to parse
        id_dict = json.loads(triggered_id)
        return id_dict['aio_id']

    @callback(
        Output(ids.output_updated(MATCH), 'checked'),
        Input(ids.freq_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_frequency(freq):
        print("FREQUENCY CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = FrequencyGeneratorInterfaceAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = FrequencyGeneratorInterfaceAIO._devices[aio_id]

        print(f"FREQUENCY UPDATED to {freq} Hz for device {aio_id}, channel {ch}")
        device.set_frequency(freq, ch)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.amp_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_amplitude(amp):
        print("AMPLITUDE CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = FrequencyGeneratorInterfaceAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = FrequencyGeneratorInterfaceAIO._devices[aio_id]

        print(f"AMPLITUDE UPDATED to {amp} dBm for device {aio_id}, channel {ch}")
        device.set_amplitude(amp, ch)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.phase_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_phase(phase):
        # Get the aio_id from the triggered component
        aio_id = FrequencyGeneratorInterfaceAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = FrequencyGeneratorInterfaceAIO._devices[aio_id]

        try:
            print(f"PHASE UPDATED to {phase}° for device {aio_id}, channel {ch}")
            device.set_phase(phase, ch)
        except Exception as e:
            print(f"Failed to set phase: {str(e)}")
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.output_on(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def on_off_switch(is_on):
        # Get the aio_id from the triggered component
        aio_id = FrequencyGeneratorInterfaceAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = FrequencyGeneratorInterfaceAIO._devices[aio_id]

        print(f"OUTPUT {'ON' if is_on else 'OFF'} for device {aio_id}, channel {ch}")
        if is_on:
            device.output_on(ch)
        else:
            device.output_off(ch)
        return False
