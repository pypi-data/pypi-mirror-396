import sys
from time import sleep
import can
from can import BusABC
from .commands import NPB1700Commands
from .exceptions import NPBCommunicationError

# Max. response time (PSU/CHG to Controller): 5mSec
MAX_RESPONCE_TIME: float = 0.005

# Min. request period (Controller to PSU/CHG): 20mSec
MIN_REQUEST_PERIOD: float = 0.02

# Min. packet margin time (Controller to PSU/CHG): 5mSec
MIN_MARGIN_TIME: float = 0.005

class NPB1700:
    # Private can communication related
    __interface: str
    __channel: str = "/dev/ttyACMx"
    __tty_baudrate: int = 1000000
    __bitrate: int = 250000
    __device_id: int = 0x000C0103
    __can_bus: BusABC
    is_broadcast: bool = False

    """ Initializes npb1700 can bus instance & id
    
    :param channel: path to device which connected by CAN to NPB-1700
    :param tty_baudrate: baudrate of your device -> CAN adapter
    :param device_id: id of NPB-1700 read documentation to set correct id
    """

    def __init__(self, channel: str, interface: str, tty_baudrate: int = 1000000 , device_id: int = 0x000C0103):
        self.__channel = channel
        self.__tty_baudrate = tty_baudrate
        self.__device_id = device_id
        self.__interface = interface

        # Handle broadcast drivers
        addressMask: int = 0x000000FF
        self.is_broadcast = (self.__device_id & addressMask) == 0xFF

        try:
            self.__can_bus = can.Bus(interface=self.__interface, channel=self.__channel,
                                     ttyBaudrate=self.__tty_baudrate, bitrate=self.__bitrate)
        except can.exceptions.CanInitializationError as e:
            print(f"Failed to initialize CAN bus on {self.__channel}: {e}")
            sys.exit(1)
        except Exception as e:  # Catch any other unexpected error during instantiation
            print(
                f"An unexpected error occurred while creating NPB1700 instance: {e}")
            sys.exit(1)

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point (shuts down the bus)."""
        if hasattr(self, '_NPB1700__can_bus'):
            print(f"Shutting down CAN bus on {self.__channel}...")
            self.__can_bus.shutdown()
        # Return False to propagate any exceptions that occurred
        return False

    def spin(self, msg: can.Message, have_response: bool = True) -> can.Message:
        self.__can_bus.send(msg)
        # For debug purposes
        # print(f"Message sent on {self.__can_bus.channel_info}")
        if have_response:
            rec_msg: can.Message | None = self.__can_bus.recv(timeout=MAX_RESPONCE_TIME)
            if rec_msg is not None:
                # For debug purposes
                # print(f"Message received on {self.__can_bus.channel_info}")
                sleep(MIN_MARGIN_TIME)
                return rec_msg
            raise NPBCommunicationError
        sleep(MIN_MARGIN_TIME)
        return can.Message()

    def _create_msg(self, command: NPB1700Commands, params: bytearray = bytearray()) -> can.Message:
        dlc: int = len(command.value) + len(params)
        data: bytearray = command.value + params
        return can.Message(arbitration_id=self.__device_id, dlc=dlc, data=data, is_extended_id=True, check=True)

    def read(self, command: NPB1700Commands) -> can.Message:
        can_msg: can.Message = self._create_msg(command)
        # Send message and check if it failed
        # Max. response time (PSU/CHG to Controller): 5mSec
        rec_msg: can.Message = self.spin(can_msg, not(self.is_broadcast))
        return rec_msg

    def write(self, command: NPB1700Commands, params: bytearray) -> can.Message:
        can_msg: can.Message = self._create_msg(command, params)
        # Max. response time (PSU/CHG to Controller): 5mSec
        rec_msg: can.Message = self.spin(can_msg, False)
        if rec_msg.error_state_indicator:
            raise NPBCommunicationError
        return rec_msg
