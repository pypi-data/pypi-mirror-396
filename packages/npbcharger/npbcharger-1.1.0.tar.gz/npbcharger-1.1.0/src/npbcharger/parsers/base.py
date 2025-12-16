from abc import ABC, abstractmethod
from enum import Flag
from typing import Any, Dict, List
from can import Message


class BaseParser(ABC):
    """Abstract base class for all parsers"""

    @abstractmethod
    def parse_read(self, msg: Message) -> Any:
        """Parse response message into meaningful data"""
        pass

    @abstractmethod
    def parse_write(self, data: Any) -> bytearray:
        """Convert data to bytearray for sending"""
        pass
