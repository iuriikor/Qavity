import threading
import asyncio
import cherrypy
from hypercorn.config import Config
from hypercorn.asyncio import serve as hypercorn_serve

import dash_mantine_components as dmc
from server import app, webcam_server, dash_server
from devices import daq_card
from app import make_layout

if __name__ == '__main__':
    try:
        # Initialize Dash app
        app.layout = make_layout()

        # Configure CherryPy for the Dash app
        def start_cherrypy():
            # CherryPy configuration
            cherrypy_config = {
                'server.socket_host': '127.0.0.1',
                'server.socket_port': 8050,
                'server.thread_pool': 4,  # Adjust based on expected concurrent users
                'engine.autoreload.on': False,  # Disable autoreload for production
                'log.screen': True,  # Show logs on console
                'log.access_file': '',
                'log.error_file': '',
                'response.timeout': 3600,  # Long timeout for dashboard sessions (1 hour)
            }

            # Apply configuration
            cherrypy.config.update(cherrypy_config)

            # Mount the Flask app
            cherrypy.tree.graft(dash_server, '/')

            # Start CherryPy engine
            print(f"Starting CherryPy server on {cherrypy_config["server.socket_host"]}:{cherrypy_config["server.socket_port"]}")
            cherrypy.engine.start()


        # Configure Hypercorn for the WebSocket server
        async def start_hypercorn():
            # Hypercorn configuration
            config = Config()
            config.bind = ["127.0.0.1:5000"]  # Standard port for Quart
            config.use_reloader = False  # Disable reloader for production
            config.workers = 2  # Single worker is usually sufficient for WebSockets
            config.keep_alive_timeout = 120  # 2 minutes keep-alive
            config.websocket_ping_interval = 30  # Send ping every 30 seconds
            config.websocket_timeout = 300  # 5 minutes timeout for WebSockets

            # Start Hypercorn with Quart
            print(f"Starting Hypercorn WebSocket server on {config.bind}")
            await hypercorn_serve(webcam_server, config)


        # Start CherryPy in a separate thread
        cherrypy_thread = threading.Thread(target=start_cherrypy)
        cherrypy_thread.daemon = True
        cherrypy_thread.start()

        # Run Hypercorn in the main thread
        # We use asyncio.run which handles the event loop for us
        asyncio.run(start_hypercorn())

    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up resources
        print("Stopping CherryPy server...")
        if cherrypy.engine.state in (cherrypy.engine.states.STARTED, cherrypy.engine.states.STARTING):
            cherrypy.engine.stop()

        print("Closing DAQ resources...")
        daq_card.close()

        print("Servers stopped, all resources released.")