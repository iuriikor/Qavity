"""
AnaPico APMS06G Frequency Generator Interface
--------------------------------------------
Implementation of the FrequencyGenerator interface for the AnaPico APMS06G signal generator.
"""

from typing import Dict, Optional
import logging

# Import from your base class file
from .FrequencyGenerator import FrequencyGenerator

class AnaPicoAPMS06G(FrequencyGenerator):
    """
    Implementation for AnaPico APMS06G frequency generator.

    The APMS06G is a 6 GHz signal generator with features including:
    - Frequency range: 9 kHz to 6 GHz
    - Multiple modulation types
    - Fast switching times
    - Low phase noise

    This implementation uses SCPI commands over VISA.
    """

    def __init__(self, device_id: str, connection_params: Dict = None):
        """
        Initialize the AnaPico APMS06G frequency generator.

        Args:
            device_id: VISA resource identifier for the device
            connection_params: Additional parameters for connection (timeout, etc.)
        """
        super().__init__(device_id, connection_params)
        self.visa_resource = None
        self.model = "APMS06G"

    def connect(self) -> bool:
        """
        Connect to the AnaPico APMS06G frequency generator.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            import pyvisa
            rm = pyvisa.ResourceManager()
            self.visa_resource = rm.open_resource(self.device_id)
            self.visa_resource.timeout = self.connection_params.get('timeout', 5000)

            # Test communication and verify model
            idn = self.visa_resource.query("*IDN?")
            self.logger.info(f"Connected to: {idn.strip()}")

            # Check if it's an AnaPico device
            if "ANAPICO" not in idn.upper():
                self.logger.warning(f"Connected device may not be an AnaPico device: {idn}")

            # Reset device to known state (optional)
            self.visa_resource.write("*RST")
            self.visa_resource.write("*CLS")  # Clear status registers

            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.device_id}: {str(e)}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from the AnaPico APMS06G frequency generator.

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self.visa_resource:
                # Turn off RF output before disconnecting (safety measure)
                try:
                    self.output_off()
                except:
                    pass

                self.visa_resource.close()
                self.visa_resource = None
            self.connected = False
            self.logger.info(f"Disconnected from {self.device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.device_id}: {str(e)}")
            return False

    def set_frequency(self, frequency: float, channel: int = 1) -> bool:
        """
        Set the output frequency for the AnaPico APMS06G.

        Args:
            frequency: Frequency in Hz (range: 9kHz to 6GHz)
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Check frequency range
            if frequency < 9e3 or frequency > 6e9:
                self.logger.warning(f"Frequency {frequency} Hz is outside the valid range (9kHz to 6GHz)")
                return False

            # AnaPico APMS06G uses this command format for frequency
            self.visa_resource.write(f":FREQ:CW {frequency}")
            actual_freq = self.get_frequency(channel)

            # Verify the setting was successful
            if abs(actual_freq - frequency) > 0.1:  # Allow small rounding differences
                self.logger.warning(f"Set frequency verification failed. Set: {frequency}, Read back: {actual_freq}")
                return False

            self.logger.info(f"Set frequency to {frequency} Hz on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting frequency: {str(e)}")
            return False

    def get_frequency(self, channel: int = 1) -> float:
        """
        Get the current output frequency from the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            float: Current frequency in Hz
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(":FREQ:CW?")
            frequency = float(result.strip())
            self.logger.debug(f"Current frequency is {frequency} Hz on channel {channel}")
            return frequency
        except Exception as e:
            self.logger.error(f"Error getting frequency: {str(e)}")
            return 0.0

    def set_amplitude(self, amplitude: float, channel: int = 1) -> bool:
        """
        Set the output amplitude for the AnaPico APMS06G.

        The AnaPico generator uses dBm for power settings.

        Args:
            amplitude: Amplitude in dBm (typical range: -110 to +20 dBm)
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Check amplitude range (adjust based on actual instrument specifications)
            if amplitude < -110 or amplitude > 20:
                self.logger.warning(f"Amplitude {amplitude} dBm is outside the typical range (-110 to +20 dBm)")

            # AnaPico APMS06G uses this command for power level
            self.visa_resource.write(f":POW:LEV {amplitude}")
            actual_ampl = self.get_amplitude(channel)

            # Verify the setting was successful
            if abs(actual_ampl - amplitude) > 0.1:  # Allow small rounding differences
                self.logger.warning(f"Set amplitude verification failed. Set: {amplitude}, Read back: {actual_ampl}")
                return False

            self.logger.info(f"Set amplitude to {amplitude} dBm on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting amplitude: {str(e)}")
            return False

    def get_amplitude(self, channel: int = 1) -> float:
        """
        Get the current output amplitude from the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            float: Current amplitude in dBm
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(":POW:LEV?")
            amplitude = float(result.strip())
            self.logger.debug(f"Current amplitude is {amplitude} dBm on channel {channel}")
            return amplitude
        except Exception as e:
            self.logger.error(f"Error getting amplitude: {str(e)}")
            return 0.0

    def output_on(self, channel: int = 1) -> bool:
        """
        Turn on the RF output for the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(":OUTP ON")

            # Verify the setting was successful
            if not self.get_output_state(channel):
                self.logger.warning(f"Failed to turn output ON for channel {channel}")
                return False

            self.logger.info(f"Turned output ON for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output on: {str(e)}")
            return False

    def output_off(self, channel: int = 1) -> bool:
        """
        Turn off the RF output for the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            self.visa_resource.write(":OUTP OFF")

            # Verify the setting was successful
            if self.get_output_state(channel):
                self.logger.warning(f"Failed to turn output OFF for channel {channel}")
                return False

            self.logger.info(f"Turned output OFF for channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error turning output off: {str(e)}")
            return False

    def get_output_state(self, channel: int = 1) -> bool:
        """
        Get the current RF output state for the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            bool: True if output is on, False if off
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            result = self.visa_resource.query(":OUTP?")
            state = bool(int(result.strip()))
            self.logger.debug(f"Output state is {'ON' if state else 'OFF'} for channel {channel}")
            return state
        except Exception as e:
            self.logger.error(f"Error getting output state: {str(e)}")
            return False

    def set_waveform(self, waveform: str, channel: int = 1) -> bool:
        """
        Set the output waveform type for the AnaPico APMS06G.

        Note: The APMS06G primarily functions as a CW/modulated sine wave generator.
        This method mostly exists for interface compatibility but has limited
        functionality on this particular device.

        Args:
            waveform: Waveform type ('sine' is the primary supported type)
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # The APMS is primarily a sine wave generator
            if waveform.lower() != 'sine':
                self.logger.warning(f"Waveform '{waveform}' not fully supported by APMS06G. Using sine wave.")

            # There isn't a direct command to set waveform type on this device
            # as it's primarily a sine wave generator with modulation capabilities
            self.logger.info(f"Using sine waveform (default for APMS06G)")
            return True
        except Exception as e:
            self.logger.error(f"Error with waveform setting: {str(e)}")
            return False

    # AnaPico APMS06G specific methods below

    def set_phase(self, phase: float, channel: int = 1) -> bool:
        """
        Set the phase offset for the AnaPico APMS06G.

        Args:
            phase: Phase offset in degrees (-360 to 360)
            channel: Output channel number (default: 1)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Normalize phase to -360 to 360 range
            phase = ((phase + 360) % 720) - 360

            self.visa_resource.write(f":PHAS {phase}")
            self.logger.info(f"Set phase to {phase} degrees on channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting phase: {str(e)}")
            return False

    def get_phase(self, channel: int = 1) -> float:
        """
        Get the current phase offset for the AnaPico APMS06G.

        Args:
            channel: Output channel number (default: 1)

        Returns:
            float: Current phase offset in degrees
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return 0.0

            result = self.visa_resource.query(":PHAS?")
            phase = float(result.strip())
            self.logger.debug(f"Current phase is {phase} degrees on channel {channel}")
            return phase
        except Exception as e:
            self.logger.error(f"Error getting phase: {str(e)}")
            return 0.0

    def set_reference_source(self, source: str) -> bool:
        """
        Set the reference frequency source for the AnaPico APMS06G.

        Args:
            source: Reference source ('INT' for internal, 'EXT' for external)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            if source.upper() not in ['INT', 'EXT']:
                self.logger.error(f"Invalid reference source: {source}. Must be 'INT' or 'EXT'")
                return False

            self.visa_resource.write(f":ROSC:SOUR {source.upper()}")
            self.logger.info(f"Set reference source to {source.upper()}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting reference source: {str(e)}")
            return False

    def get_reference_source(self) -> str:
        """
        Get the current reference frequency source for the AnaPico APMS06G.

        Returns:
            str: Current reference source ('INT' or 'EXT')
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return "Unknown"

            result = self.visa_resource.query(":ROSC:SOUR?")
            source = result.strip()
            self.logger.debug(f"Current reference source is {source}")
            return source
        except Exception as e:
            self.logger.error(f"Error getting reference source: {str(e)}")
            return "Unknown"

    def enable_modulation(self, mod_type: str, state: bool = True) -> bool:
        """
        Enable or disable a specific modulation on the AnaPico APMS06G.

        Args:
            mod_type: Modulation type ('AM', 'FM', 'PM', 'PULM')
            state: True to enable, False to disable

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            mod_type = mod_type.upper()
            if mod_type not in ['AM', 'FM', 'PM', 'PULM']:
                self.logger.error(f"Invalid modulation type: {mod_type}")
                return False

            state_str = "ON" if state else "OFF"
            self.visa_resource.write(f":{mod_type}:STAT {state_str}")
            self.logger.info(f"Set {mod_type} modulation to {state_str}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting modulation state: {str(e)}")
            return False

    def set_pulse_parameters(self, period: float, width: float) -> bool:
        """
        Set pulse modulation parameters for the AnaPico APMS06G.

        Args:
            period: Pulse period in seconds
            width: Pulse width in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Set pulse period
            self.visa_resource.write(f":PULM:PER {period}")

            # Set pulse width
            self.visa_resource.write(f":PULM:WIDT {width}")

            self.logger.info(f"Set pulse parameters - Period: {period}s, Width: {width}s")
            return True
        except Exception as e:
            self.logger.error(f"Error setting pulse parameters: {str(e)}")
            return False

    def set_sweep_parameters(self, start_freq: float, stop_freq: float, step_freq: float, dwell_time: float) -> bool:
        """
        Configure frequency sweep parameters for the AnaPico APMS06G.

        Args:
            start_freq: Start frequency in Hz
            stop_freq: Stop frequency in Hz
            step_freq: Step frequency in Hz
            dwell_time: Dwell time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Check frequency ranges
            if start_freq < 9e3 or start_freq > 6e9 or stop_freq < 9e3 or stop_freq > 6e9:
                self.logger.warning(f"Frequency values outside valid range (9kHz to 6GHz)")
                return False

            # Set sweep mode to STEP
            self.visa_resource.write(":FREQ:MODE SWE")
            self.visa_resource.write(":SWE:GEN STEP")

            # Set frequency parameters
            self.visa_resource.write(f":FREQ:STAR {start_freq}")
            self.visa_resource.write(f":FREQ:STOP {stop_freq}")
            self.visa_resource.write(f":SWE:STEP:LIN {step_freq}")

            # Set dwell time
            self.visa_resource.write(f":SWE:DWEL {dwell_time}")

            self.logger.info(
                f"Set sweep parameters - Start: {start_freq}Hz, Stop: {stop_freq}Hz, Step: {step_freq}Hz, Dwell: {dwell_time}s")
            return True
        except Exception as e:
            self.logger.error(f"Error setting sweep parameters: {str(e)}")
            return False

    def start_sweep(self) -> bool:
        """
        Start frequency sweep on the AnaPico APMS06G.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Ensure RF output is on
            self.output_on()

            # Start the sweep
            self.visa_resource.write(":INIT:IMM")

            self.logger.info("Started frequency sweep")
            return True
        except Exception as e:
            self.logger.error(f"Error starting sweep: {str(e)}")
            return False

    def stop_sweep(self) -> bool:
        """
        Stop frequency sweep and return to CW mode on the AnaPico APMS06G.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Return to CW mode
            self.visa_resource.write(":FREQ:MODE CW")

            self.logger.info("Stopped frequency sweep and returned to CW mode")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping sweep: {str(e)}")
            return False

    def reset(self) -> bool:
        """
        Reset the AnaPico APMS06G to default settings.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connected:
                self.logger.warning("Not connected to device")
                return False

            # Send reset command
            self.visa_resource.write("*RST")
            self.visa_resource.write("*CLS")

            # Wait for reset to complete
            self.visa_resource.query("*OPC?")

            self.logger.info(f"Reset device {self.device_id} to default settings")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting device: {str(e)}")
            return False


# Example usage
def main():
    """Example usage of the AnaPico APMS06G frequency generator interface."""

    # Example VISA address - update with your actual device address
    device_address = "TCPIP0::192.168.1.101::inst0::INSTR"

    # Create a connection with a longer timeout for initial connection
    connection_params = {'timeout': 10000}  # 10 seconds

    generator = AnaPicoAPMS06G(device_address, connection_params)

    try:
        # Connect to the device
        if generator.connect():
            print("Connected to AnaPico APMS06G")

            # Configure the generator
            generator.set_frequency(2.45e9)  # 2.45 GHz
            generator.set_amplitude(10)  # 10 dBm
            generator.set_phase(45)  # 45 degrees phase

            # Turn on output
            generator.output_on()

            # Read back settings
            freq = generator.get_frequency()
            ampl = generator.get_amplitude()
            phase = generator.get_phase()
            state = generator.get_output_state()

            print(f"Current settings:")
            print(f"  Frequency: {freq / 1e6:.6f} MHz")
            print(f"  Amplitude: {ampl:.2f} dBm")
            print(f"  Phase: {phase:.2f} degrees")
            print(f"  Output: {'ON' if state else 'OFF'}")

            # Example of sweep configuration
            print("\nConfiguring frequency sweep...")
            generator.set_sweep_parameters(
                start_freq=1e9,  # 1 GHz
                stop_freq=2e9,  # 2 GHz
                step_freq=10e6,  # 10 MHz steps
                dwell_time=0.1  # 100 ms dwell time
            )

            # Start sweep
            generator.start_sweep()

            # Wait for some time
            import time
            print("Sweeping frequencies for 5 seconds...")
            time.sleep(5)

            # Stop sweep and return to CW mode
            generator.stop_sweep()

            # Set back to a fixed frequency
            generator.set_frequency(1e9)  # 1 GHz

            # Turn off RF output
            generator.output_off()
        else:
            print("Failed to connect to AnaPico APMS06G")

    finally:
        # Always disconnect properly
        if generator.connected:
            generator.disconnect()
            print("Disconnected from AnaPico APMS06G")


if __name__ == "__main__":
    main()
