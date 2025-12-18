from dash import html, Input, Output, State, MATCH, callback, callback_context, no_update
import uuid
import json
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from config import config, update_config  # Import the config
from logger_config import get_logger

logger = get_logger(__name__)

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
        gainControlInput = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'gainControlInput',
            'aio_id': aio_id
        }
        crosshair_checkbox = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_checkbox',
            'aio_id': aio_id
        }
        crosshair_container = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_container',
            'aio_id': aio_id
        }
        crosshair_h_line = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_h_line',
            'aio_id': aio_id
        }
        crosshair_v_line = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_v_line',
            'aio_id': aio_id
        }
        crosshair_h_position = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_h_position',
            'aio_id': aio_id
        }
        crosshair_v_position = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'crosshair_v_position',
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
        bg_path_input = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'bg_path_input',
            'aio_id': aio_id
        }
        bg_subtraction_checkbox = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'bg_subtraction_checkbox',
            'aio_id': aio_id
        }
        load_bg_btn = lambda aio_id: {
            'component': 'CameraInterfaceAIO',
            'subcomponent': 'load_bg_btn',
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

        # Load camera config
        camera_id = str(camera._id) if camera is not None else aio_id
        self.camera_config = config.get(camera_id, {})
        
        # Handle camera properties (exposure and ROI)
        if camera is not None:
            default_exp = camera.get_exposure_ms()
            
            # Load ROI values from config first, then fall back to camera or defaults
            if 'roi' in self.camera_config:
                roi_config = self.camera_config['roi']
                roi_x_tl = roi_config.get('x_tl', 0)
                roi_y_tl = roi_config.get('y_tl', 0)
                roi_x_br = roi_config.get('x_br', camera.sensor_width - 1)
                roi_y_br = roi_config.get('y_br', camera.sensor_height - 1)
            elif hasattr(camera, 'get_ROI') and camera.get_ROI()[0] is not None:
                # Get current ROI values from camera
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

        # Load background and save settings from config
        default_bg_path = self.camera_config.get('background_path', '')
        default_bg_enabled = self.camera_config.get('background_subtraction_enabled', False)
        default_save_folder = self.camera_config.get('save_folder_path', 'C:/Data/Images')
        default_save_name = self.camera_config.get('save_image_name', 'image')
        default_crosshair_enabled = self.camera_config.get('crosshair_enabled', False)
        default_crosshair_h_pos = self.camera_config.get('crosshair_h_position', 50.0)  # Horizontal position as %
        default_crosshair_v_pos = self.camera_config.get('crosshair_v_position', 50.0)  # Vertical position as %
        default_gain = self.camera_config.get('gain', 0.0)
        
        # Initialize camera with saved settings
        if camera is not None:
            # Load background image if path exists
            if default_bg_path:
                success = camera.set_background_path(default_bg_path)
                if success:
                    # Set background subtraction state
                    camera.set_background_subtraction(default_bg_enabled)
        
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

        if 'width' in htmlImg_props:
            interface_width = htmlImg_props['width']
        else:
            interface_width = 400
        if 'height' in htmlImg_props:
            interface_height = htmlImg_props['height']
        else:
            interface_height = 400

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
                dmc.MenuItem("Gain:",
                             rightSection=dmc.NumberInput(value=default_gain, debounce=True,
                                                          suffix=' dB', w=100,
                                                          id=self.ids.gainControlInput(aio_id))),
                dmc.MenuDivider(),
                dmc.MenuLabel("Display Options"),
                dmc.MenuItem(
                    dmc.Checkbox(label="Draw crosshair", checked=default_crosshair_enabled, size="sm",
                                id=self.ids.crosshair_checkbox(aio_id))
                ),
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Text("Horizontal:", size="sm", style={"width": "80px"}),
                        dmc.NumberInput(value=default_crosshair_h_pos, debounce=True,
                                      suffix=' %', w=100, min=0, max=100, step=0.1,
                                      id=self.ids.crosshair_h_position(aio_id))
                    ], gap="xs", align="center")
                ),
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Text("Vertical:", size="sm", style={"width": "80px"}),
                        dmc.NumberInput(value=default_crosshair_v_pos, debounce=True,
                                      suffix=' %', w=100, min=0, max=100, step=0.1,
                                      id=self.ids.crosshair_v_position(aio_id))
                    ], gap="xs", align="center")
                ),
                dmc.MenuDivider(),
                dmc.MenuLabel("Region of Interest (ROI)"),
                # Top-left coordinates row
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Flex([
                            dmc.Text("Top-Left:", size="sm", style={"width": "60px"}),
                            dmc.NumberInput(value=roi_x_tl, debounce=True, placeholder="X",
                                          w=100, min=0,
                                          max=camera.sensor_width-1 if camera else 4095,
                                          persistence=True, persistence_type='local',
                                          id=self.ids.roi_x_tl(aio_id)),
                            dmc.NumberInput(value=roi_y_tl, debounce=True, placeholder="Y",
                                          w=100, min=0,
                                          max=camera.sensor_height-1 if camera else 4095,
                                          persistence=True, persistence_type='local',
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
                                          w=100, min=0,
                                          max=camera.sensor_width-1 if camera else 4095,
                                          persistence=True, persistence_type='local',
                                          id=self.ids.roi_x_br(aio_id)),
                            dmc.NumberInput(value=roi_y_br, debounce=True, placeholder="Y",
                                          w=100, min=0,
                                          max=camera.sensor_height-1 if camera else 4095,
                                          persistence=True, persistence_type='local',
                                          id=self.ids.roi_y_br(aio_id))
                        ], gap="xs", align="center")
                    ], direction="column")
                ),
                dmc.MenuItem(dmc.Button("Set ROI", size="xs", id=self.ids.set_roi_btn(aio_id))),
                dmc.MenuDivider(),
                dmc.MenuLabel("Save Image"),
                dmc.MenuItem("Folder:",
                             rightSection=dmc.TextInput(placeholder="C:/Data/Images", debounce=True,
                                                        w=200, value=default_save_folder,
                                                        id=self.ids.save_folder_path(aio_id))),
                dmc.MenuItem("Name:",
                             rightSection=dmc.TextInput(placeholder="image", debounce=True,
                                                        w=200, value=default_save_name,
                                                        id=self.ids.save_image_name(aio_id))),
                dmc.MenuItem(dmc.Button("Save 16-bit PNG", size="xs", color="green", 
                                       id=self.ids.save_image_btn(aio_id))),
                dmc.MenuDivider(),
                dmc.MenuLabel("Background Subtraction"),
                dmc.MenuItem("Background Path:",
                             rightSection=dmc.TextInput(placeholder="C:/path/to/background.png", debounce=True,
                                                       w=200, value=default_bg_path,
                                                       id=self.ids.bg_path_input(aio_id))),
                dmc.MenuItem(
                    dmc.Flex([
                        dmc.Checkbox(label="Remove background", checked=default_bg_enabled, size="sm",
                                    id=self.ids.bg_subtraction_checkbox(aio_id)),
                        dmc.Button("Load Background", size="xs", color="blue",
                                  id=self.ids.load_bg_btn(aio_id))
                    ], gap="md", align="center", justify="space-between")
                ),
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

        # Create crosshair lines with thin red styling
        crosshair_display = 'block' if default_crosshair_enabled else 'none'

        # Horizontal crosshair line
        h_line = html.Div(
            id=self.ids.crosshair_h_line(aio_id),
            style={
                'position': 'absolute',
                'top': f'{default_crosshair_v_pos}%',
                'left': '0',
                'width': '100%',
                'height': '1px',
                'backgroundColor': 'red',
                'pointerEvents': 'none',
                'display': crosshair_display
            }
        )

        # Vertical crosshair line
        v_line = html.Div(
            id=self.ids.crosshair_v_line(aio_id),
            style={
                'position': 'absolute',
                'left': f'{default_crosshair_h_pos}%',
                'top': '0',
                'width': '1px',
                'height': '100%',
                'backgroundColor': 'red',
                'pointerEvents': 'none',
                'display': crosshair_display
            }
        )

        # Create camera image
        if camera is None:
            logger.warning("Camera not found - using placeholder")
            camera_img = html.Img(src=self._placeholder, id=self.ids.htmlImg(aio_id),
                                  **htmlImg_props)
        else:
            camera_img = html.Img(id=self.ids.htmlImg(aio_id), **htmlImg_props)

        # Wrap image and crosshair in a container with relative positioning
        camera_screen = html.Div(
            id=self.ids.crosshair_container(aio_id),
            children=[camera_img, h_line, v_line],
            style={
                'position': 'relative',
                'width': '100%',
                'height': '100%'
            }
        )

        # Hidden Div to mitigate problems with callbacks without Output
        hidden_div = html.Div([], id=self.ids.hidden_div(aio_id), style={'display': 'none'})
        layout = dmc.Card(
            children=[],
            style={'width': f'{interface_width}px',
                   'height': f'{interface_height}px',
                   'padding': 'xs', 'margin': '10px'}
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
        logger.info('Starting stream callback')
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        # Get the device and channel
        try:
            camera, streamer = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            logger.warning(f'Camera using placeholder: {e}')
            return ''
        logger.info(f'Camera {aio_id} starting stream')
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
            logger.warning(f'Camera using placeholder: {e}')
            return ''
        logger.info(f'Camera {aio_id} starting stream')
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
            logger.warning(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Validate ROI values
        if None in [x_tl, y_tl, x_br, y_br]:
            logger.warning(f'Camera {aio_id}: ROI values cannot be None')
            return ''
        
        # Check bounds against sensor dimensions
        if not (0 <= x_tl < camera.sensor_width and 0 <= x_br < camera.sensor_width):
            logger.warning(f'Camera {aio_id}: X coordinates must be between 0 and {camera.sensor_width-1}')
            return ''
            
        if not (0 <= y_tl < camera.sensor_height and 0 <= y_br < camera.sensor_height):
            logger.warning(f'Camera {aio_id}: Y coordinates must be between 0 and {camera.sensor_height-1}')
            return ''
        
        # Check that top-left is actually top-left of bottom-right
        if x_tl >= x_br:
            logger.warning(f'Camera {aio_id}: Top-left X ({x_tl}) must be less than bottom-right X ({x_br})')
            return ''
            
        if y_tl >= y_br:
            logger.warning(f'Camera {aio_id}: Top-left Y ({y_tl}) must be less than bottom-right Y ({y_br})')
            return ''
        
        # All validation passed, set the ROI
        try:
            camera.set_ROI(x_tl, y_tl, x_br, y_br)
            logger.info(f'Camera {aio_id}: ROI set to ({x_tl}, {y_tl}) - ({x_br}, {y_br})')
            
            # Save ROI values to config
            camera_id = str(camera._id)
            roi_config = {
                camera_id: {
                    'roi': {
                        'x_tl': x_tl,
                        'y_tl': y_tl,
                        'x_br': x_br,
                        'y_br': y_br
                    }
                }
            }
            update_config(roi_config)
            logger.debug(f'Camera {aio_id}: ROI values saved to config')
            
        except Exception as e:
            logger.error(f'Camera {aio_id}: Error setting ROI: {str(e)}')
        
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

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.load_bg_btn(MATCH), 'n_clicks'),
        State(ids.bg_path_input(MATCH), 'value'),
        prevent_initial_call=True
    )
    def load_background(n_clicks, bg_path):
        """Load background image from specified path"""
        if n_clicks is None or not bg_path:
            return no_update
            
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Load the background image
        success = camera.set_background_path(bg_path.strip())
        if success:
            print(f'Camera {aio_id}: Background image loaded successfully')
            
            # Save background path to config
            camera_id = str(camera._id)
            current_config = config.get(camera_id, {})
            current_config['background_path'] = bg_path.strip()
            update_config({camera_id: current_config})
        else:
            print(f'Camera {aio_id}: Failed to load background image')
        
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.bg_subtraction_checkbox(MATCH), 'checked'),
        prevent_initial_call=True
    )
    def toggle_background_subtraction(enable_bg):
        """Enable or disable background subtraction"""
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Set background subtraction state
        camera.set_background_subtraction(enable_bg)
        
        # Save background subtraction state to config
        camera_id = str(camera._id)
        current_config = config.get(camera_id, {})
        current_config['background_subtraction_enabled'] = enable_bg
        update_config({camera_id: current_config})
        
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.bg_path_input(MATCH), 'value'),
        prevent_initial_call=True
    )
    def save_background_path(bg_path):
        """Save background path to config when it changes"""
        if bg_path is None:
            return no_update
            
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Save background path to config
        camera_id = str(camera._id)
        current_config = config.get(camera_id, {})
        current_config['background_path'] = bg_path.strip() if bg_path else ''
        update_config({camera_id: current_config})
        
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.save_folder_path(MATCH), 'value'),
        prevent_initial_call=True
    )
    def save_folder_path(folder_path):
        """Save image folder path to config when it changes"""
        if folder_path is None:
            return no_update
            
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()
        
        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''
        
        # Save folder path to config
        camera_id = str(camera._id)
        current_config = config.get(camera_id, {})
        current_config['save_folder_path'] = folder_path.strip() if folder_path else ''
        update_config({camera_id: current_config})
        
        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.save_image_name(MATCH), 'value'),
        prevent_initial_call=True
    )
    def save_image_name(image_name):
        """Save image name to config when it changes"""
        if image_name is None:
            return no_update

        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()

        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''

        # Save image name to config
        camera_id = str(camera._id)
        current_config = config.get(camera_id, {})
        current_config['save_image_name'] = image_name.strip() if image_name else ''
        update_config({camera_id: current_config})

        return ''

    @callback(
        Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True),
        Input(ids.gainControlInput(MATCH), 'value'),
        prevent_initial_call=True
    )
    def set_gain(gain):
        """Set camera gain - placeholder for future API implementation"""
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()

        # Get the camera
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
        except Exception as e:
            print(f'Camera using placeholder: {str(e)}')
            return ''

        # TODO: Connect to camera API when available
        # camera.set_gain(gain)

        # Save gain value to config
        camera_id = str(camera._id)
        current_config = config.get(camera_id, {})
        current_config['gain'] = gain
        update_config({camera_id: current_config})

        print(f'Camera {aio_id}: gain value saved to config: {gain} (API not connected yet)')
        return ''

    @callback(
        [Output(ids.crosshair_h_line(MATCH), 'style'),
         Output(ids.crosshair_v_line(MATCH), 'style'),
         Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True)],
        Input(ids.crosshair_checkbox(MATCH), 'checked'),
        [State(ids.crosshair_h_line(MATCH), 'style'),
         State(ids.crosshair_v_line(MATCH), 'style')],
        prevent_initial_call=True
    )
    def toggle_crosshair(enable_crosshair, h_style, v_style):
        """Enable or disable crosshair overlay on camera image"""
        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()

        # Update the display property of both crosshair lines
        h_style['display'] = 'block' if enable_crosshair else 'none'
        v_style['display'] = 'block' if enable_crosshair else 'none'

        # Save crosshair state to config
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
            camera_id = str(camera._id)
        except Exception as e:
            # If camera not found, use aio_id as fallback
            camera_id = aio_id

        current_config = config.get(camera_id, {})
        current_config['crosshair_enabled'] = enable_crosshair
        update_config({camera_id: current_config})

        logger.info(f'Camera {aio_id}: crosshair {"enabled" if enable_crosshair else "disabled"}')

        return h_style, v_style, ''

    @callback(
        [Output(ids.crosshair_v_line(MATCH), 'style', allow_duplicate=True),
         Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True)],
        Input(ids.crosshair_h_position(MATCH), 'value'),
        State(ids.crosshair_v_line(MATCH), 'style'),
        prevent_initial_call=True
    )
    def update_crosshair_h_position(h_position, v_style):
        """Update horizontal position of vertical crosshair line"""
        if h_position is None:
            return no_update, no_update

        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()

        # Update the left position of the vertical line
        v_style['left'] = f'{h_position}%'

        # Save horizontal position to config
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
            camera_id = str(camera._id)
        except Exception as e:
            # If camera not found, use aio_id as fallback
            camera_id = aio_id

        current_config = config.get(camera_id, {})
        current_config['crosshair_h_position'] = h_position
        update_config({camera_id: current_config})

        logger.debug(f'Camera {aio_id}: crosshair horizontal position set to {h_position}%')

        return v_style, ''

    @callback(
        [Output(ids.crosshair_h_line(MATCH), 'style', allow_duplicate=True),
         Output(ids.hidden_div(MATCH), 'children', allow_duplicate=True)],
        Input(ids.crosshair_v_position(MATCH), 'value'),
        State(ids.crosshair_h_line(MATCH), 'style'),
        prevent_initial_call=True
    )
    def update_crosshair_v_position(v_position, h_style):
        """Update vertical position of horizontal crosshair line"""
        if v_position is None:
            return no_update, no_update

        # Get the aio_id from the triggered component
        aio_id = CameraInterfaceAIO.get_aio_id_from_trigger()

        # Update the top position of the horizontal line
        h_style['top'] = f'{v_position}%'

        # Save vertical position to config
        try:
            camera, _ = CameraInterfaceAIO._devices[aio_id]
            camera_id = str(camera._id)
        except Exception as e:
            # If camera not found, use aio_id as fallback
            camera_id = aio_id

        current_config = config.get(camera_id, {})
        current_config['crosshair_v_position'] = v_position
        update_config({camera_id: current_config})

        logger.debug(f'Camera {aio_id}: crosshair vertical position set to {v_position}%')

        return h_style, ''
