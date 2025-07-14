from controllers.frequency_generators.FrequencyGenerator import FrequencyGenerator
import subprocess
import platform
from typing import Optional, Dict, List, Union, Tuple
from controllers.sinara.modify_experiment import update_script_values_by_lines
from controllers.sinara.run_artiq_script import run_artiq_in_clang64_visible

class MirnyFrequencyGenerator(FrequencyGenerator):
    """
    Implementation of class for communication with Mirny module of Sinara.
    Every script communicating with Sinara must be run through Artiq environment,
    therefore the communication here is very slow. Also, there is no support
    for parallel execution of experiments on Sinara (i.e. independent communication
    with individual instruments), so the basic idea is following. There is a number of
    template scripts implementing certain use cases, such as rampint the drive frequency,
    continuous Mirny operation with monitoring experiment through Sampler etc.
    Communicating with Mirny changes certain parameters in corresponding template,
    and then runs .bat file to run the script in Artiq. This makes it VERY slow and
    unflexible.
    """

    def __init__(self, device_id: str, channel_params: Dict = None, connection_params: Dict = None,
                 freq_gen_path: str = None, freq_ramp_path: str = None):
        """
        Args:
            device_id: ID of Mirny in case there is more than 1. Not implemented for now.
            channel_params: Dictionary of channel output parameters.
                    Format: {int ch_num : {'frequency': float, 'attenuation': float, 'on': bool}}
            connection_params: IP address of Kasli
        """
        super().__init__(device_id, connection_params)
        self.channel_params = channel_params
        # Default ramp parameters
        self.ramp_params = {}
        self.ramp_params["Starting frequency kHz"] = channel_params[0]["frequency"]/1e03
        self.ramp_params["Ending frequency kHz"] = channel_params[0]["frequency"]/1e03
        self.ramp_params["Frequency step kHz"] = 1
        self.ramp_params["Delay seconds"] = 0.1

        self.output_updated = False
        self.connect()
        if freq_gen_path is None:
            self.freq_gen_path = r'C:/Users/CavLev/Documents/Qavity/controllers/sinara/mirny_as_freq_gen.py'
        if freq_ramp_path is None:
            self.freq_ramp_path = r'C:/Users/CavLev/Documents/Qavity/controllers/sinara/mirny_scan.py'

    def update_properties_from_dict(self, prop_dict):
        """
        Because  I can't be bothered doing it properly at the moment
        :param prop_dict: dictionary of channel and ramp properties
        :return:
        """
        try:
            for param in self.ramp_params.keys():
                if param in prop_dict.keys():
                    self.ramp_params[param] = prop_dict[param]
            self.channel_params[0]['frequency'] = prop_dict["Output frequency"]
            self.channel_params[0]['attenuation'] = prop_dict["Output attenuation"]
            self.channel_params[0]['on'] = prop_dict["Output on"]
            self.output_updated = prop_dict["Scripts updated"]
        except Exception as e:
            self.logger.error(f"Error updating channel properties from dictionary: {e}")


    def connect(self) -> bool:
        """
        Since the communication is through Kasli, I just make sure the Kasli IP is pinged.
        Suggestion for device with more than 1 Mirny: check device_db file here.
        """
        # Adjust ping command based on operating system
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.connection_params['ip_address']]
        try:
            response = subprocess.run(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True,
                                      timeout=5)
            self.logger.info(f"Connected to: Mirny {self.connection_params['ip_address']}")
            self.connected = True
            return response.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error(f"Failed to connect to Mirny: Sinara can't be reached")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Mirny: error checking ping")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from Mirny - nothing to be done here"""
        return True

    def update_freq_gen_script(self, starting_line: int = 22) -> bool:
        updates = {}
        script_path = self.freq_gen_path
        self.logger.info(f"Updating frequency generator script")
        self.logger.info(f"Pushing channel parameters: {self.channel_params[0]}")
        # First we generate a dictionary with line number and new numerical value of variable at that line
        # For now Mirny only works with 1 channel, Channel 0
        updates[starting_line] = float(self.channel_params[0]['frequency']/1e03) # Output frequency
        updates[starting_line+1] = float(self.channel_params[0]['attenuation']) # Channel attenuation
        updates[starting_line+3] = self.channel_params[0]['on'] # If the channel should be on
        # Now we push the updates into the driver script
        try:
            self.logger.info(f"Updating frequency gen script: \n {script_path}")
            update_script_values_by_lines(script_path, updates)
            self.output_updated = True
            return True
        except Exception as e:
            self.logger.error(f"Error updating the script file: {str(e)}")
            return False

    def set_frequency(self, frequency: float, channel: int = 0) -> bool:
        """Set the output frequency of Mirny."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to Mirny")
                return False

            self.channel_params[channel]['frequency'] = frequency
            self.output_updated = False
            return True
        except Exception as e:
            self.logger.error(f"Error setting frequency: {str(e)}")
            return False

    def get_frequency(self, channel: int = 0) -> float:
        try:
            if not self.connected:
                self.logger.warning("Not connected to Mirny")
                return 0.0
            if not self.output_updated:
                self.logger.warning("Mirny output not up to date with driver script")
            return self.channel_params[channel]['frequency']
        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return 0.0

    def set_attenuation(self, attenuation: float, channel: int = 0) -> bool:
        """Set the output attenuation for Mirny generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.channel_params[channel]['attenuation'] = attenuation
            self.output_updated = False
            return True
        except Exception as e:
            self.logger.error(f"Error setting attenuation: {str(e)}")
            return False

    def get_attenuation(self, channel: int = 0) -> float:
        """Get the current output attenuation for Mirny generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            if not self.output_updated:
                self.logger.warning("Mirny output not up to date with driver script")
            return self.channel_params[channel]['attenuation']
        except Exception as e:
            self.logger.error(f"Error getting attenuation: {str(e)}")
            return 0.0

    def get_amplitude(self, channel: int = 0) -> float:
        """Not implemented for Mirny generator."""
        return 0

    def set_amplitude(self, amplitude: float, channel: int = 0) -> bool:
        """Not implemented for Mirny generator."""
        return False

    def output_on(self, channel: int = 0) -> bool:
        """Turn on the output for Mirny generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            if not self.channel_params[channel]['on']:
                self.channel_params[channel]['on'] = True
                self.output_updated = False
            return True
        except Exception as e:
            self.logger.error(f"Error turning output on: {str(e)}")
            return False

    def output_off(self, channel: int = 0) -> bool:
        """Turn on the output for Mirny generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            if self.channel_params[channel]['on']:
                self.channel_params[channel]['on'] = False
                self.output_updated = False
            return True
        except Exception as e:
            self.logger.error(f"Error turning output on: {str(e)}")
            return False

    def get_output_state(self, channel: int = 0) -> bool:
        """Get the current output state for Mirny generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            if not self.output_updated:
                self.logger.warning("Mirny output not up to date with driver script")
            return self.channel_params[channel]['on']
        except Exception as e:
            self.logger.error(f"Error getting output state: {str(e)}")
            return False

    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """
        Mirny does not have this capability and only generates sine wave
        """
        self.logger.warning("Mirny only generates sine wave")
        return True

    def is_up_to_date(self):
        return self.output_updated

    def set_ramp_starting_freq(self, start_freq_kHz):
        """
        Updates ramp starting frequency. Generally should be the same as current frequency
        :param start_freq_kHz: starting ramp frequency, in kHz
        :return: True if successful, False otherwise
        """
        try:
            self.ramp_params["Starting frequency kHz"] = start_freq_kHz
            if int(start_freq_kHz) != int(self.channel_params[0]['frequency']):
                self.logger.warning(f"Starting frequency of the ramp {start_freq_kHz} kHz is "
                              f"different from current output frequency {self.channel_params[0]['frequency']/1e03} kHz")
            return True
        except Exception as e:
            self.logger.error(f"Error setting ramp starting frequency: {str(e)}")
            return False

    def set_ramp_ending_freq(self, end_freq_kHz):
        """
        Updates ramp ending frequency.
        :param end_freq_kHz: ending ramp frequency, in kHz
        :return: True if successful, False otherwise
        """
        try:
            self.ramp_params["Ending frequency kHz"] = end_freq_kHz
            return True
        except Exception as e:
            self.logger.error(f"Error setting ramp starting frequency: {str(e)}")
            return False

    def set_ramp_step(self, step_kHz):
        """
        Sets frequency step in kHz between consecutive steps in output frequency
        :param step_kHz: frequency step in kHz
        :return: True if successful, False otherwise
        """
        try:
            self.ramp_params["Frequency step kHz"] = step_kHz
            return True
        except Exception as e:
            self.logger.error(f"Error setting ramp starting frequency: {str(e)}")
            return False

    def set_ramp_delay(self, delay_s):
        """
        Sets delay time in seconds between consecutive steps in output frequency
        :param delay_s: delay time between frequency steps, in seconds
        :return: True if successful, False otherwise
        """
        try:
            self.ramp_params["Delay seconds"] = delay_s
            return True
        except Exception as e:
            self.logger.error(f"Error setting ramp starting frequency: {str(e)}")
            return False

    def update_freq_ramp_script(self) -> float:
        """
        Updates frequency ramp script. Takes parameters from self.ramp_params dictionary.
        :return: True if update was successful, False otherwise
        """
        script_path = self.freq_ramp_path # Path to the Artiq frequency ramp script
        start_freq_update_line = 24
        end_freq_update_line = 25
        step_update_line = 27
        delay_update_line = 29
        turn_off_update_line = 31
        code_updates = {start_freq_update_line: float(self.ramp_params["Starting frequency kHz"]),
                        end_freq_update_line: float(self.ramp_params["Ending frequency kHz"]),
                        step_update_line: float(self.ramp_params["Frequency step kHz"]),
                        delay_update_line: float(self.ramp_params["Delay seconds"]),
                        turn_off_update_line: False}
        try:
            update_script_values_by_lines(script_path, code_updates)
            self.logger.info('UPDATING SCRIPT TO RAMP CAVITY DRIVE FREQUENCY')
            # self.channel_params[0]['frequency'] = float(self.ramp_params["Ending frequency kHz"]*1e03)
            # self.channel_params[0]['attenuation'] = 27
            # self.channel_params[0]['on'] = True
            # self.output_updated = True
            # self.update_freq_gen_script()
            return True
        except Exception as e:
            self.logger.error(f"Error updating the script file: {str(e)}")
            return False

    def run_freq_ramp_script(self):
        run_artiq_in_clang64_visible(self.freq_ramp_path)

    def run_freq_gen_script(self):
        run_artiq_in_clang64_visible(self.freq_gen_path)
