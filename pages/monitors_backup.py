import dash
from dash import callback, html, dcc, Input, Output, State, ctx, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import plotly.graph_objects as go
import numpy

from devices import daq_card
from controllers.utils.CircularBuffer import CircularBuffer

dash.register_page(__name__)

page_config = {
        "is_running": False,
        "sample_rate": 1000,
        "update_interval": 1000,  # ms
        "channels": [],
        "buffer_length": 20,  # seconds
        "auto_scale": True,
        "y_min": -10,
        "y_max": 10
    }

# Constants
MAX_BUFFER_SIZE = 20000  # Maximum number of points to store
SAMPLES_PER_READ = 500  # Number of samples to read in each acquisition cycle
# Initialize global objects
data_buffer = CircularBuffer(MAX_BUFFER_SIZE)

# DAQ available channels
AVAILABLE_CHANNELS = [
                         {"label": f"Module 1 - Channel {i}", "value": f"cDAQ1Mod1/ai{i}"} for i in range(4)
                     ] + [
                         {"label": f"Module 2 - Channel {i}", "value": f"cDAQ1Mod2/ai{i}"} for i in range(4)
                     ]

# JavaScript for clientside callback
update_graph_clientside = """
function(n_intervals, data, config) {
    // If no data, return empty figure
    if (!data || !data.channel_data || Object.keys(data.channel_data).length === 0) {
        return {
            'data': [],
            'layout': {
                'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                'plot_bgcolor': "#25262b",
                'paper_bgcolor': "#25262b",
                'font': {'color': "#c1c2c5"},
                'xaxis': {
                    'showgrid': true,
                    'gridcolor': "#373A40",
                    'title': "Time (s)",
                    'range': [0, config.buffer_length]
                },
                'yaxis': {
                    'showgrid': true,
                    'gridcolor': "#373A40",
                    'title': "Voltage (V)"
                },
                'showlegend': false
            }
        };
    }

    // Process data
    const channel_data = data.channel_data;
    const channels = Object.keys(channel_data);

    // Get first channel's data to determine length
    const first_channel = channels[0];
    const data_length = channel_data[first_channel].length;

    // Generate x-axis values based on sample rate
    const x_values = Array.from({length: data_length}, (_, i) => i / config.sample_rate);

    // Create traces for each channel
    const traces = channels.map((channel, i) => {
        const color = config.colors[i % config.colors.length];
        return {
            x: x_values,
            y: channel_data[channel],
            mode: 'lines',
            name: channel,
            type: 'scattergl',
            line: {color: color, width: 1},
            hoverinfo: 'none'
        };
    });

    // Create layout
    const layout = {
        margin: {l: 0, r: 0, t: 0, b: 0},
        plot_bgcolor: "#25262b",
        paper_bgcolor: "#25262b",
        font: {color: "#c1c2c5"},
        xaxis: {
            showgrid: true,
            gridcolor: "#373A40",
            title: "Time (s)",
            range: [0, config.buffer_length]
        },
        yaxis: {
            showgrid: true,
            gridcolor: "#373A40",
            title: "Voltage (V)"
        },
        showlegend: false
    };

    // Set Y-axis range if not auto-scaling
    if (!config.auto_scale) {
        layout.yaxis.range = [config.y_min, config.y_max];
    }

    return {
        data: traces,
        layout: layout
    };
}
"""

# Define controls section
def create_controls_section():
    return dmc.Paper(
        p="md",
        mb=16,
        children=[
            dmc.Grid(
                children=[
                    # Start/Stop buttons
                    dmc.Flex(
                        direction="column",
                        gap="md",
                        style={"flex": 1},
                        children=[
                            dmc.Button(
                                "Start Acquisition",
                                id="start-button",
                                color="green",
                                fullWidth=True,
                                mb=8
                            ),
                            dmc.Button(
                                "Stop Acquisition",
                                id="stop-button",
                                color="red",
                                fullWidth=True
                            )
                        ]
                    ),

                    # Sample rate and update interval
                    dmc.Flex(
                        direction="column",
                        gap="md",
                        style={"flex": 1},
                        children=[
                            dmc.NumberInput(
                                id="sample-rate",
                                label="Sample Rate (Hz)",
                                value=1000,
                                min=100,
                                max=10000,
                                step=100,
                                description="Samples per second"
                            ),
                            dmc.NumberInput(
                                id="update-interval",
                                label="Update Interval (ms)",
                                value=100,
                                min=50,
                                max=1000,
                                step=50,
                                description="Plot refresh rate"
                            )
                        ]
                    ),

                    # Channel selection and buffer settings
                    dmc.Flex(
                        direction="column",
                        gap="md",
                        style={"flex": 1},
                        children=[
                            dmc.MultiSelect(
                                id="selected-channels",
                                label="Channels to Monitor",
                                data=AVAILABLE_CHANNELS,
                                value=["cDAQ1Mod1/ai0", "cDAQ1Mod1/ai1"],
                                searchable=True,
                                mb=8
                            ),
                            dmc.Group(
                                children=[
                                    dmc.NumberInput(
                                        id="buffer-length",
                                        label="Display Buffer (s)",
                                        value=10,
                                        min=1,
                                        max=60,
                                        description="Seconds of data to display"
                                    ),
                                    dmc.Switch(
                                        id="auto-scale",
                                        label="Auto Y-scale",
                                        checked=True,
                                        mt=16
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Define plotting section
def create_plotting_section():
    return dmc.Paper(
        p="md",
        children=[
            # Graph component
            dcc.Graph(
                id="live-plot",
                style={"height": "500px"},
                config={
                    'staticPlot': True,  # Disable all interactivity
                    'displayModeBar': False  # Hide the mode bar
                }
            ),

            # Y-axis range controls
            dmc.Group(
                mt=8,
                justify="center",
                id="y-axis-controls",
                style={"display": "none"},
                children=[
                    dmc.NumberInput(
                        id="y-min",
                        label="Y-Min",
                        value=-10,
                        step=0.1,
                        style={"width": "150px"}
                    ),
                    dmc.NumberInput(
                        id="y-max",
                        label="Y-Max",
                        value=10,
                        step=0.1,
                        style={"width": "150px"}
                    )
                ]
            ),

            # Intervals for updating
            dcc.Interval(
                id="acquisition-interval",
                interval=500,  # Fast interval for data acquisition (10ms = 100Hz)
                n_intervals=0,
                disabled=True
            ),

            dcc.Interval(
                id="plot-interval",
                interval=1000,  # Default 100ms = 10Hz update rate
                n_intervals=0,
                disabled=True
            ),

            # Hidden div for sharing state
            html.Div(id="acquisition-state", style={"display": "none"}),

            # Data store for clientside callbacks
            dcc.Store(id="plot-data-store", data={}),
            dcc.Store(id="plot-config-store", data={
                "buffer_length": 10,
                "auto_scale": True,
                "y_min": -10,
                "y_max": 10,
                "sample_rate": 1000,
                "colors": ['#2196f3', '#f44336', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']
            }),
            # Add this to your create_plotting_section function
            dcc.Store(id="client-buffer-store", data={"channel_data": {}})
        ]
    )

def layout():
    return dmc.MantineProvider(
    children=[
        dmc.Container(
            fluid=True,
            style={"height": "100vh", "padding": "16px"},
            children=[
                # Title
                dmc.Title("DAQ Signal Monitor", order=1, mb=16),

                # Controls section
                create_controls_section(),

                # Plotting section
                create_plotting_section()
            ]
        )
    ]
)

# 1. Clientside callback to update the plot from client-buffer
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_plot'
    ),
    Output('live-plot', 'figure'),
    [Input('plot-interval', 'n_intervals')],
    [State('client-buffer-store', 'data'),  # Use client buffer instead of plot-data-store
     State('plot-config-store', 'data')],
    prevent_initial_call=True
)

# 2. Clientside callback to handle data acquisition (reduces server calls)
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='handle_data_acquisition'
    ),
    Output('plot-data-store', 'modified_timestamp'),
    [Input('acquisition-interval', 'n_intervals')],
    [State('plot-data-store', 'data')],
    prevent_initial_call=True
)

# 3. Clientside callback to accumulate data client-side
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='accumulate_data'
    ),
    Output('client-buffer-store', 'data'),
    [Input('plot-data-store', 'data')],
    [State('client-buffer-store', 'data'),
     State('plot-config-store', 'data')],
    prevent_initial_call=True
)

# Callback to toggle auto-scale controls visibility
# Modify the callback to toggle auto-scale controls
@callback(
    [Output("y-axis-controls", "style"),
     Output("plot-config-store", "data", allow_duplicate=True)],
    [Input("auto-scale", "checked")],
    [State("plot-config-store", "data")],
    prevent_initial_call=True
)
def toggle_y_controls(auto_scale, config):
    config["auto_scale"] = auto_scale
    if auto_scale:
        return {"display": "none"}, config
    else:
        return {"display": "block"}, config

# Callback to update Y-axis limits
@callback(
    Output("plot-config-store", "data", allow_duplicate=True),
    [Input("y-min", "value"),
     Input("y-max", "value")],
    [State("plot-config-store", "data")],
    prevent_initial_call=True
)
def update_y_limits(y_min, y_max, config):
    config["y_min"] = y_min
    config["y_max"] = y_max
    return config

# # Callback to start acquisition
# @callback(
#     [Output("acquisition-interval", "disabled", allow_duplicate=True),
#      Output("plot-interval", "disabled", allow_duplicate=True),
#      Output("plot-interval", "interval", allow_duplicate=True),
#      Output("acquisition-state", "children", allow_duplicate=True)],
#     [Input("start-button", "n_clicks")],
#     [State("sample-rate", "value"),
#      State("update-interval", "value"),
#      State("selected-channels", "value"),
#      State("buffer-length", "value")],
#     prevent_initial_call=True
# )
# def start_acquisition(n_clicks, sample_rate, update_interval, selected_channels, buffer_length):
#     # If button wasn't clicked or no channels selected, do nothing
#     if not n_clicks or not selected_channels:
#         return True, True, update_interval, "not_started"
#
#     # Update configuration
#     page_config["sample_rate"] = sample_rate
#     page_config["update_interval"] = update_interval
#     page_config["channels"] = selected_channels
#     page_config["buffer_length"] = buffer_length
#
#     # Clear any existing data
#     data_buffer.clear()
#
#     # Initialize and start the DAQ
#     if daq_card.initialize(selected_channels, sample_rate):
#         if daq_card.start():
#             page_config["is_running"] = True
#             # Enable both intervals
#             return False, False, update_interval, "started"
#
#     # If we get here, something failed
#     return True, True, update_interval, "failed"


# Callback to start acquisition
@callback(
    [Output("acquisition-interval", "disabled", allow_duplicate=True),
     Output("plot-interval", "disabled", allow_duplicate=True),
     Output("plot-interval", "interval", allow_duplicate=True),
     Output("acquisition-state", "children", allow_duplicate=True),
     Output("plot-config-store", "data", allow_duplicate=True)],
    [Input("start-button", "n_clicks")],
    [State("sample-rate", "value"),
     State("update-interval", "value"),
     State("selected-channels", "value"),
     State("buffer-length", "value"),
     State("plot-config-store", "data")],
    prevent_initial_call=True
)
def start_acquisition(n_clicks, sample_rate, update_interval, selected_channels, buffer_length, config):
    # If button wasn't clicked or no channels selected, do nothing
    if not n_clicks or not selected_channels:
        return True, True, update_interval, "not_started", config

    # Update page configuration variable
    page_config["sample_rate"] = sample_rate
    page_config["update_interval"] = update_interval
    page_config["channels"] = selected_channels
    page_config["buffer_length"] = buffer_length
    # Update configuration
    config["sample_rate"] = sample_rate
    config["buffer_length"] = buffer_length

    # Clear any existing data
    data_buffer.clear()

    # Initialize and start the DAQ
    if daq_card.initialize(selected_channels, sample_rate):
        if daq_card.start():
            page_config["is_running"] = True
            # Enable both intervals
            return False, False, update_interval, "started", config

    # For now, just return as if it worked
    return False, False, update_interval, "started", config

# Callback to stop acquisition
@callback(
    [Output("acquisition-interval", "disabled", allow_duplicate=True),
     Output("plot-interval", "disabled", allow_duplicate=True),
     Output("acquisition-state", "children", allow_duplicate=True)],
    [Input("stop-button", "n_clicks")],
    prevent_initial_call=True
)
def stop_acquisition(n_clicks):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    # Stop DAQ
    daq_card.stop()
    daq_card.close()
    page_config["is_running"] = False

    # Disable intervals
    return True, True, "stopped"


# # Callback for data acquisition
# @callback(
#     Output("acquisition-state", "children", allow_duplicate=True),
#     Input("acquisition-interval", "n_intervals"),
#     prevent_initial_call=True
# )
# def acquire_data(n_intervals):
#     if not page_config["is_running"]:
#         return "not_running"
#
#     # Create buffer for this read operation
#     num_channels = len(page_config["channels"])
#     data_buffer_read = numpy.zeros((num_channels, SAMPLES_PER_READ), dtype=numpy.float64)
#
#     # Read data from DAQ
#     if daq_card.read_data(data_buffer_read, SAMPLES_PER_READ):
#         # Convert to dictionary format
#         data_dict = {}
#         for i, channel in enumerate(page_config["channels"]):
#             data_dict[channel] = data_buffer_read[i, :]
#
#         # Add to circular buffer
#         data_buffer.add_data(data_dict)
#
#         return f"acquired_{n_intervals}"
#
#     return "read_failed"


# # Callback to update the plot using WebGL
# @callback(
#     Output("live-plot", "figure", allow_duplicate=True),
#     Input("plot-interval", "n_intervals"),
#     prevent_initial_call=True
# )
# def update_plot(n_intervals):
#     # Calculate how many points to display based on buffer length and sample rate
#     max_points = int(page_config["buffer_length"] * page_config["sample_rate"])
#
#     # Get data from buffer
#     channel_data = data_buffer.get_data(max_points=max_points)
#
#     # Create figure
#     fig = go.Figure()
#
#     if channel_data:
#         # Find data length (all channels should have same length)
#         first_channel = next(iter(channel_data))
#         data_length = len(channel_data[first_channel])
#
#         if data_length > 0:
#             # Generate x-axis values based on sample rate
#             # x-values represent time in seconds, starting from 0
#             x_values = numpy.arange(data_length) / page_config["sample_rate"]
#
#             # Add each channel to the plot with a different color using WebGL
#             colors = ['#2196f3', '#f44336', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']
#             for i, (channel, values) in enumerate(channel_data.items()):
#                 color = colors[i % len(colors)]
#
#                 # Using scattergl instead of scatter for WebGL acceleration
#                 fig.add_trace(go.Scattergl(
#                     x=x_values,
#                     y=values,
#                     mode='lines',
#                     name=channel,
#                     line=dict(color=color, width=1),
#                     hoverinfo='none'  # Explicitly disable hover info
#                 ))
#
#     # Update layout
#     fig.update_layout(
#         margin=dict(l=0, r=0, t=0, b=0),
#         plot_bgcolor="#25262b",
#         paper_bgcolor="#25262b",
#         font=dict(color="#c1c2c5"),
#         xaxis=dict(
#             showgrid=True,
#             gridcolor="#373A40",
#             title="Time (s)",
#             range=[0, page_config["buffer_length"]]
#         ),
#         yaxis=dict(
#             showgrid=True,
#             gridcolor="#373A40",
#             title="Voltage (V)"
#         ),
#         showlegend=False  # Disable legend for better performance
#     )
#
#     # Set Y-axis range if not auto-scaling
#     if not page_config["auto_scale"]:
#         fig.update_yaxes(range=[page_config["y_min"], page_config["y_max"]])
#
#     return fig


# 8. Server-side callback to update data store (throttled)
@callback(
    Output("plot-data-store", "data"),
    [Input("acquisition-interval", "n_intervals"),
     Input("plot-data-store", "modified_timestamp")],  # This will be triggered by the clientside callback
    [State("plot-config-store", "data")],
    prevent_initial_call=True
)
def update_data_store(n_intervals, modified_timestamp, config):
    # Only update every 5 intervals to reduce server load
    if n_intervals % 5 != 0:
        raise PreventUpdate

    if not page_config["is_running"]:
        return {"channel_data": {}}

    # Create buffer for this read operation
    num_channels = len(page_config["channels"])

    # Ensure we have at least one channel
    if num_channels == 0:
        return {"channel_data": {}}

    # Create buffer with the correct shape
    data_buffer_read = numpy.zeros((num_channels, SAMPLES_PER_READ), dtype=numpy.float64)

    # Read data from DAQ
    if daq_card.read_data(data_buffer_read, SAMPLES_PER_READ):
        # Convert to dictionary format
        data_dict = {}
        for i, channel in enumerate(page_config["channels"]):
            data_dict[channel] = data_buffer_read[i, :].tolist()  # Convert to list for JSON serialization

        return {"channel_data": data_dict}

    return {"channel_data": {}}