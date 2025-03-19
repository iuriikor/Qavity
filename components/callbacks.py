from dash import Output, Input, callback
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
app.clientside_callback(
    """
    function(message) {
        if (message && message.data) {
            return message.data;
        }
        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
    Input("ws1", "message")
)

# Direct callback for WebSocket message to image
app.clientside_callback(
    """
    function(message) {
        if (message && message.data) {
            return message.data;
        }
        return "";
    }
    """,
    Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
    Input("ws2", "message")
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

# Callback to force WebSocket reconnection when Start is clicked
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Force WebSocket reconnection
            const ws = document.getElementById("ws1");
            if (ws) {
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
            if (ws) {
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
            if (ws) {
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