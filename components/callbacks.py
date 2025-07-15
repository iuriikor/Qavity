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

# DAQ WebSocket data handling - Fixed to properly handle Blob data
app.clientside_callback(
    """
    function(message) {
        if (!message || !message.data) {
            return dash_clientside.no_update;
        }

        try {
            // Initialize window state if it doesn't exist
            if (!window.daqState) {
                window.daqState = {
                    data: {},
                    counter: 0,
                    processingBlob: false,
                    timing: {
                        receiveTimes: [],
                        processingTimes: [],
                        lastReceiveTime: performance.now()
                    }
                };
            }

            // If we're a Blob, process it immediately
            if (message.data instanceof Blob) {
                // Track receive time with safety checks
                if (window.daqState.timing) {
                    const receiveTime = performance.now();
                    const timeSinceLastReceive = receiveTime - window.daqState.timing.lastReceiveTime;
                    window.daqState.timing.receiveTimes.push(timeSinceLastReceive);
                    window.daqState.timing.lastReceiveTime = receiveTime;
                    
                    // Keep only last 100 measurements
                    if (window.daqState.timing.receiveTimes.length > 100) {
                        window.daqState.timing.receiveTimes = window.daqState.timing.receiveTimes.slice(-100);
                    }
                }
                
                // Avoid processing multiple Blobs simultaneously
                if (window.daqState.processingBlob) {
                    return dash_clientside.no_update;
                }

                window.daqState.processingBlob = true;

                // Convert Blob to ArrayBuffer using FileReader
                const reader = new FileReader();

                reader.onload = function() {
                    try {
                        const processingStartTime = performance.now();
                        
                        // Now we have an ArrayBuffer
                        const buffer = reader.result;

                        // Create a DataView to read from the buffer
                        const view = new DataView(buffer);

                        // Parse the binary format according to the protocol
                        let offset = 0;

                        // Read timestamp (8 bytes double)
                        const timestamp = view.getFloat64(offset, false); // false = big-endian
                        offset += 8;

                        // Read number of channels (4 bytes int)
                        const numChannels = view.getInt32(offset, false);
                        offset += 4;

                        if (window.daqState.counter < 3) {
                            console.log("From Blob - Timestamp:", timestamp, "Number of channels:", numChannels);
                        }

                        // Prepare data object
                        const channelData = {};

                        // Read each channel's data
                        for (let i = 0; i < numChannels; i++) {
                            // Check if we're still within buffer bounds
                            if (offset + 4 > buffer.byteLength) {
                                console.error("Buffer overrun at channel name length");
                                break;
                            }

                            // Read channel name length (4 bytes int)
                            const nameLength = view.getInt32(offset, false);
                            offset += 4;

                            // Check if we have enough bytes for the name
                            if (offset + nameLength > buffer.byteLength) {
                                console.error("Buffer overrun at channel name");
                                break;
                            }

                            // Read channel name as UTF-8 string
                            const nameBytes = new Uint8Array(buffer, offset, nameLength);
                            const channelName = new TextDecoder('utf-8').decode(nameBytes);
                            offset += nameLength;

                            // Check if we have enough bytes for the data length
                            if (offset + 4 > buffer.byteLength) {
                                console.error("Buffer overrun at data length");
                                break;
                            }

                            // Read data length (4 bytes int)
                            const dataLength = view.getInt32(offset, false);
                            offset += 4;

                            // Check if we have enough bytes for the data values
                            if (offset + (dataLength * 8) > buffer.byteLength) {
                                console.error(`Buffer overrun at data values for ${channelName}. Need ${dataLength * 8} bytes, have ${buffer.byteLength - offset}`);
                                break;
                            }

                            // Read data values (array of 8-byte doubles)
                            const values = [];
                            for (let j = 0; j < dataLength; j++) {
                                values.push(view.getFloat64(offset, false));
                                offset += 8;
                            }

                            // Store channel data
                            channelData[channelName] = values;

                            if (window.daqState.counter < 3 && i === 0) {
                                console.log(`Channel: ${channelName}, Length: ${values.length}, First value: ${values[0]}`);
                            }
                        }

                        // Accumulate data instead of overwriting
                        if (!window.daqState.accumulatedData) {
                            window.daqState.accumulatedData = {};
                            // Initialize accumulated data for each channel
                            for (const channelName in channelData) {
                                window.daqState.accumulatedData[channelName] = [];
                            }
                        }
                        
                        // Append new data to accumulated data
                        const maxAccumulatedSamples = 10000; // Keep last 10k samples per channel
                        for (const channelName in channelData) {
                            if (!window.daqState.accumulatedData[channelName]) {
                                window.daqState.accumulatedData[channelName] = [];
                            }
                            
                            // Append new data
                            window.daqState.accumulatedData[channelName] = 
                                window.daqState.accumulatedData[channelName].concat(channelData[channelName]);
                            
                            // Trim to max length
                            if (window.daqState.accumulatedData[channelName].length > maxAccumulatedSamples) {
                                window.daqState.accumulatedData[channelName] = 
                                    window.daqState.accumulatedData[channelName].slice(-maxAccumulatedSamples);
                            }
                        }
                        
                        // Store both current chunk and accumulated data
                        window.daqState.data = window.daqState.accumulatedData;
                        window.daqState.currentChunk = channelData;
                        window.daqState.timestamp = timestamp;
                        window.daqState.counter++;
                        
                        // Track processing time with safety checks
                        if (window.daqState.timing) {
                            const processingTime = performance.now() - processingStartTime;
                            window.daqState.timing.processingTimes.push(processingTime);
                            
                            // Keep only last 100 measurements
                            if (window.daqState.timing.processingTimes.length > 100) {
                                window.daqState.timing.processingTimes = window.daqState.timing.processingTimes.slice(-100);
                            }
                        }

                        // Debug logging with timing information
                        if (window.daqState.counter % 50 === 0) {
                            console.log("DAQ data update #" + window.daqState.counter);
                            console.log("Channels:", Object.keys(channelData));
                            
                            // Calculate timing averages with safety checks
                            if (window.daqState.timing && 
                                window.daqState.timing.receiveTimes && 
                                window.daqState.timing.processingTimes &&
                                window.daqState.timing.receiveTimes.length > 0 && 
                                window.daqState.timing.processingTimes.length > 0) {
                                try {
                                    const avgReceiveInterval = window.daqState.timing.receiveTimes.reduce((a, b) => a + b, 0) / window.daqState.timing.receiveTimes.length;
                                    const avgProcessingTime = window.daqState.timing.processingTimes.reduce((a, b) => a + b, 0) / window.daqState.timing.processingTimes.length;
                                    
                                    console.log(`Timing: Receive interval: ${avgReceiveInterval.toFixed(2)}ms, Processing: ${avgProcessingTime.toFixed(2)}ms`);
                                } catch (timingError) {
                                    console.warn("Error calculating timing averages:", timingError);
                                }
                            }
                            
                            // Check memory usage to help diagnose memory leaks
                            if (window.performance && window.performance.memory) {
                                const memory = window.performance.memory;
                                console.log(`Memory: Used heap: ${(memory.usedJSHeapSize / (1024 * 1024)).toFixed(2)} MB, ` + 
                                          `Total heap: ${(memory.totalJSHeapSize / (1024 * 1024)).toFixed(2)} MB, ` +
                                          `Heap limit: ${(memory.jsHeapSizeLimit / (1024 * 1024)).toFixed(2)} MB`);
                            }
                        }

                        // Find and update the hidden div to trigger the graph update
                        const hiddenDiv = document.getElementById("hidden-daq-data");
                        if (hiddenDiv) {
                            hiddenDiv.textContent = window.daqState.counter.toString();
                            if (window.daqState.counter % 10 === 0) {
                                console.log(`Hidden div updated: counter ${window.daqState.counter}`);
                            }
                        } else {
                            if (window.daqState.counter % 50 === 0) {
                                console.error("Hidden div 'hidden-daq-data' not found!");
                            }
                        }

                        // We're done processing this Blob
                        window.daqState.processingBlob = false;

                    } catch (e) {
                        console.error("Error processing Blob data:", e);
                        window.daqState.processingBlob = false;
                    }
                };

                reader.onerror = function() {
                    console.error("FileReader error:", reader.error);
                    window.daqState.processingBlob = false;
                };

                // Start reading the Blob as an ArrayBuffer
                reader.readAsArrayBuffer(message.data);

                // Return the current counter value - graphs will update when FileReader finishes
                return window.daqState.counter.toString();
            }
        } catch (e) {
            console.error("Error processing DAQ data:", e);
            console.error("Error details:", e.stack);
            return dash_clientside.no_update;
        }
    }
    """,
    Output("hidden-daq-data", "children"),
    Input("ws-daq", "message")
)

