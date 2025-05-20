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

app.clientside_callback(
    """
    function(message) {
        if (!message) return "";

        // Initialize window state if not exists
        if (!window.webcam3State) {
            window.webcam3State = {
                frameCount: 0,
                prevBlobUrl: null
            };
        }

        try {
            // Increment frame count
            window.webcam3State.frameCount++;

            // Create a blob from the binary message
            const blob = new Blob([message.data], {type: 'image/jpeg'});

            // Clean up previous blob URL
            if (window.webcam3State.prevBlobUrl) {
                URL.revokeObjectURL(window.webcam3State.prevBlobUrl);
            }

            // Create and store new blob URL
            const url = URL.createObjectURL(blob);
            window.webcam3State.prevBlobUrl = url;

            // Every 300 frames, force reconnection
            if (window.webcam3State.frameCount >= 300) {
                window.webcam3State.frameCount = 0;
            }

            return url;
        } catch (e) {
            console.error("Error processing frame:", e);
            return "";
        }
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_3'), "src"),
    Input("ws3", "message")
)

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

# Callback to force WebSocket reconnection when Start is clicked
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Force WebSocket reconnection
            const ws = document.getElementById("ws3");
            if (ws && ws._websocket) {
                ws._websocket.close();
                // Create a new URL with timestamp to force reconnection
                const baseUrl = "ws://127.0.0.1:5000/stream3";
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
    Output(CameraInterfaceAIO.ids.hidden_div('webcam_3'), 'children', allow_duplicate=True),
    Input(CameraInterfaceAIO.ids.start_stream_btn('webcam_3'), 'n_clicks'),
    prevent_initial_call=True
)

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
                    processingBlob: false
                };
            }

            // If we're a Blob, process it immediately
            if (message.data instanceof Blob) {
                // Avoid processing multiple Blobs simultaneously
                if (window.daqState.processingBlob) {
                    return dash_clientside.no_update;
                }

                window.daqState.processingBlob = true;

                // Convert Blob to ArrayBuffer using FileReader
                const reader = new FileReader();

                reader.onload = function() {
                    try {
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

                        // Store parsed data
                        window.daqState.data = channelData;
                        window.daqState.timestamp = timestamp;
                        window.daqState.counter++;

                        // Debug logging
                        if (window.daqState.counter % 100 === 0) {
                            console.log("DAQ data update #" + window.daqState.counter);
                            console.log("Channels:", Object.keys(channelData));

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
app.clientside_callback(
    """
    function(dataSignal, channelIndices, yScaleMode, yMin, yMax, displaySamples) {
        if (!dataSignal || !window.daqState || !window.daqState.data) {
            return dash_clientside.no_update;
        }

        try {
            // Get the channel data from window.daqState
            const data = window.daqState.data;

            // Debug output for first few graph updates
            if (parseInt(dataSignal) < 5) {
                console.log("Graph update triggered with dataSignal:", dataSignal);
                console.log("Available channels:", Object.keys(data));
                if (Object.keys(data).length > 0) {
                    const firstChannel = Object.keys(data)[0];
                    console.log("First channel data length:", data[firstChannel].length);
                }
                console.log("Selected channels:", channelIndices);
            }

            // Get the buffer size (number of samples to display)
            const displaySize = parseInt(displaySamples) || 1000;  // Default if parsing fails

            // Get the selected channels
            const selectedChannels = channelIndices || [];

            if (selectedChannels.length === 0) {
                // If no channels selected, return empty plot
                return {
                    'data': [],
                    'layout': {
                        margin: {l: 40, b: 40, t: 10, r: 10},
                        xaxis: {title: 'Samples', range: [0, displaySize]},
                        yaxis: {title: 'Voltage (V)'},
                        height: 300,
                        width: 800,
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)'
                    }
                };
            }

            // Set colors for multiple traces
            const colors = ['#1E88E5', '#F44336', '#4CAF50', '#FF9800', '#9C27B0', '#795548', '#607D8B', '#3F51B5'];

            // Create a trace for each selected channel
            const traces = [];

            // Keep track of min/max values for auto y-axis
            let dataMin = null;
            let dataMax = null;

            selectedChannels.forEach((channel, i) => {
                if (data[channel]) {
                    const channelData = data[channel];
                    const displayData = channelData.length > displaySize ? 
                        channelData.slice(-displaySize) : channelData;

                    // Create x-axis data (just sample indices)
                    const xData = Array.from({length: displayData.length}, (_, i) => i);

                    // Update min/max for auto-scaling
                    if (displayData.length > 0) {
                        const minVal = Math.min(...displayData);
                        const maxVal = Math.max(...displayData);

                        if (dataMin === null || minVal < dataMin) {
                            dataMin = minVal;
                        }
                        if (dataMax === null || maxVal > dataMax) {
                            dataMax = maxVal;
                        }
                    }

                    traces.push({
                        x: xData,
                        y: displayData,
                        mode: 'lines',
                        name: channel,
                        line: {color: colors[i % colors.length], width: 2}
                    });
                } else {
                    // Log if channel doesn't exist
                    if (parseInt(dataSignal) < 5) {
                        console.warn(`Channel ${channel} not found in data`);
                    }
                }
            });

            // Create layout with y-axis settings
            const layout = {
                margin: {l: 40, b: 40, t: 10, r: 10},
                xaxis: {
                    title: 'Samples',
                    range: [0, displaySize]
                },
                yaxis: {
                    title: 'Voltage (V)'
                },
                height: 300,
                width: 800,
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                legend: {
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                },
                showlegend: selectedChannels.length >= 1
            };

            // Apply Y-axis range settings based on mode
            if (yScaleMode === 'manual') {
                // Convert input values to numbers and validate
                const yMinValue = parseFloat(yMin);
                const yMaxValue = parseFloat(yMax);

                // Debug Y-axis settings
                console.log("Manual Y scale requested:", yMinValue, yMaxValue);

                // Check if values are valid numbers and yMax > yMin
                if (!isNaN(yMinValue) && !isNaN(yMaxValue) && yMaxValue > yMinValue) {
                    layout.yaxis.range = [yMinValue, yMaxValue];
                    console.log("Setting manual Y range:", yMinValue, yMaxValue);
                } else {
                    // If invalid, fallback to auto with extra margin
                    console.warn("Invalid Y scale values, using auto scaling");
                    if (dataMin !== null && dataMax !== null) {
                        const range = dataMax - dataMin;
                        const margin = range * 0.1;  // 10% margin
                        layout.yaxis.range = [dataMin - margin, dataMax + margin];
                    }
                }
            } else {
                // Auto scaling with a margin
                if (dataMin !== null && dataMax !== null) {
                    const range = dataMax - dataMin;
                    const margin = Math.max(range * 0.1, 0.01);  // At least 0.01V margin
                    layout.yaxis.range = [dataMin - margin, dataMax + margin];
                }
            }

            // Update the graph
            return {
                'data': traces,
                'layout': layout
            };
        } catch (e) {
            console.error("Error updating graph:", e);
            console.error("Graph error details:", e.stack);
            return dash_clientside.no_update;
        }
    }
    """,
    Output({'type': 'signal-graph', 'index': MATCH}, 'figure'),
    Input("hidden-daq-data", "children"),
    Input({'type': 'channel-selector', 'index': MATCH}, 'value'),
    Input({'type': 'y-scale-mode', 'index': MATCH}, 'value'),
    Input({'type': 'y-min', 'index': MATCH}, 'value'),
    Input({'type': 'y-max', 'index': MATCH}, 'value'),
    Input({'type': 'display-samples', 'index': MATCH}, 'value')
)