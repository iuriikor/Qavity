"""
Frequency Generator Interface
-----------------------------
A Python interface for controlling various frequency generator models in the lab.
"""

import abc
import time
import logging
from typing import Optional, Dict, List, Union, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FreqGenInterface")
logger.setLevel(logging.WARNING)


class FrequencyGenerator(abc.ABC):
    """
    Abstract base class for frequency generators.
    Defines the common interface that all generator models should implement.
    """

    def __init__(self, device_id: str, connection_params: Dict = None):
        """
        Initialize the frequency generator.

        Args:
            device_id: Identifier for the device (e.g., VISA address, serial number)
            connection_params: Additional parameters needed for connection
        """
        self.device_id = device_id
        self.connection_params = connection_params or {}
        self.connected = False
        self.logger = logging.getLogger(f"FreqGenInterface.{self.__class__.__name__}")

    def __enter__(self):
        """Context manager entry - connects to the device."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disconnects from the device."""
        self.disconnect()

    @abc.abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the frequency generator.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the frequency generator.

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def set_frequency(self, frequency: float, channel: int = 1) -> bool:
        """
        Set the output frequency.

        Args:
            frequency: Frequency in Hz
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_frequency(self, channel: int = 1) -> float:
        """
        Get the current output frequency.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            float: Current frequency in Hz
        """
        pass

    @abc.abstractmethod
    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """
        Set the output amplitude.

        Args:
            amplitude: Amplitude in Volts peak-to-peak
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_amplitude(self, channel: int = 1) -> float:
        """
        Get the current output amplitude.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            float: Current amplitude in Volts peak-to-peak
        """
        pass

    @abc.abstractmethod
    def output_on(self, channel: int = 1) -> bool:
        """
        Turn on the signal output.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def output_off(self, channel: int = 1) -> bool:
        """
        Turn off the signal output.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_output_state(self, channel: int = 1) -> bool:
        """
        Get the current output state.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if output is on, False if off
        """
        pass

    @abc.abstractmethod
    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """
        Set the output waveform type.

        Args:
            waveform: Waveform type (e.g., 'sine', 'square', 'triangle', 'ramp')
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def reset(self) -> bool:
        """
        Reset the device to default settings.

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Resetting device {self.device_id}")
        # Implementation may vary by device, but this is a common approach
        return True

    def get_device_info(self) -> Dict:
        """
        Get device information.

        Returns:
            Dict: Dictionary containing device information
        """
        return {
            "device_id": self.device_id,
            "connected": self.connected,
            "type": self.__class__.__name__
        }


# Example implementation for a specific device model (using VISA)
class AgilentFrequencyGenerator(FrequencyGenerator):
    """
    Implementation for Agilent/Keysight frequency generators.
    Uses VISA for communication.
    """

    def __init__(self, device_id: str, connection_params: Dict = None):
        super().__init__(device_id, connection_params)
        self.visa_resource = None

    def connect(self) -> bool:
        """Connect to the Agilent frequency generator."""
        try:
            import pyvisa
            rm = pyvisa.ResourceManager()
            self.visa_resource = rm.open_resource(self.device_id)
            self.visa_resource.timeout = self.connection_params.get('timeout', 5000)

            # Test communication
            idn = self.visa_resource.query("*IDN?")
            self.logger.info(f"Connected to: {idn.strip()}")
            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.device_id}: {str(e)}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from the Agilent frequency generator."""
        try:
            if self.visa_resource:
                self.visa_resource.close()
                self.visa_resource = None
            self.connected = False
            self.logger.info(f"Disconnected from {self.device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.device_id}: {str(e)}")
            return False

    def set_frequency(self, frequency: float, channel: int = 1) -> bool:
        """Set the output frequency for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"SOURce{channel}:FREQuency {frequency}")
            self.logger.info(f"Set frequency to {frequency} Hz on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting frequency: {str(e)}")
            return False

    def get_frequency(self, channel: int = 1) -> float:
        """Get the current output frequency for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(f"SOURce{channel}:FREQuency?")
            frequency = float(result.strip())
            self.logger.debug(f"Current frequency is {frequency} Hz on channel {channel}")
            return frequency
        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return 0.0

    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """Set the output amplitude for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"SOURce{channel}:VOLTage {amplitude}")
            self.logger.info(f"Set amplitude to {amplitude} Vpp on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting amplitude: {str(e)}")
            return False

    def get_amplitude(self, channel: int = 1) -> float:
        """Get the current output amplitude for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(f"SOURce{channel}:VOLTage?")
            amplitude = float(result.strip())
            self.logger.debug(f"Current amplitude is {amplitude} Vpp on channel {channel}")
            return amplitude
        except Exception as e:
            self.logger.error(f"Error getting amplitude: {str(e)}")
            return 0.0

    def output_on(self, channel: int = 1) -> bool:
        """Turn on the output for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"OUTPut{channel} ON")
            self.logger.info(f"Turned output ON for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output on: {str(e)}")
            return False

    def output_off(self, channel: int = 1) -> bool:
        """Turn off the output for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"OUTPut{channel} OFF")
            self.logger.info(f"Turned output OFF for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output off: {str(e)}")
            return False

    def get_output_state(self, channel: int = 1) -> bool:
        """Get the current output state for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            result = self.visa_resource.query(f"OUTPut{channel}?")
            state = bool(int(result.strip()))
            self.logger.debug(f"Output state is {'ON' if state else 'OFF'} for channel {channel}")
            return state
        except Exception as e:
            self.logger.error(f"Error getting output state: {str(e)}")
            return False

    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """Set the output waveform type for Agilent generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            waveform_map = {
                'sine': 'SIN',
                'square': 'SQU',
                'triangle': 'TRI',
                'ramp': 'RAMP',
                'pulse': 'PULS',
                'noise': 'NOIS',
                'dc': 'DC'
            }

            if waveform.lower() not in waveform_map:
                self.logger.error(f"Unsupported waveform type: {waveform}")
                return False

            cmd = waveform_map[waveform.lower()]
            self.visa_resource.write(f"SOURce{channel}:FUNCtion {cmd}")
            self.logger.info(f"Set waveform to {waveform} on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting waveform: {str(e)}")
            return False


# Example of another implementation for a different device model
class RhodeSchwarzFrequencyGenerator(FrequencyGenerator):
    """
    Implementation for Rhode & Schwarz frequency generators.
    Uses SCPI commands over VISA.
    """

    def __init__(self, device_id: str, connection_params: Dict = None):
        super().__init__(device_id, connection_params)
        self.visa_resource = None

    def connect(self) -> bool:
        """Connect to the Rhode & Schwarz frequency generator."""
        try:
            import pyvisa
            rm = pyvisa.ResourceManager()
            self.visa_resource = rm.open_resource(self.device_id)
            self.visa_resource.timeout = self.connection_params.get('timeout', 5000)

            # Test communication
            idn = self.visa_resource.query("*IDN?")
            self.logger.info(f"Connected to: {idn.strip()}")
            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.device_id}: {str(e)}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from the Rhode & Schwarz frequency generator."""
        try:
            if self.visa_resource:
                self.visa_resource.close()
                self.visa_resource = None
            self.connected = False
            self.logger.info(f"Disconnected from {self.device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.device_id}: {str(e)}")
            return False

    def set_frequency(self, frequency: float, channel: int = 1) -> bool:
        """Set the output frequency for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # R&S syntax may differ from Agilent
            self.visa_resource.write(f"SOUR{channel}:FREQ {frequency}")
            self.logger.info(f"Set frequency to {frequency} Hz on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting frequency: {str(e)}")
            return False

    def get_frequency(self, channel: int = 1) -> float:
        """Get the current output frequency for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(f"SOUR{channel}:FREQ?")
            frequency = float(result.strip())
            self.logger.debug(f"Current frequency is {frequency} Hz on channel {channel}")
            return frequency
        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return 0.0

    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """Set the output amplitude for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"SOUR{channel}:VOLT {amplitude}")
            self.logger.info(f"Set amplitude to {amplitude} Vpp on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting amplitude: {str(e)}")
            return False

    def get_amplitude(self, channel: int = 1) -> float:
        """Get the current output amplitude for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(f"SOUR{channel}:VOLT?")
            amplitude = float(result.strip())
            self.logger.debug(f"Current amplitude is {amplitude} Vpp on channel {channel}")
            return amplitude
        except Exception as e:
            self.logger.error(f"Error getting amplitude: {str(e)}")
            return 0.0

    def output_on(self, channel: int = 1) -> bool:
        """Turn on the output for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"OUTP{channel}:STAT ON")
            self.logger.info(f"Turned output ON for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output on: {str(e)}")
            return False

    def output_off(self, channel: int = 1) -> bool:
        """Turn off the output for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(f"OUTP{channel}:STAT OFF")
            self.logger.info(f"Turned output OFF for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output off: {str(e)}")
            return False

    def get_output_state(self, channel: int = 1) -> bool:
        """Get the current output state for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            result = self.visa_resource.query(f"OUTP{channel}:STAT?")
            state = bool(int(result.strip()))
            self.logger.debug(f"Output state is {'ON' if state else 'OFF'} for channel {channel}")
            return state
        except Exception as e:
            self.logger.error(f"Error getting output state: {str(e)}")
            return False

    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """Set the output waveform type for R&S generator."""
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            waveform_map = {
                'sine': 'SIN',
                'square': 'SQU',
                'triangle': 'TRI',
                'ramp': 'RAMP',
                'pulse': 'PULS',
                'noise': 'NOIS'
            }

            if waveform.lower() not in waveform_map:
                self.logger.error(f"Unsupported waveform type: {waveform}")
                return False

            cmd = waveform_map[waveform.lower()]
            self.visa_resource.write(f"SOUR{channel}:FUNC {cmd}")
            self.logger.info(f"Set waveform to {waveform} on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting waveform: {str(e)}")
            return False


# Usage example
def main():
    """Example usage of the frequency generator interface."""

    # Example with Agilent/Keysight generator
    agilent_address = "TCPIP0::192.168.1.5::inst0::INSTR"  # Example VISA address

    with AgilentFrequencyGenerator(agilent_address) as gen:
        if gen.connected:
            # Configure the generator
            gen.set_frequency(10e6)  # 10 MHz
            gen.set_amplitude(2.0)  # 2 Vpp
            gen.set_waveform('sine')

            # Turn on output
            gen.output_on()

            # Wait a bit
            time.sleep(5)

            # Turn off output
            gen.output_off()

    # Example with Rhode & Schwarz generator
    rs_address = "GPIB0::20::INSTR"  # Example VISA address

    try:
        rs_gen = RhodeSchwarzFrequencyGenerator(rs_address)
        rs_gen.connect()

        if rs_gen.connected:
            # Configure the generator
            rs_gen.set_frequency(5e6)  # 5 MHz
            rs_gen.set_amplitude(1.5)  # 1.5 Vpp
            rs_gen.set_waveform('square')

            # Turn on output
            rs_gen.output_on()

            # Wait a bit
            time.sleep(5)

            # Turn off output
            rs_gen.output_off()
    finally:
        # Clean up
        if rs_gen.connected:
            rs_gen.disconnect()


if __name__ == "__main__":
    main()
