from quart import websocket
from server import webcam_server
import asyncio
import json
import numpy
import time
from controllers.utils.CircularBuffer import CircularBuffer
import struct


class DAQDataStreamer:
    def __init__(self, daq, path, sampling_rate=1000, buffer_size=20000, update_rate=10):
        self._daq = daq
        self._path = path
        self._sampling_rate = sampling_rate  # 1 kS/s default
        self._update_rate = update_rate  # 10 Hz default
        self._buffer_size = buffer_size  # 20 kS default
        self._streaming = False

        # Initialize the circular buffer
        self._buffer = CircularBuffer(max_size=self._buffer_size)

        # Add all channels to the buffer
        for channel in self._daq.channels:
            self._buffer.add_channel(channel)

        self._register_endpoint()
        print(f"DAQDataStreamer initialized on path {self._path} with {len(self._daq.channels)} channels")
        print(
            f"Sampling rate: {self._sampling_rate} Hz, Buffer size: {self._buffer_size} samples, Update rate: {self._update_rate} Hz")

    def _register_endpoint(self):
        """Register the websocket route for DAQ data streaming"""

        @webcam_server.websocket(self._path)
        async def stream_handler():
            print(f'DAQ WEBSOCKET CONNECTED')

            # Task for high-frequency data acquisition
            acquisition_task = None

            try:
                # Define the data acquisition coroutine
                async def acquire_data():
                    samples_per_read = 200  # Read 100 samples at a time for efficiency
                    sleep_time = 1.0 / self._update_rate

                    while self._streaming:
                        # Read data from DAQ
                        current_data = numpy.zeros((len(self._daq.channels), samples_per_read))
                        success = self._daq.read_data(current_data, samples_per_read)

                        if success:
                            # Add data to circular buffer for each channel
                            data_dict = {}
                            for i, channel in enumerate(self._daq.channels):
                                data_dict[channel] = current_data[i, :].tolist()

                            # Update the buffer
                            self._buffer.add_data(data_dict)

                        # Sleep to maintain the sampling rate
                        await asyncio.sleep(sleep_time)

                # Define frontend update coroutine - using binary format
                async def update_frontend():
                    update_interval = 1.0 / self._update_rate  # 10 Hz update rate

                    while self._streaming:
                        try:
                            # Get all data from the buffer
                            buffer_data = self._buffer.get_data()

                            # Get timestamp
                            current_time = time.time()

                            # Start with timestamp and number of channels
                            binary_data = struct.pack('!di', current_time, len(buffer_data))

                            # Add each channel's data - limit to 1000 samples per channel to reduce size
                            for channel_name, data in buffer_data.items():
                                # Limit to last 10000 samples to reduce data size
                                limited_data = data[-10000:] if len(data) > 10000 else data

                                # Channel name
                                name_bytes = channel_name.encode('utf-8')
                                binary_data += struct.pack('!i', len(name_bytes))
                                binary_data += name_bytes

                                # Data length and values
                                binary_data += struct.pack('!i', len(limited_data))
                                # Pack all data values at once
                                binary_data += struct.pack('!' + 'd' * len(limited_data), *limited_data)

                            # Send binary data to frontend
                            await websocket.send(binary_data)

                        except Exception as e:
                            print(f"Error in update_frontend: {e}")
                            import traceback
                            traceback.print_exc()

                        # Sleep to maintain update rate
                        await asyncio.sleep(update_interval)

                # Main websocket loop
                while True:
                    if not self._streaming:
                        # If streaming is off, wait and check again
                        await asyncio.sleep(0.5)
                        continue

                    # Start data acquisition task if not already running
                    if acquisition_task is None or acquisition_task.done():
                        acquisition_task = asyncio.create_task(acquire_data())

                    # Update frontend at 10 Hz
                    await update_frontend()

            except asyncio.CancelledError:
                print(f'DAQ WEBSOCKET DISCONNECTED')
                if acquisition_task and not acquisition_task.done():
                    acquisition_task.cancel()
            except Exception as e:
                print(f'ERROR IN DAQ STREAM: {str(e)}')
                import traceback
                traceback.print_exc()
            finally:
                print(f'DAQ STREAM HANDLER EXITED')
                self.stop()  # Ensure DAQ is stopped when websocket disconnects
                if acquisition_task and not acquisition_task.done():
                    acquisition_task.cancel()

    def start(self):
        """Start streaming data"""
        if not self._daq.is_initialized:
            print("DAQ not initialized, cannot start streaming")
            return False

        # Clear buffer
        self._buffer.clear()

        # Start the DAQ
        success = self._daq.start()
        if success:
            self._streaming = True
            print(f"DAQ streaming started on {self._path}")
        return success

    def stop(self):
        """Stop streaming data"""
        self._streaming = False
        success = self._daq.stop()
        print("DAQ streaming stopped")
        return success