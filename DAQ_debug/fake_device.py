import numpy as np
import time
import logging

logger = logging.getLogger(__name__)

class FakeDAQDevice:
    """
    Fake DAQ device that generates sine waves with different frequencies for testing
    """
    
    def __init__(self, num_channels=4):
        self.num_channels = num_channels
        self.channels = [f"fake_channel_{i}" for i in range(num_channels)]
        self.sample_rate = 1000
        self.is_initialized = False
        self.is_running = False
        
        # Different frequencies for each channel
        self.frequencies = [1.0, 2.0, 5.0, 10.0][:num_channels]  # Hz
        self.phase_offsets = [0, np.pi/4, np.pi/2, 3*np.pi/4][:num_channels]
        
        # Keep track of time for continuous signal generation
        self.time_offset = 0
        self.last_read_time = None
        
        logger.info(f"FakeDAQDevice initialized with {num_channels} channels")
    
    def initialize(self, channels, sample_rate=1000):
        """Initialize the fake DAQ device"""
        self.channels = channels
        self.sample_rate = sample_rate
        self.is_initialized = True
        self.time_offset = 0
        self.last_read_time = time.time()
        logger.info(f"FakeDAQDevice initialized with channels: {channels}, sample_rate: {sample_rate}")
        return True
    
    def start(self):
        """Start the fake DAQ"""
        if not self.is_initialized:
            return False
        
        self.is_running = True
        self.last_read_time = time.time()
        logger.info("FakeDAQDevice started")
        return True
    
    def read_data(self, buffer, num_samples):
        """
        Generate fake sine wave data
        """
        if not self.is_running:
            return False
        
        current_time = time.time()
        
        # If this is the first read or too much time has passed, reset
        if self.last_read_time is None or (current_time - self.last_read_time) > 1.0:
            self.last_read_time = current_time
            
        # Calculate time array for continuous signal
        dt = 1.0 / self.sample_rate
        time_array = np.arange(num_samples) * dt + self.time_offset
        
        # Generate sine waves for each channel
        for i, channel in enumerate(self.channels):
            if i < len(self.frequencies):
                freq = self.frequencies[i]
                phase = self.phase_offsets[i] if i < len(self.phase_offsets) else 0
                
                # Generate sine wave with some noise
                signal = np.sin(2 * np.pi * freq * time_array + phase)
                noise = np.random.normal(0, 0.1, num_samples)  # Add some noise
                buffer[i, :] = signal + noise
            else:
                # If more channels than frequencies, use a default
                buffer[i, :] = np.random.normal(0, 0.1, num_samples)
        
        # Update time offset for next read
        self.time_offset += num_samples * dt
        self.last_read_time = current_time
        
        return True
    
    def stop(self):
        """Stop the fake DAQ"""
        self.is_running = False
        logger.info("FakeDAQDevice stopped")
        return True
    
    def close(self):
        """Close the fake DAQ"""
        self.is_running = False
        self.is_initialized = False
        logger.info("FakeDAQDevice closed")
        return True