import dash
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, callback_context
import dash_mantine_components as dmc
import plotly.graph_objs as go
from dash_extensions import WebSocket
import json

from devices import daq_streamer, daq_card, daq_update_rate
from config import config  # Import the config

# Register this as a Dash page
dash.register_page(__name__, path='/monitors')


def layout():
    """Layout for the DAQ monitoring page - DAQ control and plots only"""

    # Create a list of available channels for the selectors
    channel_options = [
        {'value': ch, 'label': ch.split('/')[-1]}
        for ch in daq_card.channels
    ]

    # Horizontal control section
    control_section = dmc.Group([
        dmc.Button("Start Monitoring", id="start-daq-btn", color="green"),
        dmc.Button("Stop", id="stop-daq-btn", color="red"),
        dmc.NumberInput(
            id="update-rate-input",
            label="Update Rate (Hz)",
            value=daq_update_rate,
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
        # Status display
        html.Div(id="status-display", style={"marginLeft": "20px"}),
    ], mb="md")

    # Load plot configurations from config file
    plot_configs = config.get('plots', [])
    
    # Make sure we have 4 plots defined
    while len(plot_configs) < 4:
        plot_configs.append({})
    
    # Plots with settings dropdowns
    graphs = []
    for i in range(4):
        # Get configuration for this plot with defaults if not provided
        plot_config = plot_configs[i] if i < len(plot_configs) else {}
        title = plot_config.get('title', f"Plot {i + 1}")
        channels = plot_config.get('channels', [daq_card.channels[i]] if i < len(daq_card.channels) else [])
        legend_strings = plot_config.get('legend_strings', [])
        y_scale_mode = plot_config.get('y_scale_mode', 'auto')
        y_min = plot_config.get('y_min', -10)
        y_max = plot_config.get('y_max', 10)
        display_samples = plot_config.get('display_samples', '1000')
        plot_width = plot_config.get('width', 600)
        plot_height = plot_config.get('height', 300)
        
        graph_card = dmc.Card([
            dmc.CardSection([
                dmc.Group([
                    dmc.Text(title, fw=500, size="lg", style={"width": "60%"}),
                    dmc.Menu([
                        dmc.MenuTarget(
                            dmc.Button("Settings", variant="outline", size="xs",
                                       id={"type": "settings-btn", "index": i})
                        ),
                        dmc.MenuDropdown([
                            dmc.Text("Channel Selection", fw="bold"),
                            dmc.MultiSelect(
                                id={"type": "channel-selector", "index": i},
                                data=channel_options,
                                value=channels,
                                style={"width": "100%", "marginBottom": "10px"}
                            ),
                            dmc.Divider(style={"margin": "10px 0"}),
                            dmc.Text("Legend Strings", fw="bold"),
                            dmc.Textarea(
                                id={"type": "legend-strings", "index": i},
                                placeholder="Enter legend strings separated by commas",
                                value=", ".join(legend_strings) if legend_strings else "",
                                style={"width": "100%", "marginBottom": "10px"}
                            ),
                            dmc.Divider(style={"margin": "10px 0"}),
                            dmc.Text("Y-Axis Scale", fw="bold"),
                            dmc.Group([
                                dmc.RadioGroup(
                                    id={"type": "y-scale-mode", "index": i},
                                    value=y_scale_mode,
                                    children=[
                                        dmc.Radio(value="auto", label="Auto"),
                                        dmc.Radio(value="manual", label="Manual")
                                    ],
                                ),
                            ]),
                            dmc.Flex([
                                dmc.NumberInput(
                                    id={"type": "y-min", "index": i},
                                    label="Min",
                                    value=y_min,
                                    style={"width": "45%"},
                                    allowDecimal=True,
                                    step=0.1,
                                    disabled=y_scale_mode != "manual"
                                ),
                                dmc.NumberInput(
                                    id={"type": "y-max", "index": i},
                                    label="Max",
                                    value=y_max,
                                    style={"width": "45%"},
                                    allowDecimal=True,
                                    step=0.1,
                                    disabled=y_scale_mode != "manual"
                                ),
                            ], direction='row', justify='space-between', style={"marginBottom": "10px"}),
                        ]),
                    ]),
                ], style={"justifyContent": "space-between"})
            ], withBorder=True, inheritPadding=True, py='xs'),
            dmc.CardSection([
                dcc.Graph(
                    id={'type': 'signal-graph', 'index': i},
                    figure={
                        'data': [go.Scatter(x=[], y=[], mode='lines')],
                        'layout': go.Layout(
                            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                            xaxis={'title': 'Samples'},
                            yaxis={'title': 'Voltage (V)'},
                            height=plot_height,
                            width=plot_width
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], mt='sm')
        ], withBorder=True, style={"margin": "1px"})
        graphs.append(graph_card)

    # WebSocket for data streaming
    websocket = WebSocket(url="ws://127.0.0.1:5000/daq_stream", id="ws-daq")

    # Hidden div for triggering plot updates when data is received
    hidden_div = html.Div([
        html.Div(id="hidden-daq-data", style={"display": "none"}),
        # Store the full plot configuration to ensure correct data structure
        dcc.Store(
            id="plot-config-store",
            data={"plots": plot_configs}
        )
    ])

    # Main layout - simplified for DAQ only
    return dmc.MantineProvider([
        dmc.Container([
            dmc.Title("DAQ Monitor", order=1, mb="md"),
            
            # Controls
            control_section,
            
            # Plots in a simple grid - 2x2 layout
            dmc.SimpleGrid(
                cols=2,
                children=graphs,
                spacing="md"
            ),
            
            # WebSocket and hidden trigger
            websocket,
            hidden_div,
            
        ], size="xl")
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
        daq_streamer._update_rate = update_rate or daq_update_rate
        success = daq_streamer.start()
        if success:
            return dmc.Alert("Streaming started", color="green")
        else:
            return dmc.Alert("Failed to start streaming", color="red")
    
    elif trigger_id == "stop-daq-btn" and stop_clicks:
        daq_streamer.stop()
        return dmc.Alert("Streaming stopped", color="orange")
    
    elif trigger_id == "update-rate-input":
        daq_streamer._update_rate = update_rate or daq_update_rate
        return dmc.Alert(f"Update rate set to {update_rate}Hz", color="blue")
    
    return ""

# Enable/disable manual Y-axis scale inputs for each plot
@callback(
    [Output({"type": "y-min", "index": MATCH}, "disabled", allow_duplicate=True),
     Output({"type": "y-max", "index": MATCH}, "disabled", allow_duplicate=True)],
    Input({"type": "y-scale-mode", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def toggle_y_scale_inputs(scale_mode):
    """Enable or disable Y-axis min/max inputs based on scale mode"""
    return scale_mode != "manual", scale_mode != "manual"