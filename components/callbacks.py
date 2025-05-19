from dash import Output, Input, callback, ClientsideFunction, MATCH
from components.CameraInterfaceAIO import CameraInterfaceAIO

from server import app

# app.clientside_callback(
#     "function(m){return m? m.data : '';}",
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
#     Input(f"ws1", "message")
# )
# #
# # app.clientside_callback(
# #     "function(m){return m? m.data : '';}",
# #     Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
# #     Input(f"ws2", "message")
# # )

# Direct callback for WebSocket message to image
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

        // Find webcam_1 canvas
        const canvases = document.getElementsByTagName('canvas');
        let canvas = null;
        for (let i = 0; i < canvases.length; i++) {
            if (canvases[i].id.includes('webcam_1')) {
                canvas = canvases[i];
                break;
            }
        }

        if (!canvas) return "";

        try {
            // Increment frame count
            window.webcam1State.frameCount++;

            // Get canvas context
            const ctx = canvas.getContext('2d');

            // Create a blob from the binary message
            const blob = new Blob([message.data], {type: 'image/jpeg'});

            // Clean up previous blob URL
            if (window.webcam1State.prevBlobUrl) {
                URL.revokeObjectURL(window.webcam1State.prevBlobUrl);
            }

            // Create and store new blob URL
            const url = URL.createObjectURL(blob);
            window.webcam1State.prevBlobUrl = url;

            // Load and draw the image
            const img = new Image();
            img.onload = function() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                img.onload = null;
            };

            img.src = url;

            // Every 300 frames, force reconnection
            if (window.webcam1State.frameCount >= 300) {
                window.webcam1State.frameCount = 0;

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
            }

        } catch (e) {
            console.error("Error processing frame:", e);
        }

        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.hidden_div('webcam_1'), "children", allow_duplicate=True),
    Input("ws1", "message"),
    prevent_initial_call=True
)

# # Direct callback for WebSocket message to image
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

        // Find webcam_2 canvas
        const canvases = document.getElementsByTagName('canvas');
        let canvas = null;
        for (let i = 0; i < canvases.length; i++) {
            if (canvases[i].id.includes('webcam_2')) {
                canvas = canvases[i];
                break;
            }
        }

        if (!canvas) return "";

        try {
            // Increment frame count
            window.webcam2State.frameCount++;

            // Get canvas context
            const ctx = canvas.getContext('2d');

            // Create a blob from the binary message
            const blob = new Blob([message.data], {type: 'image/jpeg'});

            // Clean up previous blob URL
            if (window.webcam2State.prevBlobUrl) {
                URL.revokeObjectURL(window.webcam2State.prevBlobUrl);
            }

            // Create and store new blob URL
            const url = URL.createObjectURL(blob);
            window.webcam2State.prevBlobUrl = url;

            // Load and draw the image
            const img = new Image();
            img.onload = function() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                img.onload = null;
            };

            img.src = url;

            // Every 300 frames, force reconnection
            if (window.webcam2State.frameCount >= 300) {
                window.webcam2State.frameCount = 0;

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
            }

        } catch (e) {
            console.error("Error processing frame:", e);
        }

        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.hidden_div('webcam_2'), "children", allow_duplicate=True),
    Input("ws2", "message"),
    prevent_initial_call=True
)


app.clientside_callback(
    """
    function(message) {
        if (message && message.data) {
            return message.data;
        }
        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_3'), "src"),
    Input("ws3", "message")
)
# app.clientside_callback(
#     """
#     // Rate limiting state variables
#     let lastProcessedTime = 0;
#     const MIN_FRAME_INTERVAL = 50;
#
#     function(message) {
#         // Skip if no message
#         if (!message) return "";
#
#         const now = Date.now();
#
#         // Skip this frame if we're processing too fast
#         if (now - lastProcessedTime < MIN_FRAME_INTERVAL) {
#             // Return current src to maintain current image
#             const img = document.getElementById('CameraInterfaceAIO.htmlImg.webcam_1');
#             return img ? img.src : "";
#         }
#
#         // Process frame and update timestamp
#         lastProcessedTime = now;
#
#         // Handle binary data from WebSocket
#         // For dash-extensions WebSocket, binary data is in message itself
#
#         // Create a blob from the binary message
#         const blob = new Blob([message], {type: 'image/jpeg'});
#
#         // Clean up previous blob URL if it exists
#         if (window._prevBlobUrl1) {
#             URL.revokeObjectURL(window._prevBlobUrl1);
#         }
#
#         // Create and store new blob URL
#         const url = URL.createObjectURL(blob);
#         window._prevBlobUrl1 = url;
#
#         return url;
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
#     Input("ws1", "message")
# )
#
# app.clientside_callback(
#     """
#     // Rate limiting state variables
#     let lastProcessedTime = 0;
#     const MIN_FRAME_INTERVAL = 100;
#
#     function(message) {
#         // Skip if no message
#         if (!message) return "";
#
#         const now = Date.now();
#
#         // Skip this frame if we're processing too fast
#         if (now - lastProcessedTime < MIN_FRAME_INTERVAL) {
#             // Return current src to maintain current image
#             const img = document.getElementById('CameraInterfaceAIO.htmlImg.webcam_2');
#             return img ? img.src : "";
#         }
#
#         // Process frame and update timestamp
#         lastProcessedTime = now;
#
#         // Handle binary data from WebSocket
#         // For dash-extensions WebSocket, binary data is in message itself
#
#         // Create a blob from the binary message
#         const blob = new Blob([message], {type: 'image/jpeg'});
#
#         // Clean up previous blob URL if it exists
#         if (window._prevBlobUrl1) {
#             URL.revokeObjectURL(window._prevBlobUrl1);
#         }
#
#         // Create and store new blob URL
#         const url = URL.createObjectURL(blob);
#         window._prevBlobUrl1 = url;
#
#         return url;
#     }
#     """,
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
#     Input("ws2", "message")
# )
#
# app.clientside_callback(
#     """
#     // Rate limiting state variables
#     let lastProcessedTime = 0;
#     const MIN_FRAME_INTERVAL = 100;
#
#     function(message) {
#         // Skip if no message
#         if (!message) return "";
#
#         const now = Date.now();
#
#         // Skip this frame if we're processing too fast
#         if (now - lastProcessedTime < MIN_FRAME_INTERVAL) {
#             // Return current src to maintain current image
#             const img = document.getElementById('CameraInterfaceAIO.htmlImg.webcam_3');
#             return img ? img.src : "";
#         }
#
#         // Process frame and update timestamp
#         lastProcessedTime = now;
#
#         // Handle binary data from WebSocket
#         // For dash-extensions WebSocket, binary data is in message itself
#
#         // Create a blob from the binary message
#         const blob = new Blob([message], {type: 'image/jpeg'});
#
#         // Clean up previous blob URL if it exists
#         if (window._prevBlobUrl1) {
#             URL.revokeObjectURL(window._prevBlobUrl1);
#         }
#
#         // Create and store new blob URL
#         const url = URL.createObjectURL(blob);
#         window._prevBlobUrl1 = url;
#
#         return url;
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


# Webcam connection debug
app.clientside_callback(
    """
    function() {
        // Wait a moment to let things initialize
        setTimeout(() => {
            const ws1 = document.getElementById("ws1");
            const ws2 = document.getElementById("ws2");

            console.log("WebSocket Initialization Check:");
            console.log("ws1:", ws1);
            console.log("ws1._websocket:", ws1 ? ws1._websocket : "N/A");
            console.log("ws1 ready state:", ws1 && ws1._websocket ? ws1._websocket.readyState : "N/A");

            console.log("ws2:", ws2);
            console.log("ws2._websocket:", ws2 ? ws2._websocket : "N/A");
            console.log("ws2 ready state:", ws2 && ws2._websocket ? ws2._websocket.readyState : "N/A");
        }, 2000); // Check after 2 seconds

        return "";
    }
    """,
    Output("hidden_div_clientside", "children"),
    Input("hidden_div_clientside", "id")
)