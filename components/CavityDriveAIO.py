from dash import html, callback, Input, Output, State, MATCH, callback_context, no_update
import uuid
import json
import dash_mantine_components as dmc
import dash_core_components as dcc

from controllers.sinara.run_artiq_script import run_artiq_in_clang64_visible
from config import config, update_config

# All-in-One Components should be suffixed with 'AIO'
class CavityDriveAIO(html.Div):  # html.Div will be the "parent" component

    class ids:
        curr_freq_ctrl = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'curr_freq_ctrl',
            'aio_id': aio_id
        }
        end_freq_ctrl = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'end_freq_ctrl',
            'aio_id': aio_id
        }
        freq_step_ctrl = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'freq_step_ctrl',
            'aio_id': aio_id
        }
        freq_step_delay_ctrl = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'freq_step_delay_ctrl',
            'aio_id': aio_id
        }
        attenuation_ctrl = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'attenuation_ctrl',
            'aio_id': aio_id
        }
        output_on = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'output_on',
            'aio_id': aio_id
        }
        output_updated = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'output_updated',
            'aio_id': aio_id
        }
        scan_freq_btn = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'scan_freq_btn',
            'aio_id': aio_id
        }
        constant_output_btn = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'constant_output_btn',
            'aio_id': aio_id
        }
        cav_tem00_tem01_diff = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'cav_tem00_tem01_diff',
            'aio_id': aio_id
        }
        curr_detuning = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'curr_detuning',
            'aio_id': aio_id
        }
        # Hidden component for update callback
        update_status = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'update_status',
            'aio_id': aio_id
        }
        # Storage to keep device properties
        module_props_store = lambda aio_id: {
            'component': 'CavityDriveAIO',
            'subcomponent': 'device_props_store',
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
        # Store device in class-level storage
        # This is a CLASS variable, not an OBJECT variable, meaning that ALL objects of the same
        # class will share the same variable. This is why we need a way to distinguish between
        # devices that belong to different AIO components by the AIO id.
        CavityDriveAIO._devices[aio_id] = (device, ch)
        print(self._device.get_device_info())

        # Load module-specific properties
        module_props = config.get(name, {})
        curr_freq_kHz = module_props.get('Output frequency', self._device.get_frequency(self._ch)/1e03)
        curr_att_dB = module_props.get('Output attenuation', self._device.get_attenuation(self._ch))
        output_is_on = module_props.get('Output on', True)
        output_is_updated = module_props.get('Scripts updated', False)
        ramp_props = module_props.get('Ramp', {})
        ramp_freq_start_kHz = ramp_props.get('Starting frequency kHz', self._device.get_frequency(self._ch)/1e03)
        ramp_freq_end_kHz = ramp_props.get('Ending frequency kHz', self._device.get_frequency(self._ch)/1e03)
        ramp_freq_step = ramp_props.get('Frequency step kHz', 1)
        ramp_delay = ramp_props.get('Delay seconds', 0.1)
        tem00_tem01_spacing = module_props.get('TEM00 - TEM01 separation kHz', 488457.0)
        # Load device-specific properties - I'll leave it here as an idea for future update

        # Update device
        self._device.update_properties_from_dict(module_props | ramp_props)

        # Layout
        # Config storage
        config_store = dcc.Store(
            id=self.ids.module_props_store(aio_id),
            data={self.name : module_props},
        )
        # Add hidden status div for update callback
        hidden_status = html.Div(id=self.ids.update_status(aio_id), style={'display': 'none'})
        top_row = dmc.Flex([
            dmc.Text(self.name, size='lg', c='blue'),
            dmc.Chip("Updated", checked=output_is_updated,
                     persistence=1, persistence_type='local',
                     id=self.ids.output_updated(aio_id)),
            dmc.Switch(label="", labelPosition='top', onLabel="ON", offLabel="OFF",
                       size='lg', color="teal", style={'align-self': 'flex-end'},
                       persistence=1, persistence_type='local',
                       checked=output_is_on, id=self.ids.output_on(aio_id))
        ], justify='space-between')
        output_row = dmc.Flex(
            [
                dmc.NumberInput(value=ramp_freq_start_kHz, label='Current Frequency', thousandSeparator=" ",
                                w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' kHz',
                                debounce=True, radius=3,
                                persistence=1, persistence_type='local',
                                id=self.ids.curr_freq_ctrl(aio_id)),
                dmc.NumberInput(value=ramp_freq_end_kHz, label='Final Frequency', thousandSeparator=" ",
                                w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' kHz',
                                debounce=True, radius=3,
                                persistence=1, persistence_type='local',
                                id=self.ids.end_freq_ctrl(aio_id)),
                dmc.NumberInput(value=curr_att_dB, label='Att', suffix=' dB',
                                w=80, debounce=True, radius=3, allowDecimal=True, decimalScale=1,
                                persistence=1, persistence_type='local',
                                id=self.ids.attenuation_ctrl(aio_id)),
            ], justify='space-around', style={}, align='flex-end', direction = 'row', gap='sm')
        ramp_row = dmc.Flex([
            dmc.NumberInput(value=ramp_freq_step, label='Step', w=100, stepHoldDelay=500, stepHoldInterval=100,
                            suffix=' kHz', debounce=True, radius=3,
                            persistence=1, persistence_type='local',
                            id=self.ids.freq_step_ctrl(aio_id)),
            dmc.NumberInput(value=ramp_delay, label='Delay', w=100, stepHoldDelay=500, stepHoldInterval=100,
                            suffix=' s', debounce=True, radius=3,
                            persistence=1, persistence_type='local',
                            id=self.ids.freq_step_delay_ctrl(aio_id))
        ], direction='row', justify='space-between', align='flex-end')
        control_row = dmc.Flex([
            dmc.Button('Ramp', id=self.ids.scan_freq_btn(aio_id)),
            dmc.Button('Single tone', id=self.ids.constant_output_btn(aio_id)),
        ], justify='center', align='flex-end', direction='row', py='xs', gap='xl')
        info_row = dmc.Flex([
            dmc.NumberInput(value=tem00_tem01_spacing, label='TEM01-TEM00 spacing', suffix=' kHz',
                            w=150, debounce=True, radius=3, allowDecimal=True, decimalScale=2,
                            persistence=1, persistence_type='local',
                            id=self.ids.cav_tem00_tem01_diff(aio_id)),
            dmc.NumberInput(value=0, label='Detuning', suffix=' kHz',
                            w=150, radius=3, allowDecimal=True, decimalScale=1,
                            persistence=1, persistence_type='local',
                            disabled=True, hideControls=True,
                            id=self.ids.curr_detuning(aio_id))
        ], justify='space-between', align='flex-end', direction='row')

        layout=dmc.Card([
            dmc.CardSection(children=top_row, withBorder=True, py="xs", inheritPadding=True),
            # dmc.Divider(mt='sm', mb='sm'),
            output_row,
            ramp_row,
            control_row,
            dmc.Divider(mt='xs', mb='xs'),
            info_row,
            hidden_status,
            config_store
        ])

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
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.curr_freq_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_current_frequency(freq):
        """
        Updates Mirny generator frequency in the device object properties.
        Also updates starting frequency of the ramp in the device properties.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # print("FREQUENCY CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"FREQUENCY UPDATED to {freq} kHz for device {aio_id}, channel {ch}")
        device.set_frequency(freq*1e03, ch)
        device.set_ramp_starting_freq(freq)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.attenuation_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_attenuation(attenuation):
        """
        Updates Mirny generator attenuation in the device object properties.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # print("ATTENUATION CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()
        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"AMPLITUDE UPDATED to {attenuation} dBm for device {aio_id}, channel {ch}")
        device.set_attenuation(attenuation, ch)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.output_on(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def on_off_switch(is_on):
        """
        Updates Mirny generator output state in the device object properties.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"OUTPUT {'ON' if is_on else 'OFF'} f2or device {aio_id}, channel {ch}")
        if is_on:
            device.output_on(ch)
        else:
            device.output_off(ch)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.output_updated(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def update_all_scripts(script_isuptodate):
        """
        Updates Artiq scripts for using Mirny as single constant tone output generator
        and for frequency ramp. Pushes properties that are stored in device dictionaries
        into the actual script.
        :return:
        """
        if (script_isuptodate):
            # Get the aio_id from the triggered component
            aio_id = CavityDriveAIO.get_aio_id_from_trigger()
            # Get the device and channel
            device, ch = CavityDriveAIO._devices[aio_id]
            device.update_freq_gen_script()
            device.update_freq_ramp_script()
            return script_isuptodate
        return script_isuptodate

    @callback(
        Output(ids.module_props_store(MATCH), 'data', allow_duplicate=True),
        Input(ids.output_updated(MATCH), 'checked'),
        State(ids.module_props_store(MATCH), 'data'),
        State(ids.curr_freq_ctrl(MATCH), 'value'),
        State(ids.attenuation_ctrl(MATCH), 'value'),
        State(ids.end_freq_ctrl(MATCH), 'value'),
        State(ids.freq_step_ctrl(MATCH), 'value'),
        State(ids.freq_step_delay_ctrl(MATCH), 'value'),
        State(ids.output_on(MATCH), 'checked'),
        State(ids.cav_tem00_tem01_diff(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_config_file(output_updated, cfg_data, curr_freq_kHz, att_dB,
                           end_freq_kHz, freq_step_kHz, delay_s, output_ison, tem00_tem01_det):
        if output_updated:
            new_config = {}
            new_config["Output frequency"] = curr_freq_kHz
            new_config["Output attenuation"] = att_dB
            new_config["Output on"] = output_ison
            new_config["TEM00 - TEM01 separation kHz"] = tem00_tem01_det
            new_config["Scripts updated"] = output_updated
            new_config["Ramp"] = {}
            new_config["Ramp"]["Starting frequency kHz"] = curr_freq_kHz
            new_config["Ramp"]["Ending frequency kHz"] = end_freq_kHz
            new_config["Ramp"]["Frequency step kHz"] = freq_step_kHz
            new_config["Ramp"]["Delay seconds"] = delay_s

            module_name = list(cfg_data)[0]
            update_config(new_data={module_name:new_config})
            return {module_name:new_config}
        else:
            return no_update


    @callback(
        Output(ids.update_status(MATCH), "children", allow_duplicate=True),
        Input(ids.constant_output_btn(MATCH), "n_clicks"),
        State(ids.output_updated(MATCH), "checked"),
        running=[(Output(ids.constant_output_btn(MATCH), "loading"), True, False)],
        prevent_initial_call=True
    )
    def run_singletone(n_clicks, script_isuptodate):
        """
        Runs Artiq script for using Mirny as single constant tone output generator
        :param script_isuptodate:
        :return:
        """
        if not script_isuptodate:
            print("Must update script before running")
            return ""
        else:
            # Get the aio_id from the triggered component
            aio_id = CavityDriveAIO.get_aio_id_from_trigger()
            # Get the device and channel
            device, ch = CavityDriveAIO._devices[aio_id]
            run_artiq_in_clang64_visible(device.freq_gen_path)
            return "Success"

    # RAMP CALLBACKS
    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.end_freq_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_end_frequency(freq):
        """
        Updates Mirny generator frequency in the device object properties.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # print("FREQUENCY CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()

        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"END FREQUENCY UPDATED to {freq} Hz for device {aio_id}, channel {ch}")
        device.set_ramp_ending_freq(freq)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.freq_step_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_frequency_step(freq_step):
        """
        Updates Mirny generator ramp frequency step in the device object properties.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # print("FREQUENCY CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()
        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"FREQUENCY STEP UPDATED to {freq_step} Hz for device {aio_id}, channel {ch}")
        device.set_ramp_step(freq_step)
        return False

    @callback(
        Output(ids.output_updated(MATCH), 'checked', allow_duplicate=True),
        Input(ids.freq_step_delay_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_frequency_step_delay(delay):
        """
        Updates Mirny generator delay between ramp frequency steps.
        Because of specifics of how Sinara works, does not immediately push
        updates into the physical device.
        PRESS "UPDATE" BUTTON TO UPDATE DEVICE OUTPUT.
        """
        # print("FREQUENCY CHANGE CALLBACK WAS STARTED")
        # Get the aio_id from the triggered component
        aio_id = CavityDriveAIO.get_aio_id_from_trigger()
        # Get the device and channel
        device, ch = CavityDriveAIO._devices[aio_id]

        print(f"FREQUENCY STEP DELAY UPDATED to {delay} s for device {aio_id}, channel {ch}")
        device.set_ramp_delay(delay)
        return False

    @callback(
        Output(ids.curr_freq_ctrl(MATCH), "value", allow_duplicate=True),
        Output(ids.end_freq_ctrl(MATCH), "value", allow_duplicate=True),
        Output(ids.output_updated(MATCH), "checked", allow_duplicate=True),
        Input(ids.scan_freq_btn(MATCH), "n_clicks"),
        State(ids.output_updated(MATCH), "checked"),
        running=[(Output(ids.scan_freq_btn(MATCH), "disabled"), True, False)],
        prevent_initial_call=True
    )
    def run_ramp(n_clicks, script_isuptodate):
        if not script_isuptodate:
            print("Must update script before running")
            return  no_update
        else:
            # Get the aio_id from the triggered component
            aio_id = CavityDriveAIO.get_aio_id_from_trigger()
            # Get the device and channel
            device, ch = CavityDriveAIO._devices[aio_id]
            run_artiq_in_clang64_visible(device.freq_ramp_path)
            ramp_starting_freq = device.ramp_params["Starting frequency kHz"]
            ramp_ending_freq = device.ramp_params["Ending frequency kHz"]
            return [ramp_starting_freq, ramp_ending_freq, True]

            # # Swaps the role of starting frequency and ending frequency in case
            # # one wants to immediately scan back
            # return [ramp_ending_freq, ramp_starting_freq, False]


