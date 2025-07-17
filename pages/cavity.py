import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_mantine_components as dmc
import plotly.graph_objs as go
import json

from devices import pico, mirny_cavity_drive
from components.PicoscopeInterfaceAIO import PicoscopeInterfaceAIO
from components.CavityDriveAIO import CavityDriveAIO

# Register this as a Dash page
dash.register_page(__name__, path='/cavity')


def layout():
    """Layout for the cavity control page"""

    # Create pico and cavity drive interfaces
    pico_interface = PicoscopeInterfaceAIO(aio_id='picoscope_1', name='picoscope_1', device=pico)
    cavity_drive_interface = dmc.Flex([
        CavityDriveAIO(aio_id='cavity_drive', name='Fiber EOM cavity drive', device=mirny_cavity_drive, ch=0)
    ])

    # Main layout for cavity control page
    return dmc.MantineProvider([
        dmc.Container([
            dmc.Title("Cavity Control", order=1, mb="md"),
            
            # Cavity drive interface
            dmc.Card([
                dmc.CardSection([
                    dmc.Title("Cavity Drive Control", order=3, mb="sm"),
                    cavity_drive_interface
                ], withBorder=True, inheritPadding=True, py='md')
            ], withBorder=True, mb="md"),
            
            # Picoscope interface
            dmc.Card([
                dmc.CardSection([
                    dmc.Title("Picoscope Control", order=3, mb="sm"),
                    pico_interface
                ], withBorder=True, inheritPadding=True, py='md')
            ], withBorder=True, mb="md"),
            
        ], size="xl")
    ])