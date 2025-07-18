import os
import time

from controllers.frequency_generators.Mirny import MirnyFrequencyGenerator

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\Qavity\\dll")
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

from controllers.cameras.ThorCam import ThorCam
from controllers.cameras.Xenics import Xenics
from controllers.streamer import WebcamStreamer
from controllers.frequency_generators.Urukul import UrukulFrequencyGenerator
from controllers.frequency_generators.Mirny import MirnyFrequencyGenerator
from controllers.other.RelayBoard import RelayBoard
from controllers.DAQ.NI_cDAQ9174 import cDAQ9174
from controllers.streamers.DAQDataStreamer import DAQDataStreamer
from controllers.picoscope.ps5000a_wrapper import PicoInterface

def save_as_bin(data, file_path):
    """
    Save data as binary file
    """
    with open(file_path, 'wb') as f:
        f.write(data)
#
# #
# CAMERAS
thorSDK = TLCameraSDK()
available_cameras = thorSDK.discover_available_cameras()
thorcam_1 = ThorCam(available_cameras[0], thorSDK)
thorcam_1.initialize(10, 30)
thorcam_2 = ThorCam(available_cameras[1], thorSDK)
thorcam_2.initialize(10, 20, rotate_img=True)

# xenics_url = 'cam://0'
# xenics_cam = Xenics(xenics_url)
# xenics_cam.initialize(1, 0.01)
# CAMERA STREAMERS (sockets)
time.sleep(0.1)
streamer1 = WebcamStreamer(thorcam_1, "/stream1")
streamer2 = WebcamStreamer(thorcam_2, "/stream2")
# streamer3 = WebcamStreamer(xenics_cam, "/stream3")

# FREQUENCY GENERATORS
urukul_loading_params = {0 : {'frequency': 110000.0e03, 'amplitude': 0.45, 'attenuation': 15.0, 'on': False},
                         1 : {'frequency': 110000.0e03, 'amplitude': 0.44, 'attenuation': 15.0, 'on': False},
                         2 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 15.0, 'on': False},
                         3 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 15.0, 'on': False}}
urukul_loading_conn_params = {'ip_address': '10.34.16.100'}
urukul_loading = UrukulFrequencyGenerator(device_id='0',
                                          channel_params=urukul_loading_params,
                                          connection_params=urukul_loading_conn_params)

# Only 1 channel for now
mirny_channel_params = {0: {'frequency': 400.0e06, 'attenuation': 27, 'on': False}
                        }
mirny_cavity_drive = MirnyFrequencyGenerator(device_id='0',
                                             channel_params=mirny_channel_params,
                                             connection_params=urukul_loading_conn_params)

# RELAY BOARD CONTROLLING AUTOMATIC VALVES
valve_ports = {"Pump": 1,
               "Load": 2}
valve_control_board = RelayBoard(comport='COM6', output_ports=valve_ports)

# DAQ CARDS
daq_sampling_rate = 200
daq_update_rate = 10

daq_card = cDAQ9174()
# Configure DAQ with actual channels
daq_channels = ['cDAQ1Mod1/ai0', 'cDAQ1Mod1/ai1', 'cDAQ1Mod1/ai2', 'cDAQ1Mod1/ai3',
                'cDAQ1Mod2/ai0', 'cDAQ1Mod2/ai1', 'cDAQ1Mod2/ai2', 'cDAQ1Mod2/ai3']
daq_card.initialize(channels=daq_channels, sample_rate=daq_sampling_rate)

# Create DAQ streamer with specific parameters
daq_streamer = DAQDataStreamer(
    daq=daq_card,
    path="/daq_stream",
    sampling_rate=daq_sampling_rate,  # 200 S/s
    buffer_size=2000,   # 20 kS
    update_rate=daq_update_rate     # 4 Hz
)
daq_streamer.set_data_reduction(max_samples=2000, update_rate=daq_update_rate)
# Picoscope  
pico = PicoInterface(name='picoscope_1')

def get_daq_diagnostics():
    """
    Get current DAQ performance diagnostics
    """
    stats = daq_streamer.get_timing_stats()
    if stats:
        print("=== DAQ Performance Diagnostics ===")
        print(f"Average acquisition time: {stats['avg_acquisition_time_ms']:.2f}ms")
        print(f"Average transmission time: {stats['avg_transmission_time_ms']:.2f}ms")
        print(f"Average data size: {stats['avg_data_size_kb']:.1f}KB")
        print(f"Buffer length: {stats['buffer_length']} samples")
        print(f"Sample count: {stats['sample_count']}")
        return stats
    else:
        print("No DAQ timing statistics available yet.")
        return None