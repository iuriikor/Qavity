import dash
from dash import html, dcc, callback, Input, Output, State, _dash_renderer
import dash_mantine_components as dmc
import plotly.graph_objs as go
from dash_extensions import WebSocket
import threading
import asyncio
import time
import logging
import cherrypy
from hypercorn.config import Config
from hypercorn.asyncio import serve as hypercorn_serve
from flask import Flask
from quart import Quart, websocket

import sys
import os
# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devices import daq_card, daq_streamer

_dash_renderer._set_react_version("18.2.0")
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create separate Flask and Quart apps
dash_server = Flask('DAQ_Debug')
quart_app = Quart(__name__)

# Initialize Dash app with Flask server
app = dash.Dash(server=dash_server, external_stylesheets=dmc.styles.ALL)

# Use real DAQ card and streamer from main app
# The daq_card and daq_streamer are already initialized in the main app's devices module
print(f"Using real DAQ card with {len(daq_card.channels)} channels: {daq_card.channels}")
print(f"DAQ streamer configured for path: {daq_streamer._path}")

# Update the streamer to use our debug path
daq_streamer._path = '/daq_debug_stream'
print(f"DAQ streamer path updated to: {daq_streamer._path}")

# Layout
app.layout = dmc.MantineProvider([
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
        
        # Plots for real DAQ channels
        dmc.SimpleGrid(
            cols=2,
            children=[
                dmc.Card([
                    dmc.Text(f"Channel: {daq_card.channels[i] if i < len(daq_card.channels) else 'N/A'}", fw=500, mb="sm"),
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
                ], withBorder=True, p="sm") for i in range(min(4, len(daq_card.channels)))
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
        daq_streamer._update_rate = update_rate or 20
        success = daq_streamer.start()
        if success:
            return dmc.Alert("Streaming started", color="green")
        else:
            return dmc.Alert("Failed to start streaming", color="red")
    
    elif trigger_id == "stop-btn" and stop_clicks:
        daq_streamer.stop()
        return dmc.Alert("Streaming stopped", color="orange")
    
    elif trigger_id == "update-rate-input":
        daq_streamer._update_rate = update_rate or 20
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
    Output("hidden-data-trigger", "children", allow_duplicate=True),
    Input("ws-debug", "message"),
    prevent_initial_call=True
)

# Graph update callbacks for real DAQ channels
for i in range(min(4, len(daq_card.channels))):
    channel_name = daq_card.channels[i]
    
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
                        yaxis: {{title: 'Voltage (V)', range: [-10, 10]}},
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
                    yaxis: {{title: 'Voltage (V)', range: [-10, 10]}},
                    height: 300,
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)'
                }}
            }};
        }}
        """,
        Output(f"graph-{i}", "figure"),
        Input("hidden-data-trigger", "children"),
        Input("display-samples-select", "value"),
        prevent_initial_call=True
    )

if __name__ == '__main__':
    try:
        # Configure CherryPy for the Dash app
        def start_cherrypy():
            # CherryPy configuration
            cherrypy_config = {
                'server.socket_host': '127.0.0.1',
                'server.socket_port': 8050,
                'server.thread_pool': 4,  # Adjust based on expected concurrent users
                'engine.autoreload.on': False,  # Disable autoreload for production
                'log.screen': True,  # Show logs on console
                'log.access_file': '',
                'log.error_file': '',
                'response.timeout': 3600,  # Long timeout for dashboard sessions (1 hour)
            }

            # Apply configuration
            cherrypy.config.update(cherrypy_config)

            # Mount the Flask app
            cherrypy.tree.graft(dash_server, '/')

            # Start CherryPy engine
            print(f"Starting CherryPy server on {cherrypy_config['server.socket_host']}:{cherrypy_config['server.socket_port']}")
            cherrypy.engine.start()


        # Configure Hypercorn for the WebSocket server
        async def start_hypercorn():
            # Hypercorn configuration
            config = Config()
            config.bind = ["127.0.0.1:5001"]  # WebSocket port
            config.use_reloader = False  # Disable reloader for production
            config.workers = 1  # Single worker for debug
            config.keep_alive_timeout = 120  # 2 minutes keep-alive
            config.websocket_ping_interval = 30  # Send ping every 30 seconds
            config.websocket_timeout = 300  # 5 minutes timeout for WebSockets

            # Start Hypercorn with Quart
            print(f"Starting Hypercorn WebSocket server on {config.bind}")
            await hypercorn_serve(quart_app, config)


        # Start CherryPy in a separate thread
        cherrypy_thread = threading.Thread(target=start_cherrypy)
        cherrypy_thread.daemon = True
        cherrypy_thread.start()

        # Small delay to ensure CherryPy starts
        time.sleep(2)
        
        print("Starting DAQ Debug Monitor...")
        print("Dash server starting on http://127.0.0.1:8050")
        print("WebSocket server starting on ws://127.0.0.1:5001")
        print("WebSocket endpoint registered at: /daq_debug_stream")
        print("Open http://127.0.0.1:8050 in your browser")

        # Run Hypercorn in the main thread
        # We use asyncio.run which handles the event loop for us
        asyncio.run(start_hypercorn())

    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up resources
        print("Stopping CherryPy server...")
        if cherrypy.engine.state in (cherrypy.engine.states.STARTED, cherrypy.engine.states.STARTING):
            cherrypy.engine.stop()

        print("Closing DAQ resources...")
        daq_card.close()

        print("Servers stopped, all resources released.")
