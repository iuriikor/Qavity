from dash import Output, Input, callback, ClientsideFunction, MATCH
from components.CameraInterfaceAIO import CameraInterfaceAIO

from server import app

# Handle binary data from websocket and update HtmlIMG src directly
app.clientside_callback(
    """
    function(message) {
        if (!message) return "";

        // Initialize window state if not exists
        if (!window.webcam1State) {
            window.webcam1State = {
                frameCount: 0,
                prevBlobUrl: null
            };
        }

        try {
            // Increment frame count - in case we want to have a periodic reconnect
            window.webcam1State.frameCount++;

            // Create a blob from the binary message
            const blob = new Blob([message.data], {type: 'image/jpeg'});

            // Clean up previous blob URL
            if (window.webcam1State.prevBlobUrl) {
                URL.revokeObjectURL(window.webcam1State.prevBlobUrl);
            }

            // Create and store new blob URL
            const url = URL.createObjectURL(blob);
            window.webcam1State.prevBlobUrl = url;

            // Use this code if you want to enforce periodic reconnect
            // Every 300 frames, force reconnection
            if (window.webcam1State.frameCount >= 300) {
                window.webcam1State.frameCount = 0;
            }
            return url;
        } catch (e) {
            console.error("Error processing frame:", e);
            return "";
        }
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
    Input("ws1", "message")
)

app.clientside_callback(
    """
    function(message) {
        if (!message) return "";

        // Initialize window state if not exists
        if (!window.webcam2State) {
            window.webcam2State = {
                frameCount: 0,
                prevBlobUrl: null
            };
        }

        try {
            // Increment frame count
            window.webcam2State.frameCount++;

            // Create a blob from the binary message
            const blob = new Blob([message.data], {type: 'image/jpeg'});

            // Clean up previous blob URL
            if (window.webcam2State.prevBlobUrl) {
                URL.revokeObjectURL(window.webcam2State.prevBlobUrl);
            }

            // Create and store new blob URL
            const url = URL.createObjectURL(blob);
            window.webcam2State.prevBlobUrl = url;

            // Every 300 frames, force reconnection
            if (window.webcam2State.frameCount >= 300) {
                window.webcam2State.frameCount = 0;
            }

            return url;
        } catch (e) {
            console.error("Error processing frame:", e);
            return "";
        }
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
    Input("ws2", "message")
)

# Commented out because webcam_3 is not active in the layout
# app.clientside_callback(
#     """
#     function(message) {
#         if (!message) return "";
# 
#         // Initialize window state if not exists
#         if (!window.webcam3State) {
#             window.webcam3State = {
#                 frameCount: 0,
#                 prevBlobUrl: null
#             };
#         }
# 
#         try {
#             // Increment frame count
#             window.webcam3State.frameCount++;
# 
#             // Create a blob from the binary message
#             const blob = new Blob([message.data], {type: 'image/jpeg'});
# 
#             // Clean up previous blob URL
#             if (window.webcam3State.prevBlobUrl) {
#                 URL.revokeObjectURL(window.webcam3State.prevBlobUrl);
#             }
# 
#             // Create and store new blob URL
#             const url = URL.createObjectURL(blob);
#             window.webcam3State.prevBlobUrl = url;
# 
#             // Every 300 frames, force reconnection
#             if (window.webcam3State.frameCount >= 300) {
#                 window.webcam3State.frameCount = 0;
#             }
# 
#             return url;
#         } catch (e) {
#             console.error("Error processing frame:", e);
#             return "";
#         }
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_3'), "src"),
#     Input("ws3", "message")
# )

# Callback to force WebSocket reconnection when Start is clicked
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Force WebSocket reconnection
            const ws = document.getElementById("ws1");

            if (ws && ws._websocket) {
                ws._websocket.close();
                // Create a new URL with timestamp to force reconnection
                const baseUrl = "ws://127.0.0.1:5000/stream1";
                const newUrl = baseUrl + "?t=" + new Date().getTime();

                // Update the URL attribute which Dash uses to create the WebSocket
                ws.setAttribute("url", newUrl);

                // Trigger Dash's prop change detection
                const event = new Event("dash-prop-change");
                ws.dispatchEvent(event);
            }
        }
        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.hidden_div('webcam_1'), 'children', allow_duplicate=True),
    Input(CameraInterfaceAIO.ids.start_stream_btn('webcam_1'), 'n_clicks'),
    prevent_initial_call=True
)

