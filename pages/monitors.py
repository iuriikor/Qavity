import dash
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, callback_context
import dash_mantine_components as dmc
import plotly.graph_objs as go
from dash_extensions import WebSocket
import json

from devices import daq_streamer, daq_card

# Register this as a Dash page
dash.register_page(__name__, path='/monitors')


def layout():
    """Layout for the DAQ monitoring page"""

    # Create a list of available channels for the selectors
    channel_options = [
        {'value': ch, 'label': ch.split('/')[-1]}
        for ch in daq_card.channels
    ]

    # Control panel
    control_card = dmc.Card([
        dmc.CardSection([
            dmc.Text("DAQ Control", size="xl")
        ], withBorder=True, py='xs', inheritPadding=True),

        dmc.Flex([
            dmc.Button("Start Monitoring", id="start-daq-btn", color="green"),
            dmc.Button("Stop", id="stop-daq-btn", color="red"),
            dmc.NumberInput(
                id="sample-rate-input",
                label="Sample Rate (Hz)",
                value=50,
                min=1,
                max=1000,
                step=1,
                style={"width": 150}
            ),
            dmc.Select(
                id="buffer-size-select",
                label="Buffer Size",
                data=[
                    {'value': '100', 'label': '100 samples'},
                    {'value': '500', 'label': '500 samples'},
                    {'value': '1000', 'label': '1000 samples'},
                    {'value': '2000', 'label': '2000 samples'}
                ],
                value='1000',
                style={"width": 150}
            )
        ], gap="md", direction='column', mt='sm')
    ], withBorder=True, p="md", style={"margin": "10px"})

    # Create 4 plot cards
    graphs = []
    for i in range(4):
        # Settings for this plot
        graph_card = dmc.Card([
            dmc.CardSection([
                dmc.Group([
                    dmc.TextInput(
                        id={"type": "plot-title", "index": i},
                        value=f"Signal Monitor {i + 1}",
                        style={"width": "50%", "fontWeight": 500}
                    ),
                    dmc.Menu([
                        dmc.MenuTarget(
                            dmc.Button("Settings", variant="outline", size="xs",
                                       id={"type": "settings-btn", "index": i})
                        ),
                        dmc.MenuDropdown([
                            dmc.Text("Channel Selection", style={"fontWeight": "bold"}),
                            dmc.MultiSelect(
                                id={"type": "channel-selector", "index": i},
                                data=channel_options,
                                value=[daq_card.channels[i]] if i < len(daq_card.channels) else [daq_card.channels[0]],
                                style={"width": "100%", "marginBottom": "10px"}
                            ),
                            dmc.Divider(style={"margin": "10px 0"}),
                            dmc.Text("Y-Axis Scale", style={"fontWeight": "bold"}),
                            dmc.Group([
                                dmc.RadioGroup(
                                    id={"type": "y-scale-mode", "index": i},
                                    value="auto",
                                    children=[
                                        dmc.Radio(value="auto", label="Auto"),
                                        dmc.Radio(value="manual", label="Manual")
                                    ],
                                ),
                            ]),
                            dmc.Group([
                                dmc.NumberInput(
                                    id={"type": "y-min", "index": i},
                                    label="Min",
                                    value=-10,
                                    style={"width": "45%"},
                                    allowDecimal=True,
                                    decimalScale=1,
                                    step=0.1,
                                    disabled=True
                                ),
                                dmc.NumberInput(
                                    id={"type": "y-max", "index": i},
                                    label="Max",
                                    value=10,
                                    style={"width": "45%"},
                                    allowDecimal=True,
                                    decimalScale=1,
                                    step=0.1,
                                    disabled=True
                                ),
                            ], grow=True, style={"marginBottom": "10px"}),
                            dmc.Divider(style={"margin": "10px 0"}),
                            dmc.Text("Samples to Display", style={"fontWeight": "bold"}),
                            dmc.Select(
                                id={"type": "display-samples", "index": i},
                                data=[
                                    {'value': '100', 'label': '100 samples'},
                                    {'value': '500', 'label': '500 samples'},
                                    {'value': '1000', 'label': '1000 samples'},
                                    {'value': '2000', 'label': '2000 samples'},
                                    {'value': '10000', 'label': '10000 samples'},
                                    {'value': '20000', 'label': '20000 samples'},
                                ],
                                value='1000',
                                style={"width": "100%", "marginBottom": "10px"}
                            ),
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
                            height=300,
                            width=800
                        )
                    },
                    config={
                        'displayModeBar': False,
                        'staticPlot': True  # Disable all interactivity including hover
                    }
                )
            ], mt='sm')
        ], withBorder=True, style={"margin": "10px"})
        graphs.append(graph_card)

    # WebSocket for data streaming
    websocket = WebSocket(url="ws://127.0.0.1:5000/daq_stream", id="ws-daq")

    # Hidden div for storing data received from websocket
    hidden_div = html.Div([
    html.Div(id="hidden-daq-data", style={"display": "none"}),
    dcc.Store(id="plot-titles", data={f"plot-{i}": f"Signal Monitor {i+1}" for i in range(4)})
])

    return dmc.MantineProvider(
        dmc.Flex([
        dmc.Flex([control_card], direction="column", align="center", style={"width": "10%"}),
        dmc.Flex([
            dmc.Flex([graphs[0], graphs[1]], gap="md", style={"width": "100%"}),
            dmc.Flex([graphs[2], graphs[3]], gap="md", style={"width": "100%"}),
        ], direction="column", gap="md"),
        websocket,
        hidden_div
    ], direction="row")
    )


# Server-side callbacks
@callback(
    Output("ws-daq", "url", allow_duplicate=True),
    Input("start-daq-btn", "n_clicks"),
    Input("sample-rate-input", "value"),
    prevent_initial_call=True
)
def start_daq_streaming(n_clicks, sample_rate):
    """Start DAQ streaming with the specified sample rate"""
    if n_clicks is None:
        return dash.no_update

    # Update sample rate and start streaming
    daq_streamer._sampling_rate = sample_rate
    daq_streamer.start()

    # Force WebSocket reconnection with a timestamp
    import time
    return f"ws://127.0.0.1:5000/daq_stream?t={int(time.time())}"


@callback(
    Output("ws-daq", "url", allow_duplicate=True),
    Input("stop-daq-btn", "n_clicks"),
    prevent_initial_call=True
)
def stop_daq_streaming(n_clicks):
    """Stop DAQ streaming"""
    if n_clicks:
        daq_streamer.stop()
        # Return a dummy URL to cause the websocket to disconnect
        import time
        return f"ws://127.0.0.1:5000/daq_stream?stopped={int(time.time())}"


# Enable/disable manual Y-axis scale inputs
@callback(
    [Output({"type": "y-min", "index": MATCH}, "disabled"),
     Output({"type": "y-max", "index": MATCH}, "disabled")],
    Input({"type": "y-scale-mode", "index": MATCH}, "value")
)
def toggle_y_scale_inputs(scale_mode):
    """Enable or disable Y-axis min/max inputs based on scale mode"""
    return scale_mode != "manual", scale_mode != "manual"


@callback(
    Output("plot-titles", "data"),
    [Input({"type": "plot-title", "index": ALL}, "value")],
    State("plot-titles", "data")
)
def update_plot_titles(titles, current_titles):
    """Store custom plot titles"""
    # Get the triggered input
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    # Get the index of the title that changed
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    title_info = json.loads(trigger_id)
    index = title_info['index']

    # Update just that title
    current_titles[f"plot-{index}"] = titles[index]

    return current_titles