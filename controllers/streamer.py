from quart import websocket
from server import webcam_server
import asyncio
import base64
import cv2


class WebcamStreamer:
    def __init__(self, camera, path):
        self._camera = camera
        self._path = path
        self._register_endpoint()
        print(f"WebcamStreamer initialized for camera {self._camera.id} on path {self._path}")

    def _register_endpoint(self):
        """Register the websocket route once during initialization"""

        @webcam_server.websocket(self._path, endpoint=self._camera.id)
        async def stream_handler():
            print(f'CAMERA {self._camera.id} WEBSOCKET CONNECTED')

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