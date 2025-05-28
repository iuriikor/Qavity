import numpy as np
import os
import time
from datetime import datetime
from picoscope import ps5000a


class PicoInterface:
    """Interface class for controlling PicoScope 5444D acquisition.

    Supports both streaming mode with software trigger and callback, as well as
    externally triggered block acquisition with or without callback.
    """
    # Static class variables for callbacks
    _device_data = {}  # Dictionary to store data for each device handle
    _save_files = {}  # Dictionary to store file handles
    _user_callbacks = {}  # Dictionary to store user callbacks
    _enabled_channels = {}  # Dictionary to store enabled channels for each device
    _total_samples = {}  # Track total samples for each device

    def __init__(self, name=None):
        """Initialize the PicoScope interface."""
        self.ps = None
        self.name = name
        self.handle = None  # Will store the device handle
        self.channels_enabled = {'A': False, 'B': False, 'C': False, 'D': False}
        self.channel_ranges = {'A': 5, 'B': 5, 'C': 5, 'D': 5}  # Voltage ranges in V
        self.channel_couplings = {'A': 'DC', 'B': 'DC', 'C': 'DC', 'D': 'DC'}
        self.channel_offsets = {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0}
        self.resolution = 14  # Default resolution in bits
        self.sample_freq = 10e6  # Default 10 MHz
        self.actual_sample_freq = None  # Actual frequency set by the device
        self.num_samples = 1000  # Default number of samples
        self.actual_num_samples = None  # Actual number of samples set by the device
        self.acquisition_time = 0.0001  # Default acquisition time
        self.actual_acquisition_time = None  # Actual acquisition time
        self.sampling_interval = 1e-7  # Default sampling interval (1/frequency)
        self.is_open = False

    @staticmethod
    def streaming_callback(handle, num_samples, start_index, overflow,
                           trigger_at, triggered, auto_stop, param):
        """Static callback function for streaming mode called by SDK.

        This has the exact signature expected by the SDK, without 'self'.
        """
        # Get the data buffer and other parameters for this specific device
        data = PicoInterface._device_data.get(handle)
        save_file = PicoInterface._save_files.get(handle)
        user_callback = PicoInterface._user_callbacks.get(handle)
        enabled_channels = PicoInterface._enabled_channels.get(handle, [])

        # Update total samples counter for this device
        PicoInterface._total_samples[handle] += num_samples

        end_index = start_index + num_samples

        # Extract the data from the buffer
        if len(enabled_channels) == 1:
            data_slice = data[start_index:end_index]
        else:
            data_slice = data[:, start_index:end_index].T

        # Save to file if file object exists
        if save_file:
            data_slice.tofile(save_file)

    def get_name(self):
        if self.name:
            return self.name
        else:
            return ''

    def open(self):
        """Open connection to the PicoScope."""
        if not self.is_open:
            try:
                self.ps = ps5000a.PS5000a()
                self.handle = self.ps.handle  # Store the device handle
                self.is_open = True
                # Set default resolution
                self.set_resolution(self.resolution)
                print("PicoScope connected successfully")
                return True
            except Exception as e:
                print(f"Error opening PicoScope: {e}")
                return False
        else:
            print("PicoScope is already open")
            return True

    def close(self):
        """Close connection to the PicoScope."""
        if self.is_open and self.ps:
            try:
                # Clean up any static data for this device
                if self.handle in PicoInterface._device_data:
                    del PicoInterface._device_data[self.handle]
                if self.handle in PicoInterface._save_files:
                    if PicoInterface._save_files[self.handle]:
                        PicoInterface._save_files[self.handle].close()
                    del PicoInterface._save_files[self.handle]
                if self.handle in PicoInterface._user_callbacks:
                    del PicoInterface._user_callbacks[self.handle]
                if self.handle in PicoInterface._enabled_channels:
                    del PicoInterface._enabled_channels[self.handle]

                self.ps.stop()
                self.ps.close()
                self.is_open = False
                print("PicoScope disconnected")
                return True
            except Exception as e:
                print(f"Error closing PicoScope: {e}")
                return False
        else:
            print("PicoScope is already closed")
            return True

    def set_channel(self, channel, enabled=True, coupling='DC', voltage_range=5, offset=0.0):
        """Configure a specific channel.

        Args:
            channel (str): Channel identifier ('A', 'B', 'C', or 'D')
            enabled (bool): Whether the channel is enabled
            coupling (str): 'AC' or 'DC' coupling
            voltage_range (float): Voltage range in volts
            offset (float): Voltage offset in volts
        """
        if not self.is_open:
            print("PicoScope not open")
            return False

        if channel not in ['A', 'B', 'C', 'D']:
            print(f"Invalid channel: {channel}")
            return False

        try:
            self.ps.setChannel(
                channel=channel,
                enabled=enabled,
                coupling=coupling,
                VRange=voltage_range,
                VOffset=offset,
                BWLimited=False
            )
            self.channels_enabled[channel] = enabled
            self.channel_ranges[channel] = voltage_range
            self.channel_couplings[channel] = coupling
            self.channel_offsets[channel] = offset
            return True
        except Exception as e:
            print(f"Error setting channel {channel}: {e}")
            return False

    def configure_channels(self, channel_config):
        """Configure multiple channels at once using a dictionary.

        Args:
            channel_config (dict): Dictionary where keys are channel identifiers
                and values are dictionaries of properties. Example:
                {
                    'A': {'enabled': True, 'coupling': 'DC', 'range': 5, 'offset': 0},
                    'B': {'enabled': True, 'coupling': 'AC', 'range': 2, 'offset': 0}
                }

        Returns:
            bool: Success status
        """
        if not self.is_open:
            print("PicoScope not open")
            return False

        success = True
        for channel, config in channel_config.items():
            if channel not in ['A', 'B', 'C', 'D']:
                print(f"Invalid channel: {channel}")
                success = False
                continue

            try:
                # Get channel settings with defaults
                enabled = config.get('enabled', True)
                coupling = config.get('coupling', 'DC')
                voltage_range = config.get('range', 5)
                offset = config.get('offset', 0.0)

                # Configure the channel
                channel_success = self.set_channel(
                    channel=channel,
                    enabled=enabled,
                    coupling=coupling,
                    voltage_range=voltage_range,
                    offset=offset
                )
                if not channel_success:
                    success = False
            except Exception as e:
                print(f"Error configuring channel {channel}: {e}")
                success = False

        return success

    def set_resolution(self, resolution):
        """Set ADC resolution.

        Args:
            resolution (int): Resolution in bits (8, 12, 14, 15, or 16)
        """
        if not self.is_open:
            print("PicoScope not open")
            return False

        if resolution not in [8, 12, 14, 15, 16]:
            print(f"Invalid resolution: {resolution}")
            return False

        try:
            self.ps.setResolution(str(resolution))
            self.resolution = resolution
            return True
        except Exception as e:
            print(f"Error setting resolution: {e}")
            return False

    def set_sampling_frequency(self, frequency):
        """Set sampling frequency.

        Args:
            frequency (float): Sampling frequency in Hz

        Returns:
            float: Actual sampling frequency set
        """
        if not self.is_open:
            print("PicoScope not open")
            return 0

        # try:
        self.sample_freq = frequency
        #     result = self.ps.setSamplingFrequency(frequency, self.num_samples)
        #     self.actual_sample_freq = result[0]
        #     # Update number of samples based on the actual frequency
        #     self.actual_num_samples = result[1]
        #     # Update sampling interval and acquisition time
        #     self.sampling_interval = 1.0 / self.actual_sample_freq
        #     self.actual_acquisition_time = self.actual_num_samples / self.actual_sample_freq
        #     return self.actual_sample_freq
        # except Exception as e:
        #     print(f"Error setting sampling frequency: {e}")
        #     return 0

    def set_acquisition_time(self, time_s):
        """Set acquisition time.

        Args:
            time_s (float): Acquisition time in seconds

        Returns:
            tuple: (actual_time, num_samples)
        """
        if not self.is_open:
            print("PicoScope not open")
            return (0, 0)

        # try:
            # Store the requested acquisition time
        self.acquisition_time = time_s

        #     # Calculate number of samples based on the current sampling frequency
        #     self.num_samples = int(self.sample_freq * time_s)
        #     # Update the sampling frequency with the new number of samples
        #     actual_fs = self.set_sampling_frequency(self.sample_freq)
        #     # Result will be updated by set_sampling_frequency
        #     return (self.actual_acquisition_time, self.actual_num_samples)
        # except Exception as e:
        #     print(f"Error setting acquisition time: {e}")
        #     return (0, 0)

    def set_trigger(self, channel='NONE', threshold=0.0, direction='Rising',
                    delay=0, auto_trigger=True, timeout_ms=1000):
        """Configure trigger settings.

        Args:
            channel (str): Trigger channel ('A', 'B', 'C', 'D', 'External', or 'NONE')
            threshold (float): Trigger threshold in volts
            direction (str): 'RISING', 'FALLING', 'ABOVE', 'BELOW', or 'RISING_OR_FALLING'
            delay (int): Trigger delay in samples
            auto_trigger (bool): Auto trigger after timeout_ms if no trigger occurs
            timeout_ms (int): Timeout in milliseconds
        """
        if not self.is_open:
            print("PicoScope not open")
            return False

        if channel == 'NONE':
            try:
                # Disable trigger
                self.ps.setSimpleTrigger(None, enabled=False)
                return True
            except Exception as e:
                print(f"Error disabling trigger: {e}")
                return False
        else:
            try:
                self.ps.setSimpleTrigger(
                    channel,
                    threshold_V=threshold,
                    direction=direction,
                    delay=delay,
                    enabled=True,
                    timeout_ms=timeout_ms if auto_trigger else 0
                )
                return True
            except Exception as e:
                print(f"Error setting trigger: {e}")
                return False

    def run_streaming(self, duration=None, data_dir=None, filename=None, pre_trigger=0.0, auto_stop=True,
                      down_sample_ratio=1, down_sample_mode=0, callback=None, callback_param=None,
                      additional_metadata=None):
        """Run in streaming mode with software trigger."""
        if not self.is_open:
            print("PicoScope not open")
            return None
        if duration is None:
            duration = self.acquisition_time
        else:
            self.acquisition_time = duration

        try:
            self.num_samples = int(self.sample_freq * self.acquisition_time)
            self.actual_sample_freq, _ = self.ps.setSamplingFrequency(self.sample_freq, self.num_samples)
            self.sampling_interval = 1/self.actual_sample_freq
            print(f"REQUESTED: Samples {self.num_samples} Frequency {self.sample_freq}")
            print(f"ACTUAL: Samples {self.actual_num_samples} Frequency {self.actual_sample_freq}")
        except Exception as e:
            print(f"Error setting acquisition time: {e}")


        # Get list of enabled channels
        enabled_channels = [ch for ch, enabled in self.channels_enabled.items() if enabled]

        if not enabled_channels:
            print("No channels enabled")
            return None

        # Store enabled channels for this device
        PicoInterface._enabled_channels[self.handle] = enabled_channels

        # Initialize the total samples counter for this device
        PicoInterface._total_samples[self.handle] = 0

        # Determine if we're saving to a file
        saving_to_file = data_dir is not None and filename is not None

        # Open file for saving if path provided
        if saving_to_file:
            try:
                # Create directory if it doesn't exist
                os.makedirs(data_dir, exist_ok=True)

                # Create full file path for binary data
                full_path = os.path.join(data_dir, f"{filename}.bin")

                # Open the file
                PicoInterface._save_files[self.handle] = open(full_path, 'wb')
            except Exception as e:
                print(f"Error opening file for saving: {e}")
                PicoInterface._save_files[self.handle] = None
                saving_to_file = False
        else:
            PicoInterface._save_files[self.handle] = None

        # Set user callback
        PicoInterface._user_callbacks[self.handle] = callback
        self.ps.setNoOfCaptures(noCaptures=1)
        self.ps.memorySegments(noSegments=1)

        try:
            # Allocate data buffers for streaming
            data_buffer = self.ps.allocateDataBuffers(
                channels=enabled_channels,
                numSamples=0,  # Zero for streaming mode
                downSampleMode=down_sample_mode
            )
            data_buffer.squeeze()

            # Store buffer for this device
            PicoInterface._device_data[self.handle] = data_buffer

            # Start streaming
            self.ps.runStreaming(
                bAutoStop=auto_stop,
                downSampleMode=down_sample_mode,
                downSampleRatio=down_sample_ratio
            )
            time.sleep(0.2) # Slack to give picoscope time to arm?

            # print(f"REQUESTED STREAM DURATION: {self.acquisition_time}")
            # Process streaming data
            elapsed_time = 0
            starting_time = datetime.now()
            while elapsed_time < self.acquisition_time:
                self.ps.getStreamingLatestValues(callback=PicoInterface.streaming_callback)
                elapsed_time = (datetime.now() - starting_time).total_seconds()
                time.sleep(0.1)  # Small delay to prevent CPU hogging
            # Stop acquisition
            self.ps.stop()
            print(f"Elapsed time: {elapsed_time}")

            # Update actual values based on collected samples
            self.actual_num_samples = PicoInterface._total_samples.get(self.handle, 0)
            self.actual_acquisition_time = self.actual_num_samples / self.actual_sample_freq

            # Close file if opened
            if self.handle in PicoInterface._save_files and PicoInterface._save_files[self.handle]:
                PicoInterface._save_files[self.handle].close()
                PicoInterface._save_files[self.handle] = None

            # Save metadata if we're saving to a file
            if saving_to_file:
                metadata = self.generate_metadata(additional_metadata)
                metadata_file = os.path.join(data_dir, f"{filename}_header.dat")
                with open(metadata_file, 'w') as f:
                    for key, value in metadata.items():
                        f.write(f"{key}:\t{value}\n")
                print(f"Metadata saved to {metadata_file}")

            # Return data buffer only if not saving to file
            return None if saving_to_file else data_buffer

        except Exception as e:
            print(f"Error in streaming mode: {e}")
            # Clean up in case of error
            if self.handle in PicoInterface._save_files and PicoInterface._save_files[self.handle]:
                PicoInterface._save_files[self.handle].close()
                PicoInterface._save_files[self.handle] = None
            return None

    def run_block(self, data_dir=None, filename=None, pre_trigger_percent=0,
                  segment_index=0, callback=None, callback_param=None,
                  additional_metadata=None):
        """Run in block mode with external trigger.

        Args:
            data_dir (str, optional): Directory to save data and metadata files
            filename (str, optional): Base filename without extension
            pre_trigger_percent (float): Percentage of samples before trigger (0-100)
            segment_index (int): Memory segment to use
            callback (function): Optional callback function for notification
            callback_param: Additional parameter to pass to the callback
            additional_metadata (dict, optional): Additional metadata to include

        Returns:
            dict: Dictionary containing channel data if not saving to file, otherwise None
        """
        if not self.is_open:
            print("PicoScope not open")
            return None

        try:
            self.num_samples = int(self.sample_freq * self.acquisition_time)
            self.actual_sample_freq, _ = self.ps.setSamplingFrequency(self.sample_freq, self.num_samples)
            self.sampling_interval = 1 / self.actual_sample_freq
        except Exception as e:
            print(f"Error setting acquisition time: {e}")

        # Get list of enabled channels
        enabled_channels = [ch for ch, enabled in self.channels_enabled.items() if enabled]

        if not enabled_channels:
            print("No channels enabled")
            return None

        # Determine if we're saving to a file
        saving_to_file = data_dir is not None and filename is not None

        try:
            # Set memory segments (1 by default)
            self.ps.memorySegments(1)
            self.ps.setNoOfCaptures(1)

            # Start block mode acquisition
            self.ps.runBlock(pretrig=pre_trigger_percent / 100.0, segmentIndex=segment_index)

            # Wait for data or use callback
            if callback:
                # Register the callback with the SDK
                self.ps.setDataReadyCallback(callback, callback_param)
            else:
                # Wait for the device to become ready
                self.ps.waitReady()

            # Get the data
            result = {}
            actual_samples = 0
            for channel in enabled_channels:
                # Get data in volts
                data = self.ps.getDataV(channel, self.num_samples, segmentIndex=segment_index)
                result[channel] = data


            # Update actual sample count based on real data received
            if len(result) > 0:
                # Use the actual data length, not the buffer size
                channel = next(iter(result))
                actual_data_length = len(result[channel])

                # Update actual sample count and acquisition time
                self.actual_num_samples = actual_data_length
                self.actual_acquisition_time = self.actual_num_samples / self.actual_sample_freq

            # Save to file if requested
            if saving_to_file:
                try:
                    # Create directory if it doesn't exist
                    os.makedirs(data_dir, exist_ok=True)

                    # Create full file path for binary data
                    data_path = os.path.join(data_dir, f"{filename}.bin")

                    # Save the data
                    with open(data_path, 'wb') as f:
                        # Convert dictionary of channel data to array and save
                        channels = list(result.keys())
                        if len(channels) == 1:
                            result[channels[0]].tofile(f)
                        else:
                            # Interleave channel data
                            interleaved = np.column_stack([result[ch] for ch in channels])
                            interleaved.tofile(f)

                    # Save metadata
                    metadata = self.generate_metadata(additional_metadata)
                    metadata_file = os.path.join(data_dir, f"{filename}_header.dat")
                    with open(metadata_file, 'w') as f:
                        for key, value in metadata.items():
                            f.write(f"{key}:\t{value}\n")
                    print(f"Block data saved to {data_path}")
                    print(f"Metadata saved to {metadata_file}")

                    # Return None if saving to file
                    return None
                except Exception as e:
                    print(f"Error saving block data to file: {e}")
                    # If saving fails, still return the data
                    return result

            # Return data if not saving to file
            return result

        except Exception as e:
            print(f"Error in block mode: {e}")
            return None

    def generate_metadata(self, additional_metadata=None):
        """Generate metadata dictionary for the current configuration.

        Args:
            additional_metadata (dict): Optional additional metadata to include

        Returns:
            dict: Complete metadata dictionary
        """
        # Get list of enabled channels
        enabled_channels = [ch for ch, enabled in self.channels_enabled.items() if enabled]
        enabled_channels_str = ','.join(enabled_channels)

        # Build basic metadata
        metadata = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'RequestedSamplingFrequency': f"{self.sample_freq / 1e6:.6f} MHz",
            'ActualSamplingFrequency': f"{self.actual_sample_freq / 1e6:.6f} MHz",
            'SamplingInterval': f"{self.sampling_interval * 1e9:.6f} ns",
            'RequestedAcquisitionTime': f"{self.acquisition_time * 1000:.6f} ms",
            'ActualAcquisitionTime': f"{self.actual_acquisition_time * 1000:.6f} ms",
            'RequestedNumberOfSamples': self.num_samples,
            'ActualNumberOfSamples': self.actual_num_samples,
            'Resolution': f"{self.resolution} bits",
            'EnabledChannels': enabled_channels_str,
        }

        # Add channel-specific metadata
        for channel in enabled_channels:
            metadata[f'Channel{channel}Range'] = f"{self.channel_ranges[channel]} V"
            metadata[f'Channel{channel}Coupling'] = self.channel_couplings[channel]
            metadata[f'Channel{channel}Offset'] = f"{self.channel_offsets[channel]} V"

        # Add additional metadata if provided
        if additional_metadata:
            metadata.update(additional_metadata)

        return metadata

    def save_data_to_file(self, data_dir, filename, data, additional_metadata=None):
        """Save acquired data to file with metadata.

        Args:
            data_dir (str): Directory to save data and metadata files
            filename (str): Base filename without extension
            data (dict or numpy.ndarray): Data to save
            additional_metadata (dict): Optional additional metadata to include

        Returns:
            bool: Success status
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(data_dir, exist_ok=True)

            # Create full paths
            data_path = os.path.join(data_dir, f"{filename}.bin")
            metadata_path = os.path.join(data_dir, f"{filename}_header.dat")

            # Create binary data file
            with open(data_path, 'wb') as f:
                if isinstance(data, dict):
                    # Convert dictionary of channel data to array and save
                    channels = list(data.keys())
                    if len(channels) == 1:
                        data[channels[0]].tofile(f)
                    else:
                        # Interleave channel data
                        interleaved = np.column_stack([data[ch] for ch in channels])
                        interleaved.tofile(f)
                else:
                    # Save array directly
                    data.tofile(f)

            # Generate metadata
            metadata = self.generate_metadata(additional_metadata)

            # Create header file
            with open(metadata_path, 'w') as f:
                for key, value in metadata.items():
                    f.write(f"{key}:\t{value}\n")

            return True

        except Exception as e:
            print(f"Error saving data: {e}")
            return False