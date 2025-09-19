import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_mantine_components as dmc
import plotly.graph_objs as go
import json

from components.CameraInterfaceAIO import CameraInterfaceAIO
from devices import pico, mirny_cavity_drive#, xenics_cam, streamer3
from components.PicoscopeInterfaceAIO import PicoscopeInterfaceAIO
from components.CavityDriveAIO import CavityDriveAIO
from dash_extensions import WebSocket

# Register this as a Dash page
dash.register_page(__name__, path='/cavity')


def layout():
    """Layout for the cavity control page"""

    # Create pico and cavity drive interfaces
    pico_interface = PicoscopeInterfaceAIO(aio_id='picoscope_1', name='picoscope_1', device=pico)
    cavity_drive_interface = dmc.Flex([
        CavityDriveAIO(aio_id='cavity_drive', name='Fiber EOM cavity drive', device=mirny_cavity_drive, ch=0)
    ])
    # backplane_camera_interface = CameraInterfaceAIO(aio_id='webcam_3', camera=xenics_cam, streamer=streamer3, name='Backplane detection',
    #                                htmlImg_props={'width': '390px', 'height': '390px'})
    return dmc.MantineProvider([
        dmc.Flex([
            cavity_drive_interface,
            pico_interface,
            # backplane_camera_interface,
            # WebSocket(url=f"ws://127.0.0.1:5000/stream3", id="ws3"),
        ], direction='row', wrap='wrap')
    ])