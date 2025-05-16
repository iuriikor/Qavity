from dash import html, callback, Input, Output, State, MATCH, callback_context
import uuid
import json
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_daq as daq

# All-in-One Components should be suffixed with 'AIO'
class RelayBoardAIO(html.Div):  # html.Div will be the "parent" component

    class ids:
        pumping_time_ctrl = lambda aio_id: {
            'component': 'RelayBoardAIO',
            'subcomponent': 'pump_time_ctrl',
            'aio_id': aio_id
        }
        load_time_ctrl = lambda aio_id: {
            'component': 'RelayBoardAIO',
            'subcomponent': 'load_time_ctrl',
            'aio_id': aio_id
        }
        pump_btn = lambda aio_id: {
            'component': 'RelayBoardAIO',
            'subcomponent': 'pump_btn',
            'aio_id': aio_id
        }
        spray_btn = lambda aio_id: {
            'component': 'RelayBoardAIO',
            'subcomponent': 'spray_btn',
            'aio_id': aio_id
        }
        loading_cycle_btn = lambda aio_id: {
            'component': 'RelayBoardAIO',
            'subcomponent': 'loading_cycle_btn',
            'aio_id': aio_id
        }
        # Hidden component for update callback
        hidden_div = lambda aio_id: {
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
            device=None,
    ):

        if aio_id is None: # This should normally never be invoked, but I'll leave it here just in case
            aio_id = str(uuid.uuid4())
        RelayBoardAIO._devices[aio_id] = device
        init_pump_port_state = RelayBoardAIO._devices[aio_id].get_port_state("Pump")
        init_load_port_state = RelayBoardAIO._devices[aio_id].get_port_state("Load")

        # Define the component's layout
        layout = dmc.Card(
            children=[],
            withBorder = True,
            padding = 'xs',
            style={'margin': '10px'}
        )
        # Add hidden status div for update callback
        hidden_div = html.Div(id=self.ids.hidden_div(aio_id), style={'display': 'none'})
        title_section = dmc.CardSection([dmc.Text('Relay control', size='xl')],
                            withBorder=True, py="xs", inheritPadding=True)
        relay_status_row = dmc.Flex(
            [
                dmc.Chip("Pump", checked=init_pump_port_state, id=self.ids.pump_btn(aio_id)),
                dmc.Chip("Load", checked=init_load_port_state, id=self.ids.spray_btn(aio_id)),
            ], align='center', justify='space-between', mt='sm')

        loading_settings_row = dmc.Flex([
            dmc.NumberInput(
                label="Pumping time, s",
                placeholder="Pumping time, s",
                suffix="s",
                value=1.0,
                decimalScale=2,
                id = self.ids.pumping_time_ctrl(aio_id)
            ),
            dmc.NumberInput(
                label="Spraying time, s",
                placeholder="Spraying time, s",
                suffix="s",
                value=1.0,
                decimalScale=2,
                id = self.ids.load_time_ctrl(aio_id)
            ),
        ], direction='column')
        control_row = dmc.Flex([
            # dmc.Button("Pump", id=self.ids.pump_btn(aio_id)),
            # dmc.Button("Spray", id=self.ids.spray_btn(aio_id)),
            dmc.Button("Loading cycle", id=self.ids.loading_cycle_btn(aio_id)),
        ], justify='center', mt='sm')
        layout.children = [title_section, relay_status_row, loading_settings_row, control_row, hidden_div]
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
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.pump_btn(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def pump(btn_checked):
        # Get the aio_id from the triggered component
        aio_id = RelayBoardAIO.get_aio_id_from_trigger()
        # Get the device instance
        device= RelayBoardAIO._devices[aio_id]
        try:
            if btn_checked:
                print(f"Pumping down")
                device.close_port(port_name="Load")
                # Double check that the spraying port is now closed
                spray_isopen = device.get_port_state("Load")
                if not spray_isopen:
                    device.open_port(port_name="Pump")
                return ""
            else:
                print("Closing pumping port")
                device.close_port(port_name="Pump")
        except Exception as e:
            print(f"Failed to change pumping state: {str(e)}")
            return ""

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.spray_btn(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def spray(btn_checked):
        # Get the aio_id from the triggered component
        aio_id = RelayBoardAIO.get_aio_id_from_trigger()
        # Get the device instance
        device = RelayBoardAIO._devices[aio_id]
        try:
            if btn_checked: # If the new state of the button is active, ie we want to start spraying
                print(f"Loading particles")
                # Get state of pumping port
                pump_isopen = device.get_port_state("Pump")
                if pump_isopen is not None: # Check if the state is valid
                    if pump_isopen: # If pump is open - close pump
                        device.close_port(port_name="Pump")
                # DOUBLE CHECK
                pump_isopen = device.get_port_state("Pump")
                # Only spray if pump is closed
                if not pump_isopen:
                    device.open_port(port_name="Load") # Spray
                return ""
            else:
                print("Closing spray port")
                device.close_port(port_name="Load")  # Stop spraying
                return ""
        except Exception as e:
            print(f"Failed to start pumping: {str(e)}")
            return ""

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.loading_cycle_btn(MATCH), 'n_clicks'),
        State(ids.pumping_time_ctrl(MATCH), 'value'),
        State(ids.load_time_ctrl(MATCH), 'value'),
        prevent_initial_call=True
    )
    def loading_cycle(n_clicks, pumping_time, loading_time):
        # Get the aio_id from the triggered component
        aio_id = RelayBoardAIO.get_aio_id_from_trigger()
        # Get the device instance
        device = RelayBoardAIO._devices[aio_id]
        try:
            print(f"Pumping down")
            device.pump_for_nseconds(pumping_time)
            print(f"Loading particles")
            device.load_for_nseconds(loading_time)
            return ""
        except Exception as e:
            print(f"Failed to start pumping: {str(e)}")
        return ""
