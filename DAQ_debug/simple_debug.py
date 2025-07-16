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
import numpy
import struct

import sys
import os
# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devices import daq_streamer
from controllers.DAQ.NI_cDAQ9174 import cDAQ9174

_dash_renderer._set_react_version("18.2.0")
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create separate Flask and Quart apps
dash_server = Flask('DAQ_Debug')
quart_app = Quart(__name__)

# Initialize Dash app with Flask server
app = dash.Dash(server=dash_server, external_stylesheets=dmc.styles.ALL)

# Create actual NI DAQ device with same configuration as main app
ni_daq_device = cDAQ9174()
# Configure DAQ with actual channels - same as main app
daq_channels = ['cDAQ1Mod1/ai0', 'cDAQ1Mod1/ai1', 'cDAQ1Mod1/ai2', 'cDAQ1Mod1/ai3',
                'cDAQ1Mod2/ai0', 'cDAQ1Mod2/ai1', 'cDAQ1Mod2/ai2', 'cDAQ1Mod2/ai3']
ni_daq_device.initialize(channels=daq_channels, sample_rate=1000)

# Replace the device in the existing streamer
daq_streamer._daq = ni_daq_device

# Update the streamer's circular buffer to use actual DAQ channels
daq_streamer._buffer.clear()
for channel in ni_daq_device.channels:
    daq_streamer._buffer.add_channel(channel)

print(f"Using NI DAQ device with {len(ni_daq_device.channels)} channels: {ni_daq_device.channels}")
print(f"DAQ streamer configured for path: {daq_streamer._path}")

# The DAQ streamer will now use the actual NI DAQ device with the same streaming logic
# We just need to update the path and re-register the endpoint
daq_streamer._path = '/daq_debug_stream'

