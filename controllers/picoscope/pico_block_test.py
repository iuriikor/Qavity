from ps5000a_wrapper import PicoInterface

# Initialize the interface
pico = PicoInterface()
pico.open()

# Configure channels
channel_config = {
    'A': {'enabled': True, 'coupling': 'DC', 'range': 1},
    'B': {'enabled': True, 'coupling': 'AC', 'range': 2}
}
pico.configure_channels(channel_config)

# Set acquisition parameters
pico.set_resolution(14)
pico.set_sampling_frequency(5e6)  # 10 MHz
pico.set_acquisition_time(10.0)    # 10 ms

# Configure external trigger
pico.set_trigger(channel='A', threshold=0.5, direction='Rising', timeout_ms=1000)

# Run block acquisition with automatic file saving
# The data will be saved to 'data/block_test.bin' and metadata to 'data/block_test_header.dat'
# Since we're saving to a file, this function will return None
data = pico.run_block(
    data_dir=r'C:\Users\CavLev\Documents\Data\20250521 - picoscope test/',
    filename='block_test',
    pre_trigger_percent=20,
    additional_metadata={'AcquisitionMode': 'Block', 'TriggerType': 'Channel A'}
)

# Close the connection
pico.close()