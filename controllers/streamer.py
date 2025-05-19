from quart import websocket
from server import webcam_server
import asyncio
import base64
import cv2

import tracemalloc
import os
import psutil


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
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            memory_start = process.memory_info().rss / 1024 / 1024  # MB
            frame_count = 0

            try:
                while True:
                    if not self._camera.streamOn:
                        # If streaming is off, wait a bit and check again
                        await asyncio.sleep(1.0)
                        continue

                    # Streaming is active, get and send frames
                    # if self._camera.framerate is not None:
                    #     await asyncio.sleep(1 / self._camera.framerate)

                    frame = self._camera.get_frame()
                    if frame is not None:
                        # print('STREAMER SIDE: FRAME IS NOT NONE')
                        _, jpeg = cv2.imencode('.jpg', frame)
                        await websocket.send(jpeg.tobytes())
                        frame_count += 1
                        # if frame_count % 30 == 0:  # Check memory every 30 frames
                        #     current, peak = tracemalloc.get_traced_memory()
                        #     memory_current = process.memory_info().rss / 1024 / 1024
                        #     print(
                        #         f"Memory usage: {memory_current:.2f}MB (Python traced: {current / 1024 / 1024:.2f}MB)")
                        #     print(f"Memory increase: {memory_current - memory_start:.2f}MB")
                        #
                        #     # Get top memory consumers
                        #     snapshot = tracemalloc.take_snapshot()
                        #     top_stats = snapshot.statistics('lineno')
                        #     print("[ Top 5 memory consumers ]")
                        #     for stat in top_stats[:5]:
                        #         print(stat)

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