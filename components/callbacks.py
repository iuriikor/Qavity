from dash import Output, Input, callback, ClientsideFunction, MATCH
from components.CameraInterfaceAIO import CameraInterfaceAIO

from server import app

# # Callback format to write data from the Websocket directly into src of Htmp.Img
# # Bad practice - data transfer in this format eats A LOT of ram very fast
# app.clientside_callback(
#     """
#     function(message) {
#         if (message && message.data) {
#             return message.data;
#         }
#         return "";
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
#     Input("ws1", "message")
# )

# app.clientside_callback(
#     """
#     function(message) {
#         if (message && message.data) {
#             return message.data;
#         }
#         return "";
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
#     Input("ws2", "message")
# )
#

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

                /*
                setTimeout(() => {
                    const ws = document.getElementById("ws1");
                    if (ws && ws._websocket) {
                        ws._websocket.close();

                        setTimeout(() => {
                            const baseUrl = "ws://127.0.0.1:5000/stream1";
                            const newUrl = baseUrl + "?t=" + Date.now();
                            ws.setAttribute("url", newUrl);

                            const event = new Event("dash-prop-change");
                            ws.dispatchEvent(event);
                        }, 200);
                    }
                }, 100); 
                */
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
            
            // Use this code if you want to enforce periodic reconnect
            // Every 300 frames, force reconnection
            if (window.webcam2State.frameCount >= 300) {
                window.webcam2State.frameCount = 0;
                /*
                setTimeout(() => {
                    const ws = document.getElementById("ws2");
                    if (ws && ws._websocket) {
                        ws._websocket.close();

                        setTimeout(() => {
                            const baseUrl = "ws://127.0.0.1:5000/stream2";
                            const newUrl = baseUrl + "?t=" + Date.now();
                            ws.setAttribute("url", newUrl);

                            const event = new Event("dash-prop-change");
                            ws.dispatchEvent(event);
                        }, 200);
                    }
                }, 100);
                */
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

            // Use this code if you want to enforce periodic reconnect
            // Every 300 frames, force reconnection
            if (window.webcam3State.frameCount >= 300) {
                window.webcam3State.frameCount = 0;
                /*
                setTimeout(() => {
                    const ws = document.getElementById("ws2");
                    if (ws && ws._websocket) {
                        ws._websocket.close();

                        setTimeout(() => {
                            const baseUrl = "ws://127.0.0.1:5000/stream3";
                            const newUrl = baseUrl + "?t=" + Date.now();
                            ws.setAttribute("url", newUrl);

                            const event = new Event("dash-prop-change");
                            ws.dispatchEvent(event);
                        }, 200);
                    }
                }, 100);
                */
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

# DAQ WebSocket data handling
app.clientside_callback(
    """
    function(message) {
        if (message && message.data) {
            // Store the WebSocket data in the hidden div
            return message.data;
        }
        return "";
    }
    """,
    Output("hidden-daq-data", "children"),
    Input("ws-daq", "message")
)

app.clientside_callback(
    """
    function(jsonData, channelIndices, yScaleMode, yMin, yMax, displaySamples) {
        if (!jsonData) {
            return dash_clientside.no_update;
        }

        try {
            // Parse the JSON data
            const data = JSON.parse(jsonData);

            // Get the buffer size (number of samples to display)
            const displaySize = parseInt(displaySamples);

            // Plot data for each selected channel
            const traces = [];

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
            selectedChannels.forEach((channel, i) => {
                if (data.data[channel]) {
                    const channelData = data.data[channel];
                    const displayData = channelData.length > displaySize ? 
                        channelData.slice(-displaySize) : channelData;

                    // Create x-axis data (just sample indices)
                    const xData = Array.from({length: displayData.length}, (_, i) => i);

                    traces.push({
                        x: xData,
                        y: displayData,
                        mode: 'lines',
                        name: channel,  // Use last part of channel name
                        line: {color: colors[i % colors.length], width: 2}
                    });
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
                orientation: 'h'},
                showlegend: selectedChannels.length >= 1
            };

            // Apply manual Y-axis range if selected
            if (yScaleMode === 'manual') {
                layout.yaxis.range = [yMin, yMax];
            }

            // Update the graph
            return {
                'data': traces,
                'layout': layout
            };
        } catch (e) {
            console.error("Error updating graph:", e);
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