from dash import html
import uuid
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

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        htmlImg_props=None,
        aio_id=None,
        camera=None,
        placeholder=None
    ):
        if camera is not None:
            self._camera = camera
        if placeholder is not None:
            self._placeholder = placeholder
        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern.
            aio_id = str(uuid.uuid4())

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

        if placeholder is None:
            camera_screen = html.Img(id=self.ids.htmlImg(aio_id), style={'max-width': '100%'})
        else:
            print("CAMERA NOT FOUND - USING PLACEHOLDER")
            camera_screen = html.Img(src=self._placeholder, id=self.ids.htmlImg(aio_id),
                                     style={'max-width': '100%', 'padding':'5px 0px 0px 0px'})

        super().__init__(
            [
                dmc.Flex(style={'width': '400px', 'padding': '10px',
                                'border': 'solid', 'border-radius': '20px',
                                'margin': '20px'},
                         children=
                [
                    menu,
                    camera_screen
                ], direction="column")
            ]
        )

