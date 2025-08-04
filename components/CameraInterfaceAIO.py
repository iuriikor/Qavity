from dash import html, Input, Output, State, MATCH, callback, callback_context, no_update
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
        roi_x_tl = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'roi_x_tl',
            'aio_id': aio_id
        }
        roi_y_tl = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'roi_y_tl',
            'aio_id': aio_id
        }
        roi_x_br = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'roi_x_br',
            'aio_id': aio_id
        }
        roi_y_br = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'roi_y_br',
            'aio_id': aio_id
        }
        set_roi_btn = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'set_roi_btn',
            'aio_id': aio_id
        }
        save_folder_path = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'save_folder_path',
            'aio_id': aio_id
        }
        save_image_name = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'save_image_name',
            'aio_id': aio_id
        }
        save_image_btn = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'save_image_btn',
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
        name = None,
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

        # Handle camera properties (exposure and ROI)
        if camera is not None:
            default_exp = camera.get_exposure_ms()
            # Get current ROI values or use full sensor as default
            if hasattr(camera, 'get_ROI') and camera.get_ROI()[0] is not None:
                roi_x_tl, roi_y_tl, roi_x_br, roi_y_br = camera.get_ROI()
            else:
                # Default to full sensor
                roi_x_tl, roi_y_tl = 0, 0
                roi_x_br, roi_y_br = camera.sensor_width - 1, camera.sensor_height - 1
        else:
            # Placeholder values when no camera
            default_exp = 1.0
            roi_x_tl, roi_y_tl = 0, 0
            roi_x_br, roi_y_br = 1279, 1023  # Common camera resolution as default
        
        # Merge user-supplied properties into default properties
        # Set fixed dimensions and stretch the image to fill the container
        default_img_style = {
            'padding': '5px 0px 0px 0px',
            'margin-top': 'xs',
            'object-fit': 'fill'  # This makes the image stretch to fill the container
        }
        htmlImg_props = htmlImg_props.copy() if htmlImg_props else {} # copy the dict so as to not mutate the user's dict
        if 'style' in htmlImg_props:
            htmlImg_props['style'].update(default_img_style)
        else:
            htmlImg_props['style'] = default_img_style

        # Define the component's layout
        # cam_name = dmc.CardSection([dmc.Text(name, size='xl')],
        #                     withBorder=True, py="xs", inheritPadding=True)
        dropdown = dmc.Menu(
    [
        dmc.MenuTarget(dmc.ActionIcon(DashIconify(icon="material-symbols:settings"), size="input-sm")),
        dmc.MenuDropdown(
            [
                dmc.MenuLabel("Camera Settings"),
                dmc.MenuItem("Exposure:",
                             rightSection=dmc.NumberInput(value=default_exp, debounce=True,
                                                          suffix=' ms', w=100,
                                                          id=self.ids.exposureControlInput(aio_id))),
                dmc.MenuDivider(),
                dmc.MenuLabel("Region of Interest (ROI)"),
                # Top-left coordinates row
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Flex([
                            dmc.Text("Top-Left:", size="sm", style={"width": "60px"}),
                            dmc.NumberInput(value=roi_x_tl, debounce=True, placeholder="X",
                                          w=60, min=0, 
                                          max=camera.sensor_width-1 if camera else 4095,
                                          id=self.ids.roi_x_tl(aio_id)),
                            dmc.NumberInput(value=roi_y_tl, debounce=True, placeholder="Y",
                                          w=60, min=0, 
                                          max=camera.sensor_height-1 if camera else 4095,
                                          id=self.ids.roi_y_tl(aio_id))
                        ], gap="xs", align="center")
                    ], direction="column")
                ),
                # Bottom-right coordinates row  
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Flex([
                            dmc.Text("Bot-Right:", size="sm", style={"width": "60px"}),
                            dmc.NumberInput(value=roi_x_br, debounce=True, placeholder="X",
                                          w=60, min=0, 
                                          max=camera.sensor_width-1 if camera else 4095,
                                          id=self.ids.roi_x_br(aio_id)),
                            dmc.NumberInput(value=roi_y_br, debounce=True, placeholder="Y",
                                          w=60, min=0, 
                                          max=camera.sensor_height-1 if camera else 4095,
                                          id=self.ids.roi_y_br(aio_id))
                        ], gap="xs", align="center")
                    ], direction="column")
                ),
                dmc.MenuItem(dmc.Button("Set ROI", size="xs", id=self.ids.set_roi_btn(aio_id))),
                dmc.MenuDivider(),
                dmc.MenuLabel("Save Image"),
                dmc.MenuItem("Folder:",
                             rightSection=dmc.TextInput(placeholder="C:/Data/Images", debounce=True,
                                                       w=200, id=self.ids.save_folder_path(aio_id))),
                dmc.MenuItem("Name:",
                             rightSection=dmc.TextInput(placeholder="image", debounce=True,
                                                       w=200, id=self.ids.save_image_name(aio_id))),
                dmc.MenuItem(dmc.Button("Save 16-bit PNG", size="xs", color="green", 
                                       id=self.ids.save_image_btn(aio_id))),
            ]),
    ],closeOnItemClick=False, closeOnClickOutside=True)
        menu = dmc.CardSection([
            dmc.Text(name, size='xl'),
            dmc.Flex(
            [
                dmc.ButtonGroup(
                    [
                        dmc.Button('Start', color='blue', id=self.ids.start_stream_btn(aio_id), n_clicks=0),
                        dmc.Button('Stop', color='red', id=self.ids.stop_stream_btn(aio_id), n_clicks=0)
                    ]),
                dmc.Flex(dropdown),
            ], align='center', justify='space-between')
        ], withBorder=True, py="xs", inheritPadding=True)

        if camera is None:
            print("CAMERA NOT FOUND - USING PLACEHOLDER")
            camera_screen = html.Img(src=self._placeholder, id=self.ids.htmlImg(aio_id), 
                                     **htmlImg_props)
        else:
            camera_screen = html.Img(id=self.ids.htmlImg(aio_id), **htmlImg_props)
        # Hidden Div to mitigate problems with callbacks without Output
        hidden_div = html.Div([], id=self.ids.hidden_div(aio_id), style={'display': 'none'})
        layout = dmc.Card(
            children=[],
            style={'width': '400px', 'padding': 'xs', 'margin': '10px'}
        )
        layout.children = [menu, camera_screen, hidden_div]
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
        # streamer.stream()
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
        camera.set_exposure_ms(exposure)
        print(f'Camera {aio_id}: exposure set to {exposure}')
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.set_roi_btn(MATCH), 'n_clicks'),
        [State(ids.roi_x_tl(MATCH), 'value'),
         State(ids.roi_y_tl(MATCH), 'value'),
         State(ids.roi_x_br(MATCH), 'value'),
         State(ids.roi_y_br(MATCH), 'value')],
        prevent_initial_call=True
    )
    def set_roi(n_clicks, x_tl, y_tl, x_br, y_br):
        """Set camera ROI with validation"""
        if n_clicks is None:
            return no_update
            
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Validate ROI values
        if None in [x_tl, y_tl, x_br, y_br]:
            print(f'Camera {aio_id}: ROI values cannot be None')
            return ''
        
        # Check bounds against sensor dimensions
        if not (0 <= x_tl < camera.sensor_width and 0 <= x_br < camera.sensor_width):
            print(f'Camera {aio_id}: X coordinates must be between 0 and {camera.sensor_width-1}')
            return ''
            
        if not (0 <= y_tl < camera.sensor_height and 0 <= y_br < camera.sensor_height):
            print(f'Camera {aio_id}: Y coordinates must be between 0 and {camera.sensor_height-1}')
            return ''
        
        # Check that top-left is actually top-left of bottom-right
        if x_tl >= x_br:
            print(f'Camera {aio_id}: Top-left X ({x_tl}) must be less than bottom-right X ({x_br})')
            return ''
            
        if y_tl >= y_br:
            print(f'Camera {aio_id}: Top-left Y ({y_tl}) must be less than bottom-right Y ({y_br})')
            return ''
        
        # All validation passed, set the ROI
        try:
            camera.set_ROI(x_tl, y_tl, x_br, y_br)
            print(f'Camera {aio_id}: ROI set to ({x_tl}, {y_tl}) - ({x_br}, {y_br})')
        except Exception as e:
            print(f'Camera {aio_id}: Error setting ROI: {str(e)}')
        
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.save_image_btn(MATCH), 'n_clicks'),
        [State(ids.save_folder_path(MATCH), 'value'),
         State(ids.save_image_name(MATCH), 'value')],
        prevent_initial_call=True
    )
    def save_image(n_clicks, folder_path, image_name):
        """Save current camera frame as PNG with timestamp prefix"""
        if n_clicks is None:
            return no_update
            
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Validate inputs
        if not folder_path or not folder_path.strip():
            print(f'Camera {aio_id}: Folder path cannot be empty')
            return ''
            
        if not image_name or not image_name.strip():
            print(f'Camera {aio_id}: Image name cannot be empty')
            return ''
        
        # Clean the inputs
        folder_path = folder_path.strip()
        image_name = image_name.strip()
        
        # Save the image using the ThorCam method (always 16-bit)
        try:
            saved_path = camera.save_image(folder_path, image_name)
            if saved_path:
                print(f'Camera {aio_id}: Successfully saved 16-bit image to {saved_path}')
            else:
                print(f'Camera {aio_id}: Failed to save image')
        except Exception as e:
            print(f'Camera {aio_id}: Error during image save: {str(e)}')
        
        return ''
