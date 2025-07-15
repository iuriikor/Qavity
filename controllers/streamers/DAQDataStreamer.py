from quart import websocket
from server import webcam_server
import asyncio
import json
import numpy
import time
from controllers.utils.CircularBuffer import CircularBuffer
import struct
import logging


class DAQDataStreamer:
    def __init__(self, daq, path, sampling_rate=1000, buffer_size=20000, update_rate=10):
        self._daq = daq
        self._path = path
        self._sampling_rate = sampling_rate  # 1 kS/s default
        self._update_rate = update_rate  # 10 Hz default
        self._buffer_size = buffer_size  # 20 kS default
        self._streaming = False
        
        # Add debugging and timing tracking
        self._logger = logging.getLogger(f"DAQDataStreamer.{self._path}")
        self._debug_enabled = True
        self._timing_stats = {
            'acquisition_times': [],
            'transmission_times': [],
            'data_sizes': [],
            'last_timestamp': time.time()
        }

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
                    samples_per_read = 200  # Read 200 samples at a time for efficiency
                    sleep_time = 1.0 / self._update_rate

                    while self._streaming:
                        start_time = time.time()
                        
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
                            
                            # Track acquisition timing
                            acq_time = time.time() - start_time
                            self._timing_stats['acquisition_times'].append(acq_time)
                            
                            # Keep only last 100 measurements for stats
                            if len(self._timing_stats['acquisition_times']) > 100:
                                self._timing_stats['acquisition_times'] = self._timing_stats['acquisition_times'][-100:]
                            
                            if self._debug_enabled and len(self._timing_stats['acquisition_times']) % 50 == 0:
                                avg_acq_time = sum(self._timing_stats['acquisition_times']) / len(self._timing_stats['acquisition_times'])
                                self._logger.info(f"Avg acquisition time: {avg_acq_time*1000:.2f}ms")

                        # Sleep to maintain the sampling rate
                        await asyncio.sleep(sleep_time)

                # Define frontend update coroutine - using binary format
                async def update_frontend():
                    update_interval = 1.0 / self._update_rate  # 10 Hz update rate

                    while self._streaming:
                        try:
                            start_time = time.time()
                            
                            # Get all data from the buffer
                            buffer_data = self._buffer.get_data()

                            # Get timestamp
                            current_time = time.time()

                            # Start with timestamp and number of channels
                            binary_data = struct.pack('!di', current_time, len(buffer_data))

                            # Add each channel's data - limit to reduce latency
                            max_samples_per_channel = getattr(self, '_max_samples_per_channel', 2000)
                            
                            for channel_name, data in buffer_data.items():
                                # Limit to last N samples to reduce data size and latency
                                limited_data = data[-max_samples_per_channel:] if len(data) > max_samples_per_channel else data

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
                            
                            # Track transmission timing and data size
                            transmission_time = time.time() - start_time
                            data_size = len(binary_data)
                            
                            self._timing_stats['transmission_times'].append(transmission_time)
                            self._timing_stats['data_sizes'].append(data_size)
                            
                            # Keep only last 100 measurements
                            if len(self._timing_stats['transmission_times']) > 100:
                                self._timing_stats['transmission_times'] = self._timing_stats['transmission_times'][-100:]
                                self._timing_stats['data_sizes'] = self._timing_stats['data_sizes'][-100:]
                            
                            # Periodic debug logging
                            if self._debug_enabled and len(self._timing_stats['transmission_times']) % 50 == 0:
                                avg_trans_time = sum(self._timing_stats['transmission_times']) / len(self._timing_stats['transmission_times'])
                                avg_data_size = sum(self._timing_stats['data_sizes']) / len(self._timing_stats['data_sizes'])
                                time_since_last = current_time - self._timing_stats['last_timestamp']
                                self._timing_stats['last_timestamp'] = current_time
                                
                                self._logger.info(f"Transmission: {avg_trans_time*1000:.2f}ms avg, {avg_data_size/1024:.1f}KB avg, {time_since_last:.2f}s since last log")

                        except Exception as e:
                            self._logger.error(f"Error in update_frontend: {e}")
                            import traceback
                            traceback.print_exc()

                        # Sleep to maintain update rate
                        await asyncio.sleep(update_interval)

                # Main websocket loop - run acquisition and transmission in parallel
                while True:
                    if not self._streaming:
                        # If streaming is off, wait and check again
                        await asyncio.sleep(0.5)
                        continue

                    # Start data acquisition task if not already running
                    if acquisition_task is None or acquisition_task.done():
                        acquisition_task = asyncio.create_task(acquire_data())

                    # Create transmission task for parallel execution
                    transmission_task = asyncio.create_task(update_frontend())
                    
                    # Wait for the transmission task to complete
                    await transmission_task

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
    
    def set_data_reduction(self, max_samples=2000, update_rate=20):
        """
        Adjust data reduction settings to reduce latency
        
        Args:
            max_samples: Maximum samples per channel to send to frontend
            update_rate: Update rate in Hz
        """
        self._update_rate = update_rate
        self._max_samples_per_channel = max_samples
        self._logger.info(f"Data reduction settings: max_samples={max_samples}, update_rate={update_rate}Hz")
    
    def get_timing_stats(self):
        """Get current timing statistics"""
        if not self._timing_stats['acquisition_times']:
            return None
            
        return {
            'avg_acquisition_time_ms': sum(self._timing_stats['acquisition_times']) / len(self._timing_stats['acquisition_times']) * 1000,
            'avg_transmission_time_ms': sum(self._timing_stats['transmission_times']) / len(self._timing_stats['transmission_times']) * 1000,
            'avg_data_size_kb': sum(self._timing_stats['data_sizes']) / len(self._timing_stats['data_sizes']) / 1024,
            'buffer_length': self._buffer.get_length(),
            'sample_count': len(self._timing_stats['acquisition_times'])
        }