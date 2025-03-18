from dash import html, Input, Output, MATCH, callback, callback_context
import uuid
import json
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# All-in-One Components should be suffixed with 'AIO'
class CameraInterfaceAIO(html.Div):  # html.Div will be the "parent" component

    # A set of functions that create pattern-matching callbacks of the subcomponents
    class ids:
        dropdown = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'dropdownMenu',
            'aio_id': aio_id
        }
        htmlImg = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'htmlImg',
            'aio_id': aio_id
        }
        exposureControlInput = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'exposureControlInput',
            'aio_id': aio_id
        }
        start_stream_btn = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'start_stream_btn',
            'aio_id': aio_id
        }
        stop_stream_btn = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'stop_stream_btn',
            'aio_id': aio_id
        }
        hidden_div = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'hidden_div',
            'aio_id': aio_id
        }

    # Make the ids class a public class
    ids = ids

    # Class level storage for device instances
    # Maps aio_id to (camera, streamer) pairs
    _devices = {}

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        htmlImg_props=None,
        aio_id=None,
        camera=None,
        streamer = None,
        placeholder=None
    ):
        # If aio_id is not provided, use a generated id
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        if camera is not None:
            if streamer is not None:
                CameraInterfaceAIO._devices[aio_id] = (camera, streamer)
            else:
                raise Exception('Camera AND streamer must be specified')
        if placeholder is not None:
            self._placeholder = placeholder

        # Merge user-supplied properties into default properties
        htmlImg_props = htmlImg_props.copy() if htmlImg_props else {} # copy the dict so as to not mutate the user's dict

        # Define the component's layout
        dropdown = dmc.Menu(
    [
        dmc.MenuTarget(dmc.ActionIcon(DashIconify(icon="material-symbols:settings"), size="input-sm")),
        dmc.MenuDropdown(
            [
                dmc.MenuLabel("Camera Settings"),
                dmc.MenuItem("Exposure:",
                             rightSection=dmc.NumberInput(value=5, debounce=True,
                                                          suffix=' ms', w=100,
                                                          id=self.ids.exposureControlInput(aio_id))),
            ]),
    ],closeOnItemClick=False, closeOnClickOutside=True)
        menu = dmc.Flex(
            [
                dmc.ButtonGroup(
                    [
                        dmc.Button('Start', color='blue', id=self.ids.start_stream_btn(aio_id), n_clicks=0),
                        dmc.Button('Stop', color='red', id=self.ids.stop_stream_btn(aio_id), n_clicks=0)
                    ]),
                dmc.Flex(dropdown),
            ], align='center', justify='space-between')

        if camera is None:
            print("CAMERA NOT FOUND - USING PLACEHOLDER")
            camera_screen = html.Img(src=self._placeholder, id=self.ids.htmlImg(aio_id),
                                     style={'max-width': '100%', 'padding': '5px 0px 0px 0px'})
        else:
            camera_screen = html.Img(id=self.ids.htmlImg(aio_id), style={'max-width': '100%'})
        # Hidden Div to mitigate problems with callbacks without Output
        hidden_div = html.Div([], id=self.ids.hidden_div(aio_id), style={'display': 'none'})
        #%% LAYOUT DEFINITION
        layout = dmc.Flex([],
                          direction='column',
                          style={'width': '400px', 'padding': '10px',
                                'border': 'solid', 'border-radius': '20px',
                                'margin': '20px'}
                          )
        layout.children = [hidden_div, menu, camera_screen]
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
        Input(ids.start_stream_btn(MATCH), 'n_clicks'),
        prevent_initial_call=True
    )
    def start_stream(n_clicks):
        print('STARTING STREAM CALLBACK')
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        # Get the device and channel
        try:
            camera, streamer = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {e}')
            return ''
        print(f'Camera {aio_id} starting stream')
        camera.start_stream()
        streamer.stream()
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.stop_stream_btn(MATCH), 'n_clicks'),
        prevent_initial_call=True
    )
    def stop_stream(n_clicks):
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        # Get the device and channel
        try:
            camera, streamer = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {e}')
            return ''
        print(f'Camera {aio_id} starting stream')
        camera.stop_stream()
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.exposureControlInput(MATCH), 'value'),
        prevent_initial_call=True
    )
    def set_exposure_ms(exposure):
        """Set camera exposure in milliseconds"""
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        # Get the device and channel
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        camera.set_exposure(exposure)
        print(f'Camera {aio_id}: exposure set to {exposure}')
        return ''
