from typing import Optional, Dict, List, Union, Tuple
import dae_RelayBoard
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DAE_Relay_Board")


class RelayBoard(object):

    def __init__(self, comport: str, output_ports: Dict = None):
        """
        :param comport: COM port the device is connected to. Example: "COM4"
        :param output_ports: dictionary of the form "Name": number, where Name is the short descriptive name
            of the relay board port of corresponding number. For internal use only
        """
        self.board = None
        self.comport = comport
        self._output_ports = output_ports
        self.logger = logging.getLogger("DAE_Relay_Board")
        self.initialised = False
        try:
            self.board = dae_RelayBoard.DAE_RelayBoard(dae_RelayBoard.DAE_RELAYBOARD_TYPE_16)
            self.board.initialise(self.comport)
            self.initialised = True
        except Exception as e:
            self.logger.error(f"Error connecting to the relay board on {self.comport}: {str(e)}")
            self.initialised = False


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disconnects from the device."""
        self.board.disconnect()

    def open_port(self, port_number:int = None, port_name:str = None) -> bool:
        """
        Opens a port specified by either port number OR port name

        :param port_number: either specify a port number
        :param port_name: or specify a port name that is already in the _output_ports dictionary
        :return: bool True if action is successful, False otherwise
        """
        try:
            if port_number:
                self.board.setState(port_number, True)
            if port_name:
                if port_name in self._output_ports:
                    self.board.setState(self._output_ports[port_name], True)
                else:
                    self.logger.warning(f"Port {port_name} not found in the _output_ports dictionary")
            return True
        except Exception as e:
            self.logger.error(f"Error opening relay port: {e}")
            return False

    def close_port(self, port_number=None, port_name=None) -> bool:
        """
        Closes a port specified by either port number OR port name

        :param port_number: either specify a port number
        :param port_name: or specify a port name that is already in the _output_ports dictionary
        :return: bool True if action is successful, False otherwise
        """
        try:
            if port_number:
                self.board.setState(port_number, False)
            if port_name:
                if port_name in self._output_ports:
                    self.board.setState(self._output_ports[port_name], False)
                else:
                    self.logger.warning(f"Port {port_name} not found in the _output_ports dictionary")
            return True
        except Exception as e:
            self.logger.error(f"Error opening relay port: {e}")
            return False

    def pump_for_nseconds(self, pump_time: float = 1.0) -> bool:
        """
        :param pump_time: duration of pumpdown
        :return: bool True if action is successful, False otherwise
        """
        try:
            # Close loading port to prevent overloading the pump
            self.board.setState(self._output_ports["Load"], False)
            self.board.setState(self._output_ports["Pump"], True)
            time.sleep(pump_time)
            self.board.setState(self._output_ports["Pump"], False)
            return True
        except Exception as e:
            self.logger.error(f"Error pumping: {e}")
            return False

    def load_for_nseconds(self, load_time: float = 1.0) -> bool:
        """
        :param load_time: duration of pumpdown
        :return: bool True if action is successful, False otherwise
        """
        try:
            # Close pumping port to prevent overloading the pump
            self.board.setState(self._output_ports["Pump"], False)
            self.board.setState(self._output_ports["Load"], True)
            time.sleep(load_time)
            self.board.setState(self._output_ports["Load"], False)
            return True
        except Exception as e:
            self.logger.error(f"Error pumping: {e}")
            return False

    def vent_for_nseconds(self, vent_time: float = 1.0) -> bool:
        """
        :param vent_time: duration of pumpdown
        :return: bool True if action is successful, False otherwise
        """
        try:
            # Close pumping port to prevent overloading the pump
            self.board.setState(self._output_ports["Pump"], False)
            self.board.setState(self._output_ports["Vent"], True)
            time.sleep(vent_time)
            self.board.setState(self._output_ports["Vent"], False)
            return True
        except Exception as e:
            self.logger.error(f"Error pumping: {e}")
            return False

    def get_state(self, ch_num: int) -> bool:
        """
        Gets the state of a relay with NUMBER ch_num
        :param ch_num: number of channel
        :return: True if relay is open, False otherwise
        """
        try:
            return self.board.getState(ch_num)
        except Exception as e:
            self.logger.error(f"Error getting relay state: {e}")
            return False

    def get_port_state(self, port_name: str) -> bool:
        """
        Gets the state of a relay with DESCRIPTION port_name
        :param port_name: port name. Must be in the _output_ports dictionary keys
        :return: True if relay is open, False otherwise
        """
        try:
            return self.board.getState(self._output_ports[port_name])
        except Exception as e:
            self.logger.error(f"Error getting relay state: {e}")
            return None