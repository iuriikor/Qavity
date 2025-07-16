import threading
import asyncio
import time
from hypercorn.config import Config
from hypercorn.asyncio import serve as hypercorn_serve
from flask import Flask
from quart import Quart, websocket
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_extensions import WebSocket
import plotly.graph_objs as go
import logging

from fake_device import FakeDAQDevice
from fake_streamer import FakeDAQStreamer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create separate Flask and Quart apps (similar to main app)
dash_server = Flask('DAQ_Debug')
quart_app = Quart(__name__)

# Initialize Dash app with Flask server
app = dash.Dash(server=dash_server, external_stylesheets=dmc.styles.ALL)

# Create fake device and streamer - use unique instances
fake_device = FakeDAQDevice(num_channels=4)
fake_device.initialize(
    channels=["ch0_1Hz", "ch1_2Hz", "ch2_5Hz", "ch3_10Hz"],
    sample_rate=1000
)
fake_streamer = FakeDAQStreamer(fake_device, update_rate=20)

# WebSocket endpoint
@quart_app.websocket('/daq_debug_stream')
async def daq_debug_stream():
    logger.info("WebSocket connection established")
    try:
        await fake_streamer.stream_data(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

# Layout function
def create_layout():
    return dmc.MantineProvider([
        dmc.Container([
            dmc.Title("DAQ Debug Monitor", order=1),
            
            # Controls
            dmc.Group([
                dmc.Button("Start Streaming", id="start-btn", color="green"),
                dmc.Button("Stop Streaming", id="stop-btn", color="red"),
                dmc.NumberInput(
                    id="update-rate-input",
                    label="Update Rate (Hz)",
                    value=20,
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
            ], mb="md"),
            
            # Status
            html.Div(id="status-display", style={"marginBottom": "10px"}),
            
            # Plots in 2x2 grid
            dmc.SimpleGrid(
                cols=2,
                children=[
                    dmc.Card([
                        dmc.Text("Channel 0 - 1Hz Sine Wave", fw=500, mb="sm"),
                        dcc.Graph(
                            id="graph-0",
                            figure={
                                'data': [go.Scatter(x=[], y=[], mode='lines')],
                                'layout': go.Layout(
                                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                    xaxis={'title': 'Samples'},
                                    yaxis={'title': 'Amplitude'},
                                    height=300
                                )
                            },
                            config={'displayModeBar': False}
                        )
                    ], withBorder=True, p="sm"),
                    
                    dmc.Card([
                        dmc.Text("Channel 1 - 2Hz Sine Wave", fw=500, mb="sm"),
                        dcc.Graph(
                            id="graph-1",
                            figure={
                                'data': [go.Scatter(x=[], y=[], mode='lines')],
                                'layout': go.Layout(
                                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                    xaxis={'title': 'Samples'},
                                    yaxis={'title': 'Amplitude'},
                                    height=300
                                )
                            },
                            config={'displayModeBar': False}
                        )
                    ], withBorder=True, p="sm"),
                    
                    dmc.Card([
                        dmc.Text("Channel 2 - 5Hz Sine Wave", fw=500, mb="sm"),
                        dcc.Graph(
                            id="graph-2",
                            figure={
                                'data': [go.Scatter(x=[], y=[], mode='lines')],
                                'layout': go.Layout(
                                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                    xaxis={'title': 'Samples'},
                                    yaxis={'title': 'Amplitude'},
                                    height=300
                                )
                            },
                            config={'displayModeBar': False}
                        )
                    ], withBorder=True, p="sm"),
                    
                    dmc.Card([
                        dmc.Text("Channel 3 - 10Hz Sine Wave", fw=500, mb="sm"),
                        dcc.Graph(
                            id="graph-3",
                            figure={
                                'data': [go.Scatter(x=[], y=[], mode='lines')],
                                'layout': go.Layout(
                                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                    xaxis={'title': 'Samples'},
                                    yaxis={'title': 'Amplitude'},
                                    height=300
                                )
                            },
                            config={'displayModeBar': False}
                        )
                    ], withBorder=True, p="sm"),
                ]
            ),
            
            # WebSocket and hidden trigger
            WebSocket(url="ws://127.0.0.1:5001/daq_debug_stream", id="ws-debug"),
            html.Div(id="hidden-data-trigger", style={"display": "none"}),
            
        ], size="xl")
    ])

# Callbacks
@callback(
    Output("status-display", "children"),
    Input("start-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"),
    Input("update-rate-input", "value"),
    prevent_initial_call=True
)
def control_streaming(start_clicks, stop_clicks, update_rate):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "start-btn" and start_clicks:
        fake_streamer.update_rate = update_rate or 20
        success = fake_streamer.start()
        if success:
            return dmc.Alert("Streaming started", color="green")
        else:
            return dmc.Alert("Failed to start streaming", color="red")
    
    elif trigger_id == "stop-btn" and stop_clicks:
        fake_streamer.stop()
        return dmc.Alert("Streaming stopped", color="orange")
    
    elif trigger_id == "update-rate-input":
        fake_streamer.update_rate = update_rate or 20
        return dmc.Alert(f"Update rate set to {update_rate}Hz", color="blue")
    
    return ""

# WebSocket data handler
app.clientside_callback(
    """
    function(message) {
        if (!message || !message.data) {
            return dash_clientside.no_update;
        }
        
        // Initialize window state
        if (!window.debugDaqState) {
            window.debugDaqState = {
                data: {},
                counter: 0,
                processingBlob: false
            };
        }
        
        // Handle Blob data
        if (message.data instanceof Blob) {
            if (window.debugDaqState.processingBlob) {
                return dash_clientside.no_update;
            }
            
            window.debugDaqState.processingBlob = true;
            
            const reader = new FileReader();
            reader.onload = function() {
                try {
                    const buffer = reader.result;
                    const view = new DataView(buffer);
                    let offset = 0;
                    
                    // Parse binary data
                    const timestamp = view.getFloat64(offset, false);
                    offset += 8;
                    
                    const numChannels = view.getInt32(offset, false);
                    offset += 4;
                    
                    const channelData = {};
                    
                    for (let i = 0; i < numChannels; i++) {
                        const nameLength = view.getInt32(offset, false);
                        offset += 4;
                        
                        const nameBytes = new Uint8Array(buffer, offset, nameLength);
                        const channelName = new TextDecoder('utf-8').decode(nameBytes);
                        offset += nameLength;
                        
                        const dataLength = view.getInt32(offset, false);
                        offset += 4;
                        
                        const values = [];
                        for (let j = 0; j < dataLength; j++) {
                            values.push(view.getFloat64(offset, false));
                            offset += 8;
                        }
                        
                        channelData[channelName] = values;
                    }
                    
                    // Accumulate data
                    if (!window.debugDaqState.accumulatedData) {
                        window.debugDaqState.accumulatedData = {};
                        for (const channelName in channelData) {
                            window.debugDaqState.accumulatedData[channelName] = [];
                        }
                    }
                    
                    const maxSamples = 2000;
                    for (const channelName in channelData) {
                        if (!window.debugDaqState.accumulatedData[channelName]) {
                            window.debugDaqState.accumulatedData[channelName] = [];
                        }
                        
                        window.debugDaqState.accumulatedData[channelName] = 
                            window.debugDaqState.accumulatedData[channelName].concat(channelData[channelName]);
                        
                        if (window.debugDaqState.accumulatedData[channelName].length > maxSamples) {
                            window.debugDaqState.accumulatedData[channelName] = 
                                window.debugDaqState.accumulatedData[channelName].slice(-maxSamples);
                        }
                    }
                    
                    window.debugDaqState.data = window.debugDaqState.accumulatedData;
                    window.debugDaqState.counter++;
                    
                    // Update trigger
                    const hiddenDiv = document.getElementById("hidden-data-trigger");
                    if (hiddenDiv) {
                        hiddenDiv.textContent = window.debugDaqState.counter.toString();
                    }
                    
                    window.debugDaqState.processingBlob = false;
                    
                } catch (e) {
                    console.error("Error processing debug DAQ data:", e);
                    window.debugDaqState.processingBlob = false;
                }
            };
            
            reader.readAsArrayBuffer(message.data);
            return window.debugDaqState.counter.toString();
        }
        
        return dash_clientside.no_update;
    }
    """,
    Output("hidden-data-trigger", "children"),
    Input("ws-debug", "message")
)

# Graph update callbacks
for i in range(4):
    channel_name = f"ch{i}_{[1,2,5,10][i]}Hz"
    
    app.clientside_callback(
        f"""
        function(dataSignal, displaySamples) {{
            if (!dataSignal || !window.debugDaqState || !window.debugDaqState.data) {{
                return dash_clientside.no_update;
            }}
            
            const data = window.debugDaqState.data;
            const channelName = "{channel_name}";
            const displaySize = parseInt(displaySamples) || 1000;
            
            if (!data[channelName] || data[channelName].length === 0) {{
                return {{
                    'data': [],
                    'layout': {{
                        margin: {{l: 40, b: 40, t: 10, r: 10}},
                        xaxis: {{title: 'Samples', range: [0, displaySize]}},
                        yaxis: {{title: 'Amplitude', range: [-2, 2]}},
                        height: 300
                    }}
                }};
            }}
            
            const channelData = data[channelName];
            const displayData = channelData.length > displaySize ? 
                channelData.slice(-displaySize) : channelData;
            
            const xData = Array.from({{length: displayData.length}}, (_, i) => i);
            
            return {{
                'data': [{{
                    x: xData,
                    y: displayData,
                    mode: 'lines',
                    line: {{color: '#1E88E5', width: 2}}
                }}],
                'layout': {{
                    margin: {{l: 40, b: 40, t: 10, r: 10}},
                    xaxis: {{title: 'Samples', range: [0, displaySize]}},
                    yaxis: {{title: 'Amplitude', range: [-2, 2]}},
                    height: 300,
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)'
                }}
            }};
        }}
        """,
        Output(f"graph-{i}", "figure"),
        Input("hidden-data-trigger", "children"),
        Input("display-samples-select", "value")
    )

if __name__ == '__main__':
    try:
        # Set app layout
        app.layout = create_layout()
        
        # Start Flask/Dash server in a separate thread
        def start_dash_server():
            app.run_server(debug=False, host='127.0.0.1', port=8050)
        
        dash_thread = threading.Thread(target=start_dash_server, daemon=True)
        dash_thread.start()
        
        # Small delay to ensure Dash server starts
        time.sleep(2)
        
        # Configure Hypercorn for the WebSocket server (similar to main app)
        async def start_hypercorn():
            config = Config()
            config.bind = ["127.0.0.1:5001"]  # Different port from main app
            config.use_reloader = False
            config.workers = 1  # Single worker for debug
            config.keep_alive_timeout = 120
            config.websocket_ping_interval = 30
            config.websocket_timeout = 300
            
            print(f"Starting Hypercorn WebSocket server on {config.bind}")
            await hypercorn_serve(quart_app, config)
        
        # Run Hypercorn in the main thread
        print("Starting DAQ Debug Monitor...")
        print("Open http://127.0.0.1:8050 in your browser")
        asyncio.run(start_hypercorn())
        
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Stopping servers...")
        fake_device.close()
        print("Debug monitor stopped.")