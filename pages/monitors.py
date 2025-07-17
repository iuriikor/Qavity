import dash
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, callback_context
import dash_mantine_components as dmc
import plotly.graph_objs as go
from dash_extensions import WebSocket
import json

from devices import daq_streamer, daq_card, pico, mirny_cavity_drive
from components.PicoscopeInterfaceAIO import PicoscopeInterfaceAIO
from components.CavityDriveAIO import CavityDriveAIO
from config import config  # Import the config

# Register this as a Dash page
dash.register_page(__name__, path='/monitors')


def layout():
    """Layout for the DAQ monitoring page - simplified version"""

    # Control section - using full layout style
    control_section = dmc.Flex([
        dmc.Text("DAQ Control", size="xl"),
        dmc.Flex([
            dmc.Button("Start Monitoring", id="start-daq-btn", color="green"),
            dmc.Button("Stop", id="stop-daq-btn", color="red"),
            dmc.NumberInput(
                id="update-rate-input",
                label="Update Rate (Hz)",
                value=10,
                min=1,
                max=100,
                step=1,
                style={"width": 150}
            ),
            dmc.Select(
                id="display-samples-select",
                label="Display Samples",
                data=[
                    {'value': '100', 'label': '100 samples'},
                    {'value': '500', 'label': '500 samples'},
                    {'value': '1000', 'label': '1000 samples'},
                    {'value': '2000', 'label': '2000 samples'},
                ],
                value='1000',
                style={"width": 150}
            ),
            # Y-axis controls integrated into control section
            dmc.Text("Y-Axis Scale", fw="bold"),
            dmc.RadioGroup(
                id="y-scale-mode",
                value="auto",
                children=[
                    dmc.Radio(value="auto", label="Auto"),
                    dmc.Radio(value="manual", label="Manual")
                ],
            ),
            dmc.NumberInput(
                id="y-min",
                label="Min",
                value=-10,
                style={"width": 100},
                step=0.1,
                disabled=True
            ),
            dmc.NumberInput(
                id="y-max",
                label="Max",
                value=10,
                style={"width": 100},
                step=0.1,
                disabled=True
            ),
            # Status display
            html.Div(id="status-display", style={"marginBottom": "10px"}),
        ], gap="md", direction='column', justify='flex-start', align='center')
    ], justify='flex-start', align='center', direction='column', mr='xs')
    
    # Control panel
    DAQ_card = dmc.Card([], withBorder=True, p="sm", mr='sm', mb='sm')

    # Simple plots for DAQ channels - similar to debug example
    graphs = []
    for i in range(min(4, len(daq_card.channels))):
        graph_card = dmc.Card([
            dmc.Text(f"Channel: {daq_card.channels[i]}", fw=500, mb="sm"),
            dcc.Graph(
                id=f"graph-{i}",
                figure={
                    'data': [go.Scatter(x=[], y=[], mode='lines')],
                    'layout': go.Layout(
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        xaxis={'title': 'Samples'},
                        yaxis={'title': 'Voltage (V)'},
                        height=300
                    )
                },
                config={'displayModeBar': False}
            )
        ], withBorder=True, p="sm")
        graphs.append(graph_card)

    # WebSocket for data streaming
    websocket = WebSocket(url="ws://127.0.0.1:5000/daq_stream", id="ws-daq")

    # Hidden div for triggering plot updates when data is received
    hidden_div = html.Div(id="hidden-daq-data", style={"display": "none"})

    # Configure DAQ card layout - using full layout structure with simplified plots
    DAQ_card.children = dmc.Flex([
        control_section,
        dmc.Flex([graphs[0], graphs[2]], gap="xs", style={"width": "100%"}, mt='sm', direction='column'),
        dmc.Flex([graphs[1], graphs[3]], gap="xs", style={"width": "100%"}, mt='sm', direction='column'),
    ], direction='row')
    
    # Create pico and cavity drive interfaces - from full layout
    pico_interface = PicoscopeInterfaceAIO(aio_id='picoscope_1', name='picoscope_1', device=pico)
    cavity_drive_interface = dmc.Flex([
        CavityDriveAIO(aio_id='cavity_drive', name='Fiber EOM cavity drive', device=mirny_cavity_drive, ch=0)
    ])

    # Main layout - using full layout structure
    return dmc.MantineProvider([
        dmc.Flex([
            dmc.Flex([DAQ_card, cavity_drive_interface], direction='column'),
            pico_interface,
            websocket,
            hidden_div
        ], direction="row", wrap='wrap'),
    ])


# Server-side callbacks - simplified like debug example
@callback(
    Output("status-display", "children"),
    Input("start-daq-btn", "n_clicks"),
    Input("stop-daq-btn", "n_clicks"),
    Input("update-rate-input", "value"),
    prevent_initial_call=True
)
def control_streaming(start_clicks, stop_clicks, update_rate):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "start-daq-btn" and start_clicks:
        daq_streamer._update_rate = update_rate or 10
        success = daq_streamer.start()
        if success:
            return dmc.Alert("Streaming started", color="green")
        else:
            return dmc.Alert("Failed to start streaming", color="red")
    
    elif trigger_id == "stop-daq-btn" and stop_clicks:
        daq_streamer.stop()
        return dmc.Alert("Streaming stopped", color="orange")
    
    elif trigger_id == "update-rate-input":
        daq_streamer._update_rate = update_rate or 10
        return dmc.Alert(f"Update rate set to {update_rate}Hz", color="blue")
    
    return ""

# Enable/disable manual Y-axis scale inputs
@callback(
    [Output("y-min", "disabled"),
     Output("y-max", "disabled")],
    Input("y-scale-mode", "value")
)
def toggle_y_scale_inputs(scale_mode):
    """Enable or disable Y-axis min/max inputs based on scale mode"""
    return scale_mode != "manual", scale_mode != "manual"