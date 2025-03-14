import threading

import dash_mantine_components as dmc
from server import app, webcam_server
from app import make_layout

if __name__ == '__main__':
    # app.layout = dmc.MantineProvider(app.make_layout())
    # layout = app.make_layout()
    app.layout = make_layout()
    threading.Thread(target=app.run_server).start()
    # webcam_server.run()

    # print("TERMINATING CONNECTIONS TO HARDWARE")
    # close_app()
