import threading

import dash_mantine_components as dmc
from server import app, webcam_server
from devices import daq_card
from app import make_layout

if __name__ == '__main__':
    # app.layout = dmc.MantineProvider(app.make_layout())
    # layout = app.make_layout()
    try:
        app.layout = make_layout()
        threading.Thread(target=app.run_server, kwargs={'debug': False, 'use_reloader': False}).start()
        webcam_server.run()
    finally:
        daq_card.close()