# Register the endpoint using the existing streamer's register method
# Since the streamer is already initialized, we need to manually register on our quart app
@quart_app.websocket('/daq_debug_stream')
async def daq_debug_stream():
    from quart import websocket
    print(f'DAQ DEBUG WEBSOCKET CONNECTED')
    
    # Task for high-frequency data acquisition
    acquisition_task = None
    
    try:
        # Define the data acquisition coroutine - same as main app
        async def acquire_data():
            samples_per_read = 50  # Read 50 samples at a time for efficiency
            sleep_time = 1.0 / daq_streamer._update_rate
            
            while daq_streamer._streaming:
                start_time = time.time()
                
                # Read data from fake DAQ device
                current_data = numpy.zeros((len(daq_streamer._daq.channels), samples_per_read))
                success = daq_streamer._daq.read_data(current_data, samples_per_read)
                
                if success:
                    # Add data to circular buffer for each channel
                    data_dict = {}
                    for i, channel in enumerate(daq_streamer._daq.channels):
                        data_dict[channel] = current_data[i, :].tolist()
                    
                    # Update the buffer
                    daq_streamer._buffer.add_data(data_dict)
                    
                    # Track acquisition timing
                    acq_time = time.time() - start_time
                    daq_streamer._timing_stats['acquisition_times'].append(acq_time)
                    
                    # Keep only last 100 measurements for stats
                    if len(daq_streamer._timing_stats['acquisition_times']) > 100:
                        daq_streamer._timing_stats['acquisition_times'] = daq_streamer._timing_stats['acquisition_times'][-100:]
                    
                    if daq_streamer._debug_enabled and len(daq_streamer._timing_stats['acquisition_times']) % 50 == 0:
                        avg_acq_time = sum(daq_streamer._timing_stats['acquisition_times']) / len(daq_streamer._timing_stats['acquisition_times'])
                        # daq_streamer._logger.info(f"Avg acquisition time: {avg_acq_time*1000:.2f}ms")
                
                # Sleep to maintain the sampling rate
                await asyncio.sleep(sleep_time)
        
        # Define frontend update coroutine - using binary format (same as main app)
        async def update_frontend():
            # Fixed update interval based on streamer's update rate
            update_interval = 1.0 / daq_streamer._update_rate
            
            # Track the last position we sent to avoid echoing
            last_sent_length = {}
            
            while daq_streamer._streaming:
                try:
                    start_time = time.time()
                    
                    # Get all data from the buffer
                    buffer_data = daq_streamer._buffer.get_data()
                    
                    # Get timestamp
                    current_time = time.time()
                    
                    # Use fixed samples per update to control data size
                    samples_per_update = getattr(daq_streamer, '_samples_per_update', 200)
                    
                    # Debug: Check buffer data structure
                    if len(buffer_data) == 0:
                        print("Warning: Empty buffer data")
                        await asyncio.sleep(update_interval)
                        continue
                    
                    # Count channels with data and prepare data to send
                    channels_to_send = {}
                    
                    for channel_name, data in buffer_data.items():
                        if len(data) == 0:
                            continue
                        
                        # Get the current buffer length
                        current_length = len(data)
                        
                        # Initialize tracking for this channel if needed
                        if channel_name not in last_sent_length:
                            last_sent_length[channel_name] = 0
                        
                        # Calculate how much new data we have
                        new_data_count = current_length - last_sent_length[channel_name]
                        
                        if new_data_count > 0:
                            # Send only NEW data since last update to avoid echoing
                            # But limit to samples_per_update to prevent overwhelming frontend
                            data_to_send = data[last_sent_length[channel_name]:]
                            if len(data_to_send) > samples_per_update:
                                data_to_send = data_to_send[-samples_per_update:]
                            
                            channels_to_send[channel_name] = data_to_send
                            last_sent_length[channel_name] = current_length
                    
                    # Skip if no new data to send
                    if len(channels_to_send) == 0:
                        await asyncio.sleep(update_interval)
                        continue
                    
                    # Start with timestamp and number of channels WITH DATA
                    binary_data = struct.pack('!di', current_time, len(channels_to_send))
                    
                    for channel_name, data_to_send in channels_to_send.items():
                        # Channel name
                        name_bytes = channel_name.encode('utf-8')
                        binary_data += struct.pack('!i', len(name_bytes))
                        binary_data += name_bytes
                        
                        # Data length and values
                        binary_data += struct.pack('!i', len(data_to_send))
                        # Pack all data values at once
                        binary_data += struct.pack('!' + 'd' * len(data_to_send), *data_to_send)
                    
                    # Debug: Log data structure occasionally
                    if current_time % 5 < 0.1:  # Log every ~5 seconds
                        print(f"Debug: Update rate: {daq_streamer._update_rate}Hz (interval: {update_interval*1000:.1f}ms)")
                        print(f"Debug: Sending {len(channels_to_send)} channels, buffer size: {len(binary_data)} bytes")
                        for ch, data in channels_to_send.items():
                            total_buffer_size = len(buffer_data.get(ch, []))
                            print(f"Debug: {ch}: {len(data)} new samples (total buffer: {total_buffer_size})")
                    
                    # Send binary data to frontend
                    await websocket.send(binary_data)
                    
                except Exception as e:
                    print(f"Error in update_frontend: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Use fixed update interval based on streamer's update rate
                await asyncio.sleep(update_interval)
        
        # Main websocket loop - run acquisition and transmission in parallel (same as main app)
        while True:
            if not daq_streamer._streaming:
                # If streaming is off, wait and check again
                await asyncio.sleep(0.5)
                continue
            
            # Start data acquisition task if not already running
            if acquisition_task is None or acquisition_task.done():
                acquisition_task = asyncio.create_task(acquire_data())
            
            # Create transmission task for parallel execution
            transmission_task = asyncio.create_task(update_frontend())
            
            # Wait for the transmission task to complete
            await transmission_task
    
    except asyncio.CancelledError:
        print(f'DAQ DEBUG WEBSOCKET DISCONNECTED')
        if acquisition_task and not acquisition_task.done():
            acquisition_task.cancel()
    except Exception as e:
        print(f'ERROR IN DAQ DEBUG STREAM: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        print(f'DAQ DEBUG STREAM HANDLER EXITED')
        daq_streamer.stop()  # Ensure DAQ is stopped when websocket disconnects
        if acquisition_task and not acquisition_task.done():
            acquisition_task.cancel()

print("DAQ debug WebSocket endpoint registered at: /daq_debug_stream")

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
        
        # Y-axis controls
        dmc.Group([
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
        ], mb="md"),
        
        # Status
        html.Div(id="status-display", style={"marginBottom": "10px"}),
        
        # Plots for NI DAQ channels
        dmc.SimpleGrid(
            cols=2,
            children=[
                dmc.Card([
                    dmc.Text(f"Channel: {ni_daq_device.channels[i] if i < len(ni_daq_device.channels) else 'N/A'}", fw=500, mb="sm"),
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
                ], withBorder=True, p="sm") for i in range(min(4, len(ni_daq_device.channels)))
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
        # Also update the samples_per_update to control frontend update frequency
        daq_streamer._samples_per_update = min(200, max(50, int(1000 / (update_rate or 20))))
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

# Graph update callbacks for NI DAQ channels
for i in range(min(4, len(ni_daq_device.channels))):
    channel_name = ni_daq_device.channels[i]
    
    app.clientside_callback(
        f"""
        function(dataSignal, displaySamples, yScaleMode, yMin, yMax) {{
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
                        yaxis: {{title: 'Voltage (V)'}},
                        height: 300
                    }}
                }};
            }}
            
            const channelData = data[channelName];
            const displayData = channelData.length > displaySize ? 
                channelData.slice(-displaySize) : channelData;
            
            const xData = Array.from({{length: displayData.length}}, (_, i) => i);
            
            // Calculate Y-axis range
            let yAxisRange;
            if (yScaleMode === 'manual') {{
                const yMinValue = parseFloat(yMin);
                const yMaxValue = parseFloat(yMax);
                
                if (!isNaN(yMinValue) && !isNaN(yMaxValue) && yMaxValue > yMinValue) {{
                    yAxisRange = [yMinValue, yMaxValue];
                }} else {{
                    // Fallback to auto if manual values are invalid
                    const dataMin = Math.min(...displayData);
                    const dataMax = Math.max(...displayData);
                    const range = dataMax - dataMin;
                    const margin = Math.max(range * 0.1, 0.01);
                    yAxisRange = [dataMin - margin, dataMax + margin];
                }}
            }} else {{
                // Auto scale
                if (displayData.length > 0) {{
                    const dataMin = Math.min(...displayData);
                    const dataMax = Math.max(...displayData);
                    const range = dataMax - dataMin;
                    const margin = Math.max(range * 0.1, 0.01);
                    yAxisRange = [dataMin - margin, dataMax + margin];
                }} else {{
                    yAxisRange = [-1, 1];
                }}
            }}
            
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
                    yaxis: {{title: 'Voltage (V)', range: yAxisRange}},
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
        Input("y-scale-mode", "value"),
        Input("y-min", "value"),
        Input("y-max", "value"),
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

        print("Closing NI DAQ resources...")
        ni_daq_device.close()

        print("Servers stopped, all resources released.")
