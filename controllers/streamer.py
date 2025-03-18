from quart import websocket
from server import webcam_server
import asyncio
import base64
import cv2

class WebcamStreamer:
    def __init__(self, camera, path):
        self._camera = camera
        self._path = path

    def stream(self):
        print('ENTERING STREAM FUNCTION')
        @webcam_server.websocket(self._path, endpoint=self._camera.id)
        async def stream_start():
            print('CAMERA STARTING STREAM')
            self._camera.start_stream()
            print('ENTERING STREAMER LOOP')
            while True:
                if self._camera.framerate is not None:
                    await asyncio.sleep(1/self._camera.framerate)  # add delay if CPU usage is too high
                frame = self._camera.get_frame()
                print('FRAME RECEIVED')
                if frame is not None:
                    _, jpeg = cv2.imencode('.jpg', frame)
                    await websocket.send(f"data:image/jpeg;base64, {base64.b64encode(jpeg.tobytes()).decode()}")
                if not self._camera.streamOn:
                    break
