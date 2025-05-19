import threading

import dash_mantine_components as dmc
from server import app, webcam_server
from devices import daq_card
from app import make_layout
from waitress import serve

# def run_app():
#     try:
#         app.layout = make_layout()
#         threading.Thread(target=app.run_server, kwargs={'debug': False, 'use_reloader': False}).start()
#         webcam_server.run()
#     finally:
#         daq_card.close()
if __name__ == '__main__':
    # app.layout = dmc.MantineProvider(app.make_layout())
    # layout = app.make_layout()
    try:
        app.layout = make_layout()
        print("Starting Dash server...")
        threading.Thread(target=app.run_server, kwargs={'debug': False, 'use_reloader': False}).start()
        print("Starting Quart server...")
        # serve(app.server, host="127.0.0.1", port=8050)

        # Add this to see when the Quart server is actually ready
        @webcam_server.before_serving
        async def startup():
            print("Quart server is starting up - registered endpoints:")
            for rule in webcam_server.url_map.iter_rules():
                print(f"  {rule.endpoint}: {rule.rule}")
        webcam_server.run()
    finally:
        daq_card.close()