# Fixed Graph update callback with proper Y-scale handling
# Create four separate callbacks, one for each plot
# In the JavaScript callback, add more comprehensive debugging:
for plot_idx in range(4):
    app.clientside_callback(
        f"""
        function(dataSignal, channelIndices, yScaleMode, yMin, yMax, displaySamples, plotConfigStore) {{
            // Do not try to get data on window loading
            if (!dataSignal || !window.daqState || !window.daqState.data) {{
                // console.log(`Plot {plot_idx} early return - no data yet`);
                return dash_clientside.no_update;
            }}
            
            // Initialize plot state tracking
            if (!window.plotState) {{
                window.plotState = {{}};
            }}
            if (!window.plotState.plot_{plot_idx}) {{
                window.plotState.plot_{plot_idx} = {{
                    lastUpdate: 0,
                    lastDataLength: 0,
                    lastConfig: null,
                    lastDataCounter: 0
                }};
            }}
            
            // Get current time and plot state
            const now = Date.now();
            const plotState = window.plotState.plot_{plot_idx};

            try {{
                // Get the channel data from window.daqState
                const data = window.daqState.data;

                // Get plot configuration for this specific plot
                let plotConfig = {{}};
                if (plotConfigStore && 
                    plotConfigStore.plots && 
                    Array.isArray(plotConfigStore.plots) &&
                    plotConfigStore.plots[{plot_idx}]) {{

                    plotConfig = plotConfigStore.plots[{plot_idx}];
                    // console.log(`Plot {plot_idx} config loaded:`, plotConfig);
                }} else {{
                    // console.log(`Plot {plot_idx} no config found, using defaults`);
                }}

                // Extract configuration values with defaults
                const legendStrings = plotConfig.legend_strings || [];
                const plotWidth = plotConfig.width || 800;  // Default width
                const plotHeight = plotConfig.height || 300; // Default height


                // Get the buffer size (number of samples to display)
                const displaySize = parseInt(displaySamples) || 1000;

                // Get the selected channels
                const selectedChannels = channelIndices || [];
                
                // Check if data has actually changed
                const currentDataLength = Object.keys(data).length > 0 ? Object.values(data)[0].length : 0;
                const configString = JSON.stringify({{channelIndices, yScaleMode, yMin, yMax, displaySamples}});
                
                // Use DAQ counter as a better indicator of new data
                const currentDataCounter = window.daqState.counter || 0;
                
                // Check if we need a full recreation vs just data update
                const needsFullRecreation = (
                    plotState.lastConfig !== configString ||  // Config changed
                    selectedChannels.length === 0 ||          // No channels
                    !plotState.lastDataCounter               // First time
                );
                
                // If configuration changed, always update
                if (needsFullRecreation) {{
                    plotState.lastUpdate = now;
                    plotState.lastDataLength = currentDataLength;
                    plotState.lastConfig = configString;
                    plotState.lastDataCounter = currentDataCounter;
                    // Continue to create new plot
                }} else {{
                    // For data-only updates, use counter to detect changes
                    if (currentDataCounter === plotState.lastDataCounter) {{
                        // No new data received
                        return dash_clientside.no_update;
                    }}
                    
                    // Debug: Log plot updates occasionally
                    if (currentDataCounter % 10 === 0) {{
                        console.log(`Plot {plot_idx}: Counter ${{currentDataCounter}}, last update ${{now - plotState.lastUpdate}}ms ago`);
                    }}
                    
                    // Minimal throttling - allow updates every 10ms (100 Hz max)
                    if (now - plotState.lastUpdate < 10) {{
                        return dash_clientside.no_update;
                    }}
                    
                    // Update tracking state
                    plotState.lastUpdate = now;
                    plotState.lastDataLength = currentDataLength;
                    plotState.lastConfig = configString;
                    plotState.lastDataCounter = currentDataCounter;
                }}

                if (selectedChannels.length === 0) {{
                    // If no channels selected, return empty plot with configured dimensions
                    return {{
                        'data': [],
                        'layout': {{
                            margin: {{l: 40, b: 40, t: 10, r: 10}},
                            xaxis: {{title: 'Samples', range: [0, displaySize]}},
                            yaxis: {{title: 'Voltage (V)'}},
                            height: plotHeight,  // Use configured height
                            width: plotWidth,    // Use configured width
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

                        // Use legend string if available, otherwise use channel name
                        let displayName = channel;
                        if (Array.isArray(legendStrings) && i < legendStrings.length && legendStrings[i]) {{
                            displayName = legendStrings[i];
                            // console.log(`Plot {plot_idx} using custom legend: "${{displayName}}" for channel: ${{channel}}`);
                        }}

                        traces.push({{
                            x: xData,
                            y: displayData,
                            mode: 'lines',
                            name: displayName,
                            line: {{color: colors[i % colors.length], width: 2}}
                        }});
                    }} else {{
                        // console.log(`Plot {plot_idx} Channel ${{channel}} not found or empty in data`);
                    }}
                }});

                // Create layout with configured dimensions
                const layout = {{
                    margin: {{l: 40, b: 40, t: 10, r: 10}},
                    xaxis: {{
                        title: 'Samples',
                        range: [0, displaySize]
                    }},
                    yaxis: {{
                        title: 'Voltage (V)'
                    }},
                    height: plotHeight,  // Use configured height
                    width: plotWidth,    // Use configured width
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    legend: {{
                        x: 0,
                        y: 1.1,
                        orientation: 'h'
                    }},
                    showlegend: selectedChannels.length >= 1
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
            }} catch (e) {{
                console.error(`Error updating graph for plot {plot_idx}:`, e);
                return dash_clientside.no_update;
            }}
        }}
        """,
        Output({'type': 'signal-graph', 'index': plot_idx}, 'figure'),
        Input("hidden-daq-data", "children"),
        Input({'type': 'channel-selector', 'index': plot_idx}, 'value'),
        Input({'type': 'y-scale-mode', 'index': plot_idx}, 'value'),
        Input({'type': 'y-min', 'index': plot_idx}, 'value'),
        Input({'type': 'y-max', 'index': plot_idx}, 'value'),
        Input({'type': 'display-samples', 'index': plot_idx}, 'value'),
        Input("plot-config-store", "data")
    )