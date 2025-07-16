from quart import Quart
import asyncio
import json
import numpy as np
import time
import struct
import logging
from fake_device import FakeDAQDevice

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FakeDAQStreamer:
    def __init__(self, device, quart_app, path, update_rate=20):
        self.device = device
        self._quart_app = quart_app
        self._path = path
        self.update_rate = update_rate
        self.streaming = False
        self.buffer_size = 20000
        self.data_buffer = {}
        
        # Initialize data buffer for each channel
        for channel in self.device.channels:
            self.data_buffer[channel] = []
        
        # Register the websocket endpoint
        self._register_endpoint()
        
        logger.info(f"FakeDAQStreamer initialized with {len(self.device.channels)} channels, update_rate: {update_rate}Hz")
    
    def _register_endpoint(self):
        """Register the websocket route for DAQ data streaming"""
        
        @self._quart_app.websocket(self._path)
        async def stream_handler():
            from quart import websocket
            logger.info(f"WebSocket connection established on {self._path}")
            
            try:
                await self.stream_data(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                logger.info("WebSocket connection closed")
        
        logger.info(f"WebSocket endpoint registered at {self._path}")
    
    def start(self):
        """Start streaming"""
        if not self.device.is_initialized:
            logger.error("Device not initialized")
            return False
        
        # Clear buffers
        for channel in self.device.channels:
            self.data_buffer[channel] = []
        
        success = self.device.start()
        if success:
            self.streaming = True
            logger.info("FakeDAQStreamer started")
        return success
    
    def stop(self):
        """Stop streaming"""
        self.streaming = False
        success = self.device.stop()
        logger.info("FakeDAQStreamer stopped")
        return success
    
    async def stream_data(self, websocket):
        """Stream data via websocket"""
        logger.info("Starting websocket data stream")
        
        samples_per_read = 100
        
        # Keep WebSocket connection alive, only stream data when streaming is enabled
        try:
            while True:
                if self.streaming:
                    try:
                        start_time = time.time()
                        
                        # Calculate sleep time based on current update rate
                        sleep_time = 1.0 / self.update_rate
                        
                        # Read data from device
                        current_data = np.zeros((len(self.device.channels), samples_per_read))
                        success = self.device.read_data(current_data, samples_per_read)
                        
                        if success:
                            # Update circular buffer
                            for i, channel in enumerate(self.device.channels):
                                self.data_buffer[channel].extend(current_data[i, :].tolist())
                                
                                # Keep buffer size manageable
                                if len(self.data_buffer[channel]) > self.buffer_size:
                                    self.data_buffer[channel] = self.data_buffer[channel][-self.buffer_size:]
                            
                            # Prepare data for transmission (binary format)
                            current_time = time.time()
                            
                            # Send recent data (not entire buffer)
                            samples_to_send = min(200, samples_per_read)
                            
                            # Create binary data
                            binary_data = struct.pack('!di', current_time, len(self.device.channels))
                            
                            for channel in self.device.channels:
                                if len(self.data_buffer[channel]) > 0:
                                    # Get recent data
                                    recent_data = self.data_buffer[channel][-samples_to_send:]
                                    
                                    # Channel name
                                    name_bytes = channel.encode('utf-8')
                                    binary_data += struct.pack('!i', len(name_bytes))
                                    binary_data += name_bytes
                                    
                                    # Data
                                    binary_data += struct.pack('!i', len(recent_data))
                                    binary_data += struct.pack('!' + 'd' * len(recent_data), *recent_data)
                            
                            # Send data
                            await websocket.send(binary_data)
                            
                            # Log performance occasionally
                            if int(time.time()) % 5 == 0 and time.time() - int(time.time()) < 0.1:
                                processing_time = time.time() - start_time
                                logger.info(f"Data sent: {len(binary_data)} bytes, processing time: {processing_time*1000:.1f}ms, update_rate: {self.update_rate}Hz")
                        
                        # Sleep to maintain update rate
                        await asyncio.sleep(sleep_time)
                        
                    except Exception as e:
                        logger.error(f"Error in stream_data: {e}")
                        await asyncio.sleep(0.1)
                else:
                    # Not streaming, just wait a bit
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        
        logger.info("Websocket data stream ended")