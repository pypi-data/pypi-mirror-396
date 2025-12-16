from typing import Any
from can import Message
from .base import BaseParser
from ..commands import COMMAND_LEN


class BytesForward(BaseParser):
    """
    Parser for manufacturer data strings (like serial number or model ID).
    Reads the 6 data bytes and returns them as a bytearray.
    """
    raw_data_len = 6

    def __init__(self, data_len: int = 6):
        self.raw_data_len = COMMAND_LEN + data_len

    def parse_read(self, msg: Message) -> bytearray:
        # Check total message length
        if len(msg.data) < self.raw_data_len:
            raise ValueError(
                f"Manufacturer data too short (Expected {self.raw_data_len} bytes)")

        raw_data = msg.data[COMMAND_LEN:self.raw_data_len]

        return raw_data

    def parse_write(self, data: Any) -> bytearray:
        raise NotImplementedError("Manufacturer string data is read only.")
