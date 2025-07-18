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
# dash.register_page(__name__, path='/monitors')


def layout():
    """Layout for the DAQ monitoring page"""

    # Create a list of available channels for the selectors
    channel_options = [
        {'value': ch, 'label': ch.split('/')[-1]}
        for ch in daq_card.channels
    ]

    # Get global config
    global_config = config.get('global', {})

    control_section = dmc.Flex([
                dmc.Text("DAQ Control", size="xl"),
                dmc.Flex([
                    dmc.Button("Start Monitoring", id="start-daq-btn"),
                    dmc.Button("Stop", id="stop-daq-btn", color="red"),
                    dmc.NumberInput(
                        id="sample-rate-input",
                        label="Sample Rate (Hz)",
                        value=global_config.get('sample_rate', 50),
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
                        value=global_config.get('buffer_size', '1000'),
                        style={"width": 150}
                    ),
                    # Add a Save Configuration button
                    dmc.Button("Save Configuration", id="save-config-btn", color="blue"),
                    html.Div(id="save-config-status"),
                ], gap="md", direction='column', justify='flex-start', align='center')
            ], justify='flex-start', align='center', direction='column', mr='xs')
    # Control panel
    DAQ_card = dmc.Card([], withBorder=True, p="sm", mr='sm', mb='sm')

    # Create 4 plot cards based on config
    graphs = []
    plot_configs = config.get('plots', [])

    # Make sure we have 4 plots defined
    while len(plot_configs) < 4:
        plot_configs.append({})

    for i, plot_config in enumerate(plot_configs[:4]):  # Limit to 4 plots
        # Get configuration for this plot with defaults if not provided
        title = plot_config.get('title', f"Signal Monitor {i + 1}")
        channels = plot_config.get('channels', [daq_card.channels[i]] if i < len(daq_card.channels) else [])
        legend_strings = plot_config.get('legend_strings', [])
        y_scale_mode = plot_config.get('y_scale_mode', 'auto')
        y_min = plot_config.get('y_min', -10)
        y_max = plot_config.get('y_max', 10)
        display_samples = plot_config.get('display_samples', '1000')
        plot_width = plot_config.get('width', 600)
        plot_height = plot_config.get('height', 200)

        # Settings for this plot
        graph_card = dmc.Card([
            dmc.CardSection([
                dmc.Group([
                    # Fixed title display with correct props
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
                                    allowDecimal=True,  # This property is valid
                                    decimalScale=1,  # Use precision instead of decimalScale
                                    step=0.1,
                                    disabled=y_scale_mode != "manual"
                                ),
                                dmc.NumberInput(
                                    id={"type": "y-max", "index": i},
                                    label="Max",
                                    value=y_max,
                                    style={"width": "45%"},
                                    allowDecimal=True,  # This property is valid
                                    decimalScale=1,  # Use precision instead of decimalScale
                                    step=0.1,
                                    disabled=y_scale_mode != "manual"
                                ),
                            ], direction='column', justify='space-between', style={"marginBottom": "10px"}),
                            dmc.Divider(style={"margin": "10px 0"}),
                            dmc.Text("Samples to Display", fw="bold"),
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
                                value=display_samples,
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
                            height=plot_height,
                            width=plot_width
                        )
                    },
                    config={
                        'displayModeBar': False,
                        'staticPlot': True  # Disable all interactivity including hover
                    }
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

    DAQ_card.children = dmc.Flex([
        control_section,
        dmc.Flex([graphs[0], graphs[2]], gap="xs", style={"width": "100%"}, mt='sm', direction='column'),
        dmc.Flex([graphs[1], graphs[3]], gap="xs", style={"width": "100%"}, mt='sm', direction='column'),
    ], direction='row')
    pico_interface = PicoscopeInterfaceAIO(aio_id='picoscope_1', name='picoscope_1', device=pico)
    cavity_drive_interface = dmc.Flex([
        CavityDriveAIO(aio_id='cavity_drive', name='Fiber EOM cavity drive', device=mirny_cavity_drive, ch=0)
        ])

    return dmc.MantineProvider([
        dmc.Flex([
            # dmc.Flex([
            #     control_card,
            #     dmc.Flex([graphs[0], graphs[1]], gap="xs", style={"width": "100%"}),
            #     dmc.Flex([graphs[2], graphs[3]], gap="xs", style={"width": "100%"}),
            # ], direction="column", gap="sm"),
            dmc.Flex([DAQ_card, cavity_drive_interface], direction='column'),
            pico_interface,
            websocket,
            hidden_div
        ], direction="row", wrap='wrap'),
    ])


# Server-side callbacks - COMMENTED OUT since this page is not active
# @callback(
#     Output("ws-daq", "url", allow_duplicate=True),
#     Input("start-daq-btn", "n_clicks"),
#     Input("sample-rate-input", "value"),
#     prevent_initial_call=True
# )
# def start_daq_streaming(n_clicks, sample_rate):
#     """Start DAQ streaming with the specified sample rate"""
#     if n_clicks is None:
#         return dash.no_update

#     # Update sample rate and start streaming
#     daq_streamer._sampling_rate = sample_rate
#     daq_streamer.start()

#     # Force WebSocket reconnection with a timestamp
#     import time
#     return f"ws://127.0.0.1:5000/daq_stream?t={int(time.time())}"


# @callback(
#     Output("ws-daq", "url", allow_duplicate=True),
#     Input("stop-daq-btn", "n_clicks"),
#     prevent_initial_call=True
# )
# def stop_daq_streaming(n_clicks):
#     """Stop DAQ streaming"""
#     if n_clicks:
#         daq_streamer.stop()
#         # Return a dummy URL to cause the websocket to disconnect
#         import time
#         return f"ws://127.0.0.1:5000/daq_stream?stopped={int(time.time())}"


# # Enable/disable manual Y-axis scale inputs
# @callback(
#     [Output({"type": "y-min", "index": MATCH}, "disabled"),
#      Output({"type": "y-max", "index": MATCH}, "disabled")],
#     Input({"type": "y-scale-mode", "index": MATCH}, "value")
# )
# def toggle_y_scale_inputs(scale_mode):
#     """Enable or disable Y-axis min/max inputs based on scale mode"""
#     return scale_mode != "manual", scale_mode != "manual"

# # Callback to save monitors configuration
# @callback(
#     Output("save-config-status", "children"),
#     Output("plot-config-store", "data"),
#     [Input("save-config-btn", "n_clicks")],
#     [State({"type": "channel-selector", "index": ALL}, "value"),
#      State({"type": "y-scale-mode", "index": ALL}, "value"),
#      State({"type": "y-min", "index": ALL}, "value"),
#      State({"type": "y-max", "index": ALL}, "value"),
#      State({"type": "display-samples", "index": ALL}, "value"),
#      State("sample-rate-input", "value"),
#      State("buffer-size-select", "value"),
#      State("plot-config-store", "data")]
# )
# def save_current_config(n_clicks, channels, y_scale_modes, y_mins, y_maxs,
#                         display_samples, sample_rate, buffer_size, plot_config):
#     if n_clicks is None:
#         return dash.no_update, dash.no_update

#     # Get current plot configs
#     current_plots = plot_config.get("plots", [])

#     # Create new config structure
#     new_config = {
#         "global": {
#             "buffer_size": buffer_size,
#             "sample_rate": sample_rate
#         },
#         "plots": []
#     }

#     # Build the plots config
#     for i in range(len(channels)):
#         # Get the current plot configuration to preserve existing values
#         current_plot = current_plots[i] if i < len(current_plots) else {}

#         # Preserve width and height (and other properties)
#         plot_data = {
#             "title": current_plot.get("title", f"Signal Monitor {i + 1}"),
#             "channels": channels[i] if channels[i] else [],
#             "legend_strings": current_plot.get("legend_strings", []),
#             "y_scale_mode": y_scale_modes[i],
#             "y_min": y_mins[i],
#             "y_max": y_maxs[i],
#             "display_samples": display_samples[i],
#             "width": current_plot.get("width", 800),  # Preserve width
#             "height": current_plot.get("height", 300)  # Preserve height
#         }
#         new_config["plots"].append(plot_data)

#     # Save the config
#     from config import save_config
#     success = save_config(new_config)

#     # Also update the plot-config-store
#     new_store_data = {"plots": new_config["plots"]}

#     message = dmc.Alert(
#         "Configuration saved successfully!",
#         title="Success",
#         color="green",
#         withCloseButton=True,
#         duration=3000,
#     ) if success else dmc.Alert(
#         "Error saving configuration.",
#         title="Error",
#         color="red",
#         withCloseButton=True,
#     )

#     return message, new_store_data