# Callback to force WebSocket reconnection when Start is clicked
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Force WebSocket reconnection
            const ws = document.getElementById("ws2");
            if (ws && ws._websocket) {
                ws._websocket.close();
                // Create a new URL with timestamp to force reconnection
                const baseUrl = "ws://127.0.0.1:5000/stream2";
                const newUrl = baseUrl + "?t=" + new Date().getTime();

                // Update the URL attribute which Dash uses to create the WebSocket
                ws.setAttribute("url", newUrl);

                // Trigger Dash's prop change detection
                const event = new Event("dash-prop-change");
                ws.dispatchEvent(event);
            }
        }
        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.hidden_div('webcam_2'), 'children', allow_duplicate=True),
    Input(CameraInterfaceAIO.ids.start_stream_btn('webcam_2'), 'n_clicks'),
    prevent_initial_call=True
)

# Commented out because webcam_3 is not active in the layout
# Callback to force WebSocket reconnection when Start is clicked
# app.clientside_callback(
#     """
#     function(n_clicks) {
#         if (n_clicks > 0) {
#             // Force WebSocket reconnection
#             const ws = document.getElementById("ws3");
#             if (ws && ws._websocket) {
#                 ws._websocket.close();
#                 // Create a new URL with timestamp to force reconnection
#                 const baseUrl = "ws://127.0.0.1:5000/stream3";
#                 const newUrl = baseUrl + "?t=" + new Date().getTime();
# 
#                 // Update the URL attribute which Dash uses to create the WebSocket
#                 ws.setAttribute("url", newUrl);
# 
#                 // Trigger Dash's prop change detection
#                 const event = new Event("dash-prop-change");
#                 ws.dispatchEvent(event);
#             }
#         }
#         return "";
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.hidden_div('webcam_3'), 'children', allow_duplicate=True),
#     Input(CameraInterfaceAIO.ids.start_stream_btn('webcam_3'), 'n_clicks'),
#     prevent_initial_call=True
# )

# Theme switch
app.clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color-scheme-switch", "id"),
    Input("color-scheme-switch", "checked"),
)

# DAQ WebSocket data handler - simplified version from debug example
app.clientside_callback(
    """
    function(message) {
        if (!message || !message.data) {
            return dash_clientside.no_update;
        }
        
        // Initialize window state
        if (!window.daqState) {
            window.daqState = {
                data: {},
                counter: 0,
                processingBlob: false
            };
        }
        
        // Handle Blob data
        if (message.data instanceof Blob) {
            if (window.daqState.processingBlob) {
                return dash_clientside.no_update;
            }
            
            window.daqState.processingBlob = true;
            
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
                    if (!window.daqState.accumulatedData) {
                        window.daqState.accumulatedData = {};
                        for (const channelName in channelData) {
                            window.daqState.accumulatedData[channelName] = [];
                        }
                    }
                    
                    const maxSamples = 2000;
                    for (const channelName in channelData) {
                        if (!window.daqState.accumulatedData[channelName]) {
                            window.daqState.accumulatedData[channelName] = [];
                        }
                        
                        window.daqState.accumulatedData[channelName] = 
                            window.daqState.accumulatedData[channelName].concat(channelData[channelName]);
                        
                        if (window.daqState.accumulatedData[channelName].length > maxSamples) {
                            window.daqState.accumulatedData[channelName] = 
                                window.daqState.accumulatedData[channelName].slice(-maxSamples);
                        }
                    }
                    
                    window.daqState.data = window.daqState.accumulatedData;
                    window.daqState.counter++;
                    
                    // Update trigger
                    const hiddenDiv = document.getElementById("hidden-daq-data");
                    if (hiddenDiv) {
                        hiddenDiv.textContent = window.daqState.counter.toString();
                    }
                    
                    window.daqState.processingBlob = false;
                    
                } catch (e) {
                    console.error("Error processing DAQ data:", e);
                    window.daqState.processingBlob = false;
                }
            };
            
            reader.readAsArrayBuffer(message.data);
            return window.daqState.counter.toString();
        }
        
        return dash_clientside.no_update;
    }
    """,
    Output("hidden-daq-data", "children"),
    Input("ws-daq", "message")
)

# Graph update callbacks for each plot with per-plot settings
for plot_idx in range(4):
    app.clientside_callback(
        f"""
        function(dataSignal, channelIndices, yScaleMode, yMin, yMax, displaySamples) {{
            // Do not try to get data on window loading
            if (!dataSignal || !window.daqState || !window.daqState.data) {{
                return dash_clientside.no_update;
            }}
            
            const data = window.daqState.data;
            const displaySize = parseInt(displaySamples) || 1000;
            const selectedChannels = channelIndices || [];
            
            if (selectedChannels.length === 0) {{
                // If no channels selected, return empty plot
                return {{
                    'data': [],
                    'layout': {{
                        margin: {{l: 40, b: 40, t: 10, r: 10}},
                        xaxis: {{title: 'Samples', range: [0, displaySize]}},
                        yaxis: {{title: 'Voltage (V)'}},
                        height: 300,
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)'
                    }}
                }};
            }}

            // Set colors for multiple traces
            const colors = ['#1E88E5', '#F44336', '#4CAF50', '#FF9800', '#9C27B0', '#795548', '#607D8B', '#3F51B5'];

            // Create a trace for each selected channel
            const traces = [];
            let dataMin = null;
            let dataMax = null;

            selectedChannels.forEach((channel, i) => {{
                if (data[channel] && data[channel].length > 0) {{
                    const channelData = data[channel];
                    const displayData = channelData.length > displaySize ? 
                        channelData.slice(-displaySize) : channelData;

                    // Create x-axis data
                    const xData = Array.from({{length: displayData.length}}, (_, i) => i);

                    // Update min/max for auto-scaling
                    if (displayData.length > 0) {{
                        const minVal = Math.min(...displayData);
                        const maxVal = Math.max(...displayData);

                        if (dataMin === null || minVal < dataMin) {{
                            dataMin = minVal;
                        }}
                        if (dataMax === null || maxVal > dataMax) {{
                            dataMax = maxVal;
                        }}
                    }}

                    traces.push({{
                        x: xData,
                        y: displayData,
                        mode: 'lines',
                        name: channel.split('/').pop(),
                        line: {{color: colors[i % colors.length], width: 2}}
                    }});
                }}
            }});

            // Create layout
            const layout = {{
                margin: {{l: 40, b: 40, t: 10, r: 10}},
                xaxis: {{
                    title: 'Samples',
                    range: [0, displaySize]
                }},
                yaxis: {{
                    title: 'Voltage (V)'
                }},
                height: 300,
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                legend: {{
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                }},
                showlegend: selectedChannels.length > 1
            }};

            // Apply Y-axis range settings based on mode
            if (yScaleMode === 'manual') {{
                const yMinValue = parseFloat(yMin);
                const yMaxValue = parseFloat(yMax);

                if (!isNaN(yMinValue) && !isNaN(yMaxValue) && yMaxValue > yMinValue) {{
                    layout.yaxis.range = [yMinValue, yMaxValue];
                }} else {{
                    if (dataMin !== null && dataMax !== null) {{
                        const range = dataMax - dataMin;
                        const margin = range * 0.1;
                        layout.yaxis.range = [dataMin - margin, dataMax + margin];
                    }}
                }}
            }} else {{
                if (dataMin !== null && dataMax !== null) {{
                    const range = dataMax - dataMin;
                    const margin = Math.max(range * 0.1, 0.01);
                    layout.yaxis.range = [dataMin - margin, dataMax + margin];
                }}
            }}

            return {{
                'data': traces,
                'layout': layout
            }};
        }}
        """,
        Output({{'type': 'signal-graph', 'index': plot_idx}}, 'figure'),
        Input("hidden-daq-data", "children"),
        Input({{'type': 'channel-selector', 'index': plot_idx}}, 'value'),
        Input({{'type': 'y-scale-mode', 'index': plot_idx}}, 'value'),
        Input({{'type': 'y-min', 'index': plot_idx}}, 'value'),
        Input({{'type': 'y-max', 'index': plot_idx}}, 'value'),
        Input("display-samples-select", "value"),
        prevent_initial_call=True
    )
