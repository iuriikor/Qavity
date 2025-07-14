from dash import html, callback, Input, Output, State, MATCH, ALL, callback_context
import uuid
import json
import dash_core_components as dcc
import dash_mantine_components as dmc
from config import config  # Import the config

from controllers.picoscope.ps5000a_wrapper import PicoInterface


# All-in-One Components should be suffixed with 'AIO'
class PicoscopeInterfaceAIO(html.Div):  # html.Div will be the "parent" component

    class ids:
        config_storage = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'config_storage',
            'aio_id': aio_id
        }
        pico_openclose = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'pico_openclose',
            'aio_id': aio_id
        }
        # Pattern-matching IDs for channels
        channel_onoff = lambda aio_id, channel: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'channel_onoff',
            'channel': channel,
            'aio_id': aio_id
        }
        channel_range = lambda aio_id, channel: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'channel_range',
            'channel': channel,
            'aio_id': aio_id
        }
        # Other controls
        resolution = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'resolution',
            'aio_id': aio_id
        }
        sampling_frequency_set = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'sampling_frequency_set',
            'aio_id': aio_id
        }
        sampling_frequency_actual = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'sampling_frequency_actual',
            'aio_id': aio_id
        }
        acq_time_set = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'acq_time_set',
            'aio_id': aio_id
        }
        acq_time_actual = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'acq_time_actual',
            'aio_id': aio_id
        }
        start_stream_btn = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'start_stream_btn',
            'aio_id': aio_id
        }
        arm_trigger_btn = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'arm_trigger_btn',
            'aio_id': aio_id
        }
        chunks_input = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'chunks_input',
            'aio_id': aio_id
        }
        data_path = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'data_path',
            'aio_id': aio_id
        }
        measurement_name = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'measurement_name',
            'aio_id': aio_id
        }
        data_comments = lambda aio_id: {
            'component': 'PicoscopeInterfaceAIO',
            'subcomponent': 'data_comments',
            'aio_id': aio_id
        }

    # Class level storage for device instances
    # Maps aio_id to device
    _devices = {}

    # Define the arguments of the All-in-One component
    def __init__(
            self,
            aio_id=None,
            name=None,
            device=None,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        self.name = name
        self._device = device
        self.aio_id = aio_id  # Store for creating channel controls

        # Store device in class-level storage
        PicoscopeInterfaceAIO._devices[aio_id] = device

        # Load config file
        if self._device:
            self.pico_config = config.get(self._device.get_name(), {})
        else:
            self.pico_config = {}

        # Parse defaults
        self.default_sampling_rate = self.pico_config.get('sampling_frequency', '1')
        self.default_acqusition_time = self.pico_config.get('acqusition_time', '1')
        self.default_resolution = self.pico_config.get('resolution', '12')
        self.default_data_path = self.pico_config.get('data_path', 'C:/')
        self.default_msmt_name = self.pico_config.get('measurement_set_name', 'none')
        self.default_channel_props = self.pico_config.get('channels', {})

        # Channel configuration
        self.channels = ['A', 'B', 'C', 'D']
        self.channel_colors = {'A': 'blue', 'B': 'red', 'C': 'teal', 'D': 'yellow'}
        self.channel_names = {'A': 'Channel 1', 'B': 'Channel 2', 'C': 'Channel 3', 'D': 'Channel 4'}

        # Define the component's layout
        layout = dmc.Card([])

        # Picoscope open/close
        pico_openclose = dmc.Flex([
            dmc.Chip('Open', variant="filled", size="lg", checked=False,
                     id=self.ids.pico_openclose(aio_id))
        ], direction='row', justify='space-between')

        # Top bar
        top_bar = dmc.CardSection(
            dmc.Flex([dmc.Text(self._device.get_name(), size='xl'), pico_openclose],
                     justify='space-between'),
            withBorder=True, py="xs", inheritPadding=True
        )

        # Config storage
        config_store = dcc.Store(
            id=self.ids.config_storage(aio_id),
            data={self._device.get_name(): self.pico_config},
        )

        # Data saving section
        data_path = dmc.Flex(
            children=[
                dmc.TextInput(
                    value=self.default_data_path,
                    label='Data path:',
                    id=self.ids.data_path(aio_id),
                    debounce=True,
                    w=400
                ),
                dmc.TextInput(
                    value=self.default_msmt_name,
                    label='Measurement name:',
                    id=self.ids.measurement_name(aio_id),
                    debounce=True
                ),
            ],
            direction='column'
        )

        # Sampling parameters
        sampling_params = dmc.Flex(
            children=[
                dmc.Flex(children=[
                    dmc.NumberInput(
                        value=float(self.default_sampling_rate),
                        label='Sampling frequency:',
                        suffix='MHz',
                        allowDecimal=True, decimalScale=1, min=0.1, max=20, step=0.1,
                        debounce=True, hideControls=True, w=150,
                        id=self.ids.sampling_frequency_set(aio_id)
                    ),
                    dmc.NumberInput(
                        suffix='MHz', allowDecimal=True, decimalScale=10,
                        hideControls=True, disabled=True, w=150, radius='sm',
                        id=self.ids.sampling_frequency_actual(aio_id)
                    ),
                ], direction='row', align='flex-end', justify='space-between'),

                dmc.Flex(children=[
                    dmc.NumberInput(
                        value=float(self.default_acqusition_time),
                        label='Sampling time:',
                        suffix='s',
                        allowDecimal=True, decimalScale=2, min=0.1, max=20, step=0.01,
                        debounce=True, hideControls=True, w=150,
                        id=self.ids.acq_time_set(aio_id)
                    ),
                    dmc.NumberInput(
                        suffix='s', allowDecimal=True, decimalScale=2,
                        hideControls=True, disabled=True, w=150, radius='sm',
                        id=self.ids.acq_time_actual(aio_id)
                    ),
                ], direction='row', align='flex-end', justify='space-between'),

                dmc.Flex(children=[
                    dmc.Select(
                        label='Bit resolution:',
                        value=int(self.default_resolution),
                        data=[
                            {"value": "8", "label": "8 bit"},
                            {"value": "12", "label": "12 bit"},
                            {"value": "14", "label": "14 bit"},
                            {"value": "16", "label": "16 bit"},
                        ],
                        checkIconPosition="right",
                        id=self.ids.resolution(aio_id)
                    )
                ])
            ],
            direction='column'
        )

        # Create channel controls dynamically
        channel_params = self._create_channel_controls()

        # Create field to include comment into the metadata
        comment_field = dmc.Textarea(
            placeholder="Additional comments",
            label="Additional comments",
            size="md",
            w=400,
            debounce=True,
            id=self.ids.data_comments(aio_id)
        )

        # Start/stop controls
        controls = dmc.Flex([
            dmc.Button('Stream', id=self.ids.start_stream_btn(aio_id)),
            dmc.Text('OR', size='lg', fw='500'),
            dmc.NumberInput(
                label='Chunks:', hideControls=True, w=50, debounce=True,
                value=1, min=1, max=1000, id=self.ids.chunks_input(aio_id)
            ),
            dmc.Button('Arm trigger', id=self.ids.arm_trigger_btn(aio_id))
        ], direction='row', align='flex-end', justify='space-between')

        layout.children = [
            config_store, top_bar, data_path, sampling_params,
            channel_params, dmc.Divider(mt='sm', mb='sm'), comment_field,
            dmc.Divider(mt='sm', mb='sm'), controls
        ]

        super().__init__(layout)

    def _create_channel_controls(self):
        """Create channel controls dynamically using loops"""
        voltage_range = ["0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20"]

        channel_controls = []

        for channel in self.channels:
            # Get default values for this channel
            channel_enabled = self.default_channel_props.get(channel, {}).get("enabled", "False") == "True"
            channel_range = self.default_channel_props.get(channel, {}).get("range", "5")

            channel_control = dmc.Flex(
                children=[
                    dmc.Chip(
                        self.channel_names[channel],
                        variant="filled",
                        color=self.channel_colors[channel],
                        size="lg",
                        radius="xs",
                        checked=channel_enabled,
                        id=self.ids.channel_onoff(self.aio_id, channel)
                    ),
                    dmc.Flex([
                        dmc.Text("Range (V): ", size='lg', fw=500, mr='sm'),
                        dmc.Select(
                            data=voltage_range,
                            value=channel_range,
                            w=100,
                            id=self.ids.channel_range(self.aio_id, channel)
                        )
                    ], justify='flex-end'),
                ],
                direction='row', mt='sm', align='center', justify='space-between'
            )
            channel_controls.append(channel_control)

        return dmc.Flex(children=channel_controls, direction='column')

    @staticmethod
    def get_aio_id_from_trigger():
        """Extract aio_id from the component that triggered the callback"""
        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        id_dict = json.loads(triggered_id)
        return id_dict['aio_id']

    @staticmethod
    def get_channel_from_trigger():
        """Extract channel from the component that triggered the callback"""
        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        id_dict = json.loads(triggered_id)
        return id_dict.get('channel')

    # Open/Close connection callback
    @callback(
        [Output(ids.pico_openclose(MATCH), 'checked', allow_duplicate=True),
         Output(ids.sampling_frequency_actual(MATCH), 'value', allow_duplicate=True),
         Output(ids.acq_time_actual(MATCH), 'value', allow_duplicate=True)],
        Input(ids.pico_openclose(MATCH), 'checked'),
        [State(ids.config_storage(MATCH), 'data'),
         State(ids.resolution(MATCH), 'value'),
         State(ids.sampling_frequency_set(MATCH), 'value'),
         State(ids.acq_time_set(MATCH), 'value'),
         State({'component': 'PicoscopeInterfaceAIO', 'subcomponent': 'channel_onoff', 'channel': ALL, 'aio_id': MATCH},
               'checked'),
         State({'component': 'PicoscopeInterfaceAIO', 'subcomponent': 'channel_range', 'channel': ALL, 'aio_id': MATCH},
               'value')],
        prevent_initial_call=True
    )
    def toggle_connection(is_checked, current_config, resolution, freq_mhz, acq_time, channel_states, range_values):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        if is_checked:
            # Open the device first
            success = device.open()
            print(f"Opening PicoScope connection: {'Success' if success else 'Failed'}")

            if success:
                # Apply all configuration from AIO interface
                print("Applying AIO configuration to device...")

                # 1. Set resolution
                if resolution is not None:
                    device.set_resolution(int(resolution))
                    print(f"Applied resolution: {resolution} bits")

                # 2. Configure channels
                channels = ['A', 'B', 'C', 'D']
                for i, channel in enumerate(channels):
                    enabled = channel_states[i] if i < len(channel_states) and channel_states[i] is not None else False
                    voltage_range = float(range_values[i]) if i < len(range_values) and range_values[
                        i] is not None else 5.0

                    device.set_channel(
                        channel=channel,
                        enabled=enabled,
                        voltage_range=voltage_range
                    )
                    print(f"Applied Channel {channel}: {'enabled' if enabled else 'disabled'}, range: {voltage_range}V")

                # 3. Set sampling frequency and time and get actual value
                actual_freq_mhz = freq_mhz
                if freq_mhz is not None:
                    freq_hz = freq_mhz * 1e6
                    sampling_period = 1/freq_hz
                    actual_sampling_period, num_samples = device.set_sampling_period(sampling_period, acq_time)
                    actual_freq_mhz = 1/actual_sampling_period/1e06 if actual_sampling_period > 0 else freq_mhz
                    print(f"Applied sampling frequency: {freq_mhz} MHz, actual: {actual_freq_mhz} MHz")

                print("Device configuration complete!")
                return success, actual_freq_mhz, acq_time
            else:
                return False, freq_mhz, acq_time

        else:
            success = device.close()
            print(f"Closing PicoScope connection: {'Success' if success else 'Failed'}")
            return not success, freq_mhz, acq_time

    # Single callback for ALL channel on/off states
    @callback(
        Output(ids.config_storage(MATCH), 'data', allow_duplicate=True),
        Input({'component': 'PicoscopeInterfaceAIO', 'subcomponent': 'channel_onoff', 'channel': ALL, 'aio_id': MATCH},
              'checked'),
        State(ids.config_storage(MATCH), 'data'),
        prevent_initial_call=True
    )
    def channels_on_off(channel_states, current_config):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        channels = ['A', 'B', 'C', 'D']  # Order should match the ALL pattern

        for i, state in enumerate(channel_states):
            if state is not None and i < len(channels):
                channel = channels[i]
                current_range = device.channel_ranges.get(channel, 5)
                device.set_channel(channel, enabled=state, voltage_range=current_range)
                print(f"Channel {channel} {'enabled' if state else 'disabled'}")

                # Update the config data if needed
                if current_config and device.get_name() in current_config:
                    device_config = current_config[device.get_name()]
                    if 'channels' in device_config:
                        if channel in device_config['channels']:
                            device_config['channels'][channel]['enabled'] = str(state)

        return current_config

    # Single callback for ALL channel ranges
    @callback(
        Output(ids.config_storage(MATCH), 'data', allow_duplicate=True),
        Input({'component': 'PicoscopeInterfaceAIO', 'subcomponent': 'channel_range', 'channel': ALL, 'aio_id': MATCH},
              'value'),
        State(ids.config_storage(MATCH), 'data'),
        prevent_initial_call=True
    )
    def update_channel_ranges(range_values, current_config):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        channels = ['A', 'B', 'C', 'D']  # Order should match the ALL pattern

        for i, voltage_range in enumerate(range_values):
            if voltage_range is not None and i < len(channels):
                channel = channels[i]
                # Only update if channel is enabled
                if device.channels_enabled.get(channel, False):
                    device.set_channel(channel, enabled=True, voltage_range=float(voltage_range))
                    print(f"Channel {channel} range set to {voltage_range}V")

                    # Update the config data if needed
                    if current_config and device.get_name() in current_config:
                        device_config = current_config[device.get_name()]
                        if 'channels' in device_config:
                            if channel in device_config['channels']:
                                device_config['channels'][channel]['range'] = str(voltage_range)

        return current_config

    # Resolution callback
    @callback(
        Output(ids.config_storage(MATCH), 'data', allow_duplicate=True),
        Input(ids.resolution(MATCH), 'value'),
        State(ids.config_storage(MATCH), 'data'),
        prevent_initial_call=True
    )
    def update_resolution(resolution, current_config):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        if resolution is not None:
            success = device.set_resolution(int(resolution))
            print(f"Resolution set to {resolution} bits: {'Success' if success else 'Failed'}")

            # Update the config data if needed
            if success and current_config and device.get_name() in current_config:
                current_config[device.get_name()]['resolution'] = str(resolution)

        return current_config

    # Sampling frequency callback
    @callback(
        Output(ids.sampling_frequency_actual(MATCH), 'value', allow_duplicate=True),
        Input(ids.sampling_frequency_set(MATCH), 'value'),
        State(ids.acq_time_set(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_sampling_frequency(freq_mhz, acq_time_s):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        if freq_mhz is not None:
            freq_hz = freq_mhz * 1e6
            # actual_freq = device.set_sampling_frequency(freq_hz, acq_time_s)
            # actual_freq_mhz = actual_freq / 1e6 if actual_freq > 0 else freq_mhz
            # print(f"Sampling frequency set to {freq_mhz} MHz, actual: {actual_freq_mhz} MHz")
            # return actual_freq_mhz
            actual_sampling_rate, num_samples = device.set_sampling_period(1/freq_hz, acq_time_s)
            actual_freq_mhz = 1/actual_sampling_rate / 1e06
            print(f"Sampling frequency set to {freq_mhz} MHz, actual: {actual_freq_mhz} MHz")
            return actual_freq_mhz

        return freq_mhz

    # Acquisition time callback
    @callback(
        Output(ids.acq_time_actual(MATCH), 'value', allow_duplicate=True),
        Input(ids.acq_time_set(MATCH), 'value'),
        State(ids.sampling_frequency_set(MATCH), 'value'),
        prevent_initial_call=True
    )
    def update_acquisition_time(acq_time, freq_MHz):
        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]

        if acq_time is not None:
            freq_hz = freq_MHz * 1e6
            actual_sampling_rate, num_samples = device.set_sampling_period(1 / freq_hz, acq_time)
            actual_acq_time = num_samples*actual_sampling_rate
            return actual_acq_time
        return acq_time

    # Start streaming callback
    @callback(
        Output(ids.start_stream_btn(MATCH), 'children', allow_duplicate=True),
        [Input(ids.start_stream_btn(MATCH), 'n_clicks')],
        [State(ids.data_path(MATCH), 'value'),
         State(ids.measurement_name(MATCH), 'value'),
         State(ids.data_comments(MATCH),'value')],
        prevent_initial_call=True
    )
    def start_streaming(n_clicks, data_path, measurement_name, comments):
        if n_clicks is None:
            return 'Stream'

        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]
        metadata={}
        metadata['comments'] = comments

        print(f"Starting streaming acquisition...")
        result = device.run_streaming(
            data_dir=data_path,
            filename=measurement_name,
            auto_stop=True,
            additional_metadata=metadata
        )

        if result is not None or (data_path and measurement_name):
            print("Streaming completed successfully")
            return 'Stream Complete'
        else:
            print("Streaming failed")
            return 'Stream Failed'

    # Arm trigger callback
    @callback(
        Output(ids.arm_trigger_btn(MATCH), 'children', allow_duplicate=True),
        [Input(ids.arm_trigger_btn(MATCH), 'n_clicks')],
        [State(ids.data_path(MATCH), 'value'),
         State(ids.measurement_name(MATCH), 'value'),
         State(ids.chunks_input(MATCH), 'value'),
         State(ids.data_comments(MATCH),'value')],
        prevent_initial_call=True
    )
    def arm_trigger(n_clicks, data_path, measurement_name, num_chunks, comments):
        if n_clicks is None:
            return 'Arm trigger'

        aio_id = PicoscopeInterfaceAIO.get_aio_id_from_trigger()
        device = PicoscopeInterfaceAIO._devices[aio_id]
        metadata = {}
        metadata['comments'] = comments

        if num_chunks is None or num_chunks < 1:
            num_chunks = 1

        print(f"Arming trigger for {num_chunks} block acquisitions...")
        device.set_trigger(channel='A', threshold=1.0, direction='Rising',
                           delay=0, auto_trigger=False, timeout_ms=1000)
        success = device.run_multi_block_acquisition(
            data_dir=data_path,
            measurement_set_name=measurement_name,
            num_chunks=num_chunks,
            pre_trigger_percent=0,
            additional_metadata=metadata
        )

        if success:
            return f'{num_chunks} Triggers Complete'
        else:
            return 'Multi-Trigger Failed'