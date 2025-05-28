from dash import html, callback, Input, Output, State, MATCH, callback_context
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
        if aio_id is None: # This should normally never be invoked, but I'll leave it here just in case
            aio_id = str(uuid.uuid4())
        self.name = name
        self._device = device
        # Store device in class-level storage
        # This is a CLASS variable, not an OBJECT variable, meaning that ALL objects of the same
        # class will share the same variable. This is why we need a way to distinguish between
        # devices that belong to different AIO components by the AIO id.
        PicoscopeInterfaceAIO._devices[aio_id] = device

        # Load config file
        if self._device:
            self.pico_config = config.get(self._device.get_name(), {})
        else:
            self.pico_config = {}
        # Parse
        self.default_sampling_rate = self.pico_config.get('sampling_frequency', '1')
        self.default_acqusition_time = self.pico_config.get('acqusition_time', '1')
        self.default_resolution = self.pico_config.get('resolution', '12')
        self.default_data_path = self.pico_config.get('data_path', 'C:/')
        self.default_msmt_name = self.pico_config.get('measurement_set_name', 'none')
        self.default_channel_props = self.pico_config.get('channels', {})

        # Define the component's layout
        layout = dmc.Card([])

        # Picoscope open/close
        pico_openclose = dmc.Flex([
            dmc.Chip('Open', variant="filled",
                     size="lg",
                     # mb='sm',
                     checked=False,
                     id='pico_openclose')
        ], direction='row', justify='space-between')

        # Top bar
        top_bar = dmc.CardSection(dmc.Flex([dmc.Text(self._device.get_name(), size='xl'), pico_openclose],
                                           justify='space-between'),
                                withBorder=True, py="xs", inheritPadding=True)
        # Add storage of picoscope configuration
        config_store = dcc.Store(
            id=self.ids.config_storage(aio_id),
            data={self._device.get_name(): self.pico_config},
        )
        # Saving data
        data_path = dmc.Flex(
            children = [
                dmc.TextInput(value=self.default_data_path,
                              label='Data path:',
                              id='data_path',
                              debounce=True,
                              w=400),
                dmc.TextInput(value=self.default_msmt_name,
                              label='Measurement name:',
                              id='measurement_name',
                              debounce=True),
            ], direction='column', style={}
        )
        # Setting picoscope sampling parameters
        sampling_params = dmc.Flex(
            children =[
                dmc.Flex(children=[
                    dmc.NumberInput(value=float(self.default_sampling_rate), label='Sampling frequency:', suffix='MHz',
                                    allowDecimal=True, decimalScale=1, min=0.1, max=20, step=0.1,
                                    debounce=True, hideControls=True, w=150, id='sampling_frequency_set'),
                    dmc.NumberInput(suffix='MHz', allowDecimal=True, decimalScale=10, hideControls=True,
                                    disabled=True, w=150, radius='sm', id='sampling_frequency_actual'),
                    ], direction='row', align='flex-end', justify='space-between'),
                dmc.Flex(children=[
                    dmc.NumberInput(value=float(self.default_acqusition_time), label='Sampling time:', suffix='s',
                                    allowDecimal=True, decimalScale=2, min=0.1, max=20, step=0.01,
                                    debounce=True, hideControls=True, w=150, id='acq_time_set'),
                    dmc.NumberInput(suffix='s', allowDecimal=True, decimalScale=2, hideControls=True,
                                    disabled=True, w=150, radius='sm', id='acq_time_actual'),
                ], direction='row', align='flex-end', justify='space-between'),
                dmc.Flex(children=[
                    dmc.Select(label='Bit resolution:',
                               value=int(self.default_resolution),
                               data=[
                                   {"value": "8", "label": "8 bit"},
                                   {"value": "12", "label": "12 bit"},
                                   {"value": "14", "label": "14 bit"},
                                   {"value": "16", "label": "16 bit"},
                               ], checkIconPosition="right",
                               id='resolution')
                ])
            ], direction='column'
        )

        voltage_range = ["0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20"]
        chA = dmc.Flex(children=[
                    dmc.Chip('Channel 1',
                             variant="filled",
                             color="blue",
                             size="lg",
                             radius="xs",
                             checked=(self.default_channel_props["A"]["enabled"]=="True"),
                             id='chA_onoff'),
                    dmc.Flex([dmc.Text("Range (V): ", size='lg', fw=500, mr='sm'),
                              dmc.Select(
                                data=voltage_range,
                                value=self.default_channel_props["A"]["range"],
                                w=100,
                                id="chA_range"
                    )], justify='flex-end'),
                ], direction='row', mt='sm', align='center', justify='space-between')
        chB = dmc.Flex(children=[
            dmc.Chip('Channel 2',
                     variant="filled",
                     color="red",
                     size="lg",
                     radius="xs",
                     checked=(self.default_channel_props["B"]["enabled"] == "True"),
                     id='chB_onoff'),
            dmc.Flex([dmc.Text("Range (V): ", size='lg', fw=500, mr='sm'),
                      dmc.Select(
                          data=voltage_range,
                          value=self.default_channel_props["B"]["range"],
                          w=100,
                          id="chB_range"
                      )], justify='flex-end'),
        ], direction='row', mt='sm', align='flex-end', justify='space-between')
        chC = dmc.Flex(children=[
            dmc.Chip('Channel 3',
                     variant="filled",
                     color="teal",
                     size="lg",
                     radius="xs",
                     checked=(self.default_channel_props["C"]["enabled"] == "True"),
                     id='chC_onoff'),
            dmc.Flex([dmc.Text("Range (V): ", size='lg', fw=500, mr='sm'),
                      dmc.Select(
                          data=voltage_range,
                          value=self.default_channel_props["C"]["range"],
                          w=100,
                          id="chC_range"
                      )], justify='flex-end'),
        ], direction='row', mt='sm', align='flex-end', justify='space-between')
        chD = dmc.Flex(children=[
            dmc.Chip('Channel 4',
                     variant="filled",
                     color="yellow",
                     size="lg",
                     radius="xs",
                     checked=(self.default_channel_props["D"]["enabled"] == "True"),
                     id='chD_onoff'),
            dmc.Flex([dmc.Text("Range (V): ", size='lg', fw=500, mr='sm'),
                      dmc.Select(
                          data=voltage_range,
                          value=self.default_channel_props["D"]["range"],
                          w=100,
                          id="chD_range"
                      )], justify='flex-end'),
        ], direction='row', mt='sm', align='flex-end', justify='space-between')
        # Channel parameters
        channel_params = dmc.Flex(
            children=[
                chA, chB, chC, chD
            ], direction='column')
        # Start/stop controls
        controls = dmc.Flex([
            dmc.Button('Stream', id='start_stream_btn'),
            dmc.Text('OR', size='lg', fw='500'),
            dmc.NumberInput(label='Chunks: ', hideControls=True, w=150, debounce=True),
            dmc.Button('Arm trigger', id='arm_triger_btn')
        ], direction='row', align='flex-end', justify='space-between')

        layout.children = [config_store, top_bar, data_path, sampling_params, channel_params, dmc.Divider(mt='sm', mb='sm'), controls]

        super().__init__(layout)

    @staticmethod
    def get_aio_id_from_trigger():
        """Extract aio_id from the component that triggered the callback"""
        # Get the ID of the component that triggered the callback
        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        # The ID is a JSON string that we need to parse
        id_dict = json.loads(triggered_id)
        return id_dict['aio_id']
