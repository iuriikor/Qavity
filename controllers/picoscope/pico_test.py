from ps5000a_wrapper import PicoInterface

# Define a callback function for real-time monitoring
def process_data(data_chunk, channels, param):
    # This is just for monitoring - we're saving to a file separately
    print(f"Received {len(data_chunk)} samples for channels {channels}")

# Initialize the interface
pico = PicoInterface()
pico.open()

# Configure channels
channel_config = {
    'A': {'enabled': True, 'coupling': 'DC', 'range': 5},
    'B': {'enabled': True, 'coupling': 'AC', 'range': 2}
}
pico.configure_channels(channel_config)

# Set acquisition parameters
pico.set_resolution(14)
pico.set_sampling_frequency(5e6, 10e-03)   # 1 MHz
# pico.set_acquisition_time(10.0)

# Run streaming acquisition with direct file output
# The data will be saved to 'data/streaming_test.bin' and metadata to 'data/streaming_test_header.dat'
# Since we're saving to a file, this function will return None
data = pico.run_streaming(
    data_dir=r'C:\Users\CavLev\Documents\Data\20250521 - picoscope test/',
    filename='streaming_test',
    additional_metadata={'ExperimentType': 'Streaming Test'}
)

# Close the connection
pico.close()