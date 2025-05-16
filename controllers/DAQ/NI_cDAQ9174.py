import numpy as np

import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader

import logging
# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DAQinterface")


class cDAQ9174:
    """
    Pure interface class for communicating with National Instruments cDAQ-9174 hardware.
    """

    def __init__(self):
        """Initialize the DAQ interface. For specifics - RTFM of nidaqmx."""
        self.task = None # Task object tells DAQ what to do
        self.reader = None  # StreamReader object responsible for data transfer
        self.channels = []
        self.sample_rate = 1000
        self.is_initialized = False
        # Create a class-specific logger object
        self.logger = logging.getLogger(f"DAQinterface.{self.__class__.__name__}")

    def initialize(self, channels, sample_rate=1000):
        """
        Initialize the DAQ interface with specified channels and sample rate.

        Args:
            channels (list): List of channel names to read from, e.g. ['cDAQ1Mod1/ai0']
            sample_rate (int): Sampling rate in samples per second.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        # Clean up any existing task
        self.close()

        try:
            # Create DAQmx task
            self.task = nidaqmx.Task()

            # Add channels
            for channel in channels:
                self.task.ai_channels.add_ai_voltage_chan(
                    channel,
                    terminal_config=TerminalConfiguration.DIFF
                )

            # Configure timing
            self.task.timing.cfg_samp_clk_timing(
                rate=sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=1000  # Internal buffer size
            )

            # Create reader
            self.reader = AnalogMultiChannelReader(self.task.in_stream)

            # Store configuration
            self.channels = channels
            self.sample_rate = sample_rate
            self.is_initialized = True

            return True

        except Exception as e:
            self.logger.error(f"Error initializing DAQ: {e}")
            self.close()
            return False

    def start(self):
        """
        Start the DAQ task.

        Returns:
            bool: True if the task was started successfully, False otherwise.
        """
        if not self.is_initialized or not self.task:
            return False

        try:
            self.task.start()
            return True
        except Exception as e:
            self.logger.error(f"Error starting DAQ task: {e}")
            return False

    def read_data(self, buffer, num_samples):
        """
        Read data from the DAQ into the provided buffer.

        Args:
            buffer (numpy.ndarray): Pre-allocated buffer to read data into.
                                   Should be shape (num_channels, num_samples).
            num_samples (int): Number of samples to read per channel.

        Returns:
            bool: True if the read was successful, False otherwise.
        """
        if not self.is_initialized or not self.task:
            self.logger.warning(f"DAQ task not initialized")
            return False

        try:
            self.reader.read_many_sample(
                buffer,
                number_of_samples_per_channel=num_samples,
                timeout=1.0
            )
            return True
        except Exception as e:
            self.logger.error(f"Error reading data from DAQ: {e}")
            return False

    def stop(self):
        """
        Stop the DAQ task.

        Returns:
            bool: True if the task was stopped successfully, False otherwise.
        """
        if not self.task:
            return True  # Already stopped

        try:
            self.task.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping DAQ task: {e}")
            return False

    def close(self):
        """
        Close the DAQ task and clean up resources.

        Returns:
            bool: True if cleanup was successful, False otherwise.
        """
        try:
            if self.task:
                try:
                    self.task.stop()
                except:
                    pass
                self.task.close()
                self.task = None

            self.reader = None
            self.is_initialized = False
            return True
        except Exception as e:
            self.logger.error(f"Error closing DAQ task: {e}")
            return False