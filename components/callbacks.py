from dash import Output, Input, callback
from components.CameraInterfaceAIO import CameraInterfaceAIO

from server import app

# app.clientside_callback(
#     "function(m){return m? m.data : '';}",
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_1'), "src"),
#     Input(f"ws1", "message")
# )
#
# app.clientside_callback(
#     "function(m){return m? m.data : '';}",
#     Output(CameraInterfaceAIO.ids.htmlImg('webcam_2'), "src"),
#     Input(f"ws2", "message")
# )
