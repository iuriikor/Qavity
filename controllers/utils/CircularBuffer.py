from collections import deque


class CircularBuffer:
    """
    Circular buffer for storing channel data without timestamps.
    X-axis will be generated based on sample count and sample rate.
    """

    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.buffer = {}  # Dictionary of deques for each channel
        self.sample_count = 0  # Total number of samples added

    def add_channel(self, channel):
        """Add a new channel to the buffer if it doesn't exist"""
        if channel not in self.buffer:
            self.buffer[channel] = deque(maxlen=self.max_size)

    def add_data(self, data_dict):
        """Add data for multiple channels"""
        if not data_dict:
            return

        # Add data for each channel
        for channel, values in data_dict.items():
            self.add_channel(channel)
            for value in values:
                self.buffer[channel].append(value)

        # Update sample count based on the first channel's data
        if data_dict:
            first_channel = next(iter(data_dict))
            self.sample_count += len(data_dict[first_channel])

    def get_data(self, channels=None, max_points=None):
        """Get data for specified channels"""
        result = {}
        channels_to_get = channels if channels else self.buffer.keys()

        # Get data for each channel
        for channel in channels_to_get:
            if channel in self.buffer:
                data = list(self.buffer[channel])
                if max_points and len(data) > max_points:
                    data = data[-max_points:]
                result[channel] = data

        return result

    def get_length(self):
        """Get the current length of data in the buffer"""
        if not self.buffer:
            return 0
        first_channel = next(iter(self.buffer))
        return len(self.buffer[first_channel])

    def clear(self):
        """Clear all data"""
        for channel in self.buffer:
            self.buffer[channel].clear()
        self.sample_count = 0