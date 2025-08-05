from quart import websocket
from server import webcam_server
import asyncio
import base64
import cv2


# Global registry to track all registered streamers
_registered_streamers = []


class WebcamStreamer:
    def __init__(self, camera, path):
        self._camera = camera
        self._path = path
        self._register_endpoint()
        # Add to global registry
        _registered_streamers.append(self)
        print(f"WebcamStreamer initialized for camera {self._camera.id} on path {self._path}")

    def _register_endpoint(self):
        """Register the websocket route once during initialization"""
        
        @webcam_server.websocket(self._path, endpoint=self._camera.id)
        async def stream_handler():
            print(f'CAMERA {self._camera.id} WEBSOCKET CONNECTED')
            
            # Send an initial ping to establish the connection properly
            try:
                await websocket.send(b'ping')
                print(f'CAMERA {self._camera.id} WEBSOCKET PING SENT')
            except Exception as e:
                print(f'CAMERA {self._camera.id} WEBSOCKET PING FAILED: {e}')

            try:
                while True:
                    if not self._camera.streamOn:
                        # Use a much shorter sleep to avoid blocking other connections
                        await asyncio.sleep(0.1)
                        continue

                    # Streaming is active, get and send frames
                    frame = self._camera.get_frame()
                    if frame is None:
                        print('STREAMER: FRAME IS NONE')
                        # If no frame available, wait briefly before retrying
                        await asyncio.sleep(0.1)
                        continue
                        
                    if frame is not None:
                        # print('STREAMER SIDE: FRAME IS NOT NONE')
                        _, jpeg = cv2.imencode('.jpg', frame)
                        await websocket.send(jpeg.tobytes())
                        jpeg = None
                        
                    await asyncio.sleep(1 / self._camera.framerate)
            except asyncio.CancelledError:
                print(f'CAMERA {self._camera.id} WEBSOCKET DISCONNECTED')
            except Exception as e:
                print(f'ERROR IN STREAM: {str(e)}')
                import traceback
                traceback.print_exc()
            finally:
                print(f'CAMERA {self._camera.id} STREAM HANDLER EXITED')

    def stream(self):
        """Start streaming"""
        print(f'STARTING CAMERA {self._camera.id} STREAM')
        self._camera.streamOn = True


def get_registered_streamers():
    """Get list of all registered streamers"""
    return _registered_streamers


def print_streamer_info():
    """Print information about all registered streamers"""
    print(f"Total registered streamers: {len(_registered_streamers)}")
    for i, streamer in enumerate(_registered_streamers):
        print(f"  Streamer {i+1}: Camera {streamer._camera.id} on path {streamer._path}")


# Function to verify all streamers are ready
async def verify_all_streamers_ready():
    """Verify that all WebSocket endpoints are properly registered"""
    print("Verifying WebSocket endpoints are ready...")
    
    # List all registered routes in the webcam_server
    routes = []
    for rule in webcam_server.url_map.iter_rules():
        if rule.websocket:
            routes.append(rule.rule)
    
    print(f"Registered WebSocket routes: {routes}")
    
    for streamer in _registered_streamers:
        if streamer._path in routes:
            print(f"✓ Endpoint {streamer._path} for camera {streamer._camera.id} is registered")
        else:
            print(f"✗ Endpoint {streamer._path} for camera {streamer._camera.id} is NOT registered")