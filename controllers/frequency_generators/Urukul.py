from controllers.frequency_generators.FrequencyGenerator import FrequencyGenerator
import subprocess
import platform
from typing import Optional, Dict, List, Union, Tuple
from controllers.sinara.modify_experiment import update_script_values_by_lines
from controllers.sinara.run_artiq_script import run_artiq_in_clang64_visible

class UrukulFrequencyGenerator(FrequencyGenerator):
    """
    Implementation of class for communication with Urukul module of Sinara.
    Every script communicating with Sinara must be run through Artiq environment,
    therefore the communication here is very slow. Also, there is no support
    for parallel execution of experiments on Sinara (i.e. independent communication
    with individual instruments), so the basic idea is following. There is a number of
    template scripts implementing certain use cases, such as particle loading,
    continuous Urukul operation with monitoring experiment through Sampler etc.
    Communicating with Urukul changes certain parameters in corresponding template,
    and then runs .bat file to run the script in Artiq. This makes it VERY slow and
    unflexible.
    """

    def __init__(self, device_id: str, channel_params: Dict = None, connection_params: Dict = None):
        """
        Args:
            device_id: ID of Urukul in case there is more than 1. Not implemented for now.
            channel_params: Dictionary of channel output parameters.
                    Format: {int ch_num : {'frequency': float, 'amplitude': float, 'attenuation': float, 'on': bool}}
            connection_params: IP address of Kasli
        """
        super().__init__(device_id, connection_params)
        self.channel_params = channel_params
        self.output_updated = False
        self.connect()

    def connect(self) -> bool:
        """
        Since the communication is through Kasli, I just make sure the Kasli IP is pinged.
        Suggestion for device with more than 1 Urukul: check device_db file here.
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
            self.logger.info(f"Connected to: Urukul {self.connection_params['ip_address']}")
            self.connected = True
            return response.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error(f"Failed to connect to Urukul: Sinara can't be reached")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Urukul: error checking ping")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from Urukul - nothing to be done here"""
        return True

    def update_freq_gen_script(self, script: str, starting_line: int) -> bool:
        updates = {}
        # First we generate a dictionary with line number and new numerical value of variable at that line
        # For every Urukul channel
        for i in range(0,4):
            updates[starting_line+i] = float(self.channel_params[i]['frequency']) # Output frequency
            updates[starting_line+i+5] = float(self.channel_params[i]['amplitude']) # Channel amplitude
            updates[starting_line+i+10] = float(self.channel_params[i]['attenuation']) # Attenuation
            updates[starting_line+i+15] = self.channel_params[i]['on'] # If the channel should be on
        # Now we push the updates into the driver script
        try:
            update_script_values_by_lines(script, updates)
            self.output_updated = True
            return True
        except Exception as e:
            self.logger.error(f"Error updating the script file: {str(e)}")
            return False

    def set_frequency(self, frequency: float, channel: int = 0) -> bool:
        """Set the output frequency of Urukul."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to Urukul")
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
                self.logger.warning("Not connected to Urukul")
                return 0.0
            if not self.output_updated:
                self.logger.warning("Urukul output not up to date with driver script")
            return self.channel_params[channel]['frequency']
        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return 0.0

    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """Set the output amplitude for Urukul generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.channel_params[channel]['amplitude'] = amplitude
            self.output_updated = False
            return True
        except Exception as e:
            self.logger.error(f"Error setting amplitude: {str(e)}")
            return False

    def get_amplitude(self, channel: int = 1) -> float:
        """Get the current output amplitude for Urukul generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            if not self.output_updated:
                self.logger.warning("Urukul output not up to date with driver script")
            return self.channel_params[channel]['amplitude']
        except Exception as e:
            self.logger.error(f"Error getting amplitude: {str(e)}")
            return 0.0

    def output_on(self, channel: int = 1) -> bool:
        """Turn on the output for Urukul generator."""
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

    def output_off(self, channel: int = 1) -> bool:
        """Turn on the output for Urukul generator."""
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

    def get_output_state(self, channel: int = 1) -> bool:
        """Get the current output state for Urukul generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            if not self.output_updated:
                self.logger.warning("Urukul output not up to date with driver script")
            return self.channel_params[channel]['on']
        except Exception as e:
            self.logger.error(f"Error getting output state: {str(e)}")
            return False

    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """
        Urukul does not have this capability and only generates sine wave
        """
        self.logger.warning("Urukul only generates sine wave")
        return True

    def is_up_to_date(self):
        return self.output_updated

    def move_particles(self, detuning: float, duration: float, distance: float = 0.0) -> float:
        """
        Args:
            detuning: (Hz) Detuning between AOMs. Detuning <0 moves the particle towards science chamber
            duration: (s) How long the particle should move at given detuning.
            distance: (m) Total distance the particle should travel.
        Returns:
            distance: (m) Total distance travelled (TODO: IMPLEMENT)
        """
        script_path = 'C:/Users/CavLev/Documents/Qavity/controllers/sinara/move_particle.py'
        detuning_update_line = 15
        time_update_line = 16
        code_updates = {detuning_update_line: float(detuning), time_update_line:float(duration)}
        try:
            update_script_values_by_lines(script_path, code_updates)
            print('UPDATING SCRIPT TO MOVE PARTICLES')
            run_artiq_in_clang64_visible(script_path)
        except Exception as e:
            self.logger.error(f"Error updating the script file: {str(e)}")
        return distance
