from typing import Any, Dict, Optional
from can import Message
from .base import BaseParser
from ..commands import COMMAND_LEN, CURVE_F


class ElectricDataParser(BaseParser):
    scaling_factor: float
    raw_data_len: int

    def __init__(self,
                 scaling_factor: float = CURVE_F,
                 constraints: Optional[Dict[str, Any]] = None, raw_data_len=4):
        self.scaling_factor = scaling_factor
        self.constraints = constraints or {}
        self.raw_data_len = raw_data_len

    def parse_read(self, msg: Message) -> float:
        raw_data_address = msg.data
        if len(raw_data_address) < self.raw_data_len:
            raise ValueError("Fault status data too short")
        raw_data = raw_data_address[2:self.raw_data_len]

        raw_value = int.from_bytes(raw_data, byteorder='little')

        return raw_value * self.scaling_factor

    def parse_write(self, data: float) -> bytearray:
        min_v = self.constraints.get('min')
        max_v = self.constraints.get('max')

        if min_v is not None:
            data = max(min_v, data)
        if max_v is not None:
            data = min(data, max_v)

        data = round(data, 2)
        raw_value = int(data / self.scaling_factor)
        return bytearray(raw_value.to_bytes(self.raw_data_len - COMMAND_LEN, byteorder='little'))
