from quart import websocket
from server import webcam_server
import asyncio
import base64
import cv2
from logger_config import get_logger

logger = get_logger(__name__)

# Global registry to track all registered streamers
_registered_streamers = []


class WebcamStreamer:
    def __init__(self, camera, path):
        self._camera = camera
        self._path = path
        self._register_endpoint()
        # Add to global registry
        _registered_streamers.append(self)
        logger.info(f"WebcamStreamer initialized for camera {self._camera.id} on path {self._path}")

    def _register_endpoint(self):
        """Register the websocket route once during initialization"""
        
        @webcam_server.websocket(self._path, endpoint=self._camera.id)
        async def stream_handler():
            logger.info(f'Camera {self._camera.id} WebSocket connected')
            
            # Send an initial ping to establish the connection properly
            try:
                await websocket.send(b'ping')
                logger.debug(f'Camera {self._camera.id} WebSocket ping sent')
            except Exception as e:
                logger.error(f'Camera {self._camera.id} WebSocket ping failed: {e}')

            try:
                while True:
                    if not self._camera.streamOn:
                        # Use a much shorter sleep to avoid blocking other connections
                        await asyncio.sleep(0.1)
                        continue

                    # Streaming is active, get and send frames
                    frame = self._camera.get_frame()
                    if frame is None:
                        logger.debug('Streamer: Frame is None')
                        # If no frame available, wait briefly before retrying
                        await asyncio.sleep(0.1)
                        continue
                        
                    if frame is not None:
                        logger.debug(f'Streamer: Processing frame for camera {self._camera.id}')
                        _, jpeg = cv2.imencode('.jpg', frame)
                        await websocket.send(jpeg.tobytes())
                        jpeg = None
                        
                    await asyncio.sleep(1 / self._camera.framerate)
            except asyncio.CancelledError:
                logger.info(f'Camera {self._camera.id} WebSocket disconnected')
            except Exception as e:
                logger.error(f'Error in stream: {str(e)}')
                import traceback
                traceback.print_exc()
            finally:
                logger.debug(f'Camera {self._camera.id} stream handler exited')

    def stream(self):
        """Start streaming"""
        logger.info(f'Starting camera {self._camera.id} stream')
        self._camera.streamOn = True


def get_registered_streamers():
    """Get list of all registered streamers"""
    return _registered_streamers


def print_streamer_info():
    """Print information about all registered streamers"""
    logger.info(f"Total registered streamers: {len(_registered_streamers)}")
    for i, streamer in enumerate(_registered_streamers):
        logger.info(f"  Streamer {i+1}: Camera {streamer._camera.id} on path {streamer._path}")


# Function to verify all streamers are ready
async def verify_all_streamers_ready():
    """Verify that all WebSocket endpoints are properly registered"""
    logger.info("Verifying WebSocket endpoints are ready...")
    
    # List all registered routes in the webcam_server
    routes = []
    for rule in webcam_server.url_map.iter_rules():
        if rule.websocket:
            routes.append(rule.rule)
    
    logger.info(f"Registered WebSocket routes: {routes}")
    
    for streamer in _registered_streamers:
        if streamer._path in routes:
            logger.info(f"✓ Endpoint {streamer._path} for camera {streamer._camera.id} is registered")
        else:
            logger.warning(f"✗ Endpoint {streamer._path} for camera {streamer._camera.id} is NOT registered")