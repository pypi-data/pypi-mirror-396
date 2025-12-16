from enum import Enum
from typing import Any, Dict, Type
from can import Message
from ..base import BaseParser


class FieldType(Enum):
    FLAG = "flag"
    BITS = "bits"
    VALUE = "value"


class ConfigParserFactory:
    """Factory for creating READ/WRITE configuration parsers"""

    @classmethod
    def create_parser(cls, parser_name: str, config: Dict) -> Type[BaseParser]:
        """
        Create a configuration parser with read/write support

        Args:
            parser_name: Name of the parser class
            config: Field configuration dictionary
            command_byte: Command byte for write operations
        """

        class DynamicConfigParser(BaseParser):
            # Add new field
            CONFIG = config

            def parse_read(self, msg: Message) -> Dict:
                """Parse response message into field values"""
                if len(msg.data) < 4:
                    raise ValueError(f"{parser_name} data too short")

                value_bytes = msg.data[2:4]
                value_word = int.from_bytes(value_bytes, byteorder='little')

                return {
                    "raw_value": value_word,
                    "fields": self._parse_fields(value_word),
                }

            def parse_write(self, data: Any) -> bytearray:
                """Convert field data to bytearray for sending - OVERWRITES EVERYTHING"""
                if isinstance(data, dict):
                    # Without current state, we can only do complete overwrite
                    value_word = self._build_value_word(data)
                else:
                    value_word = data

                value_bytes = value_word.to_bytes(2, byteorder='little')
                return bytearray(value_bytes)

            def parse_write_update(self, data: Any, current_state: int) -> bytearray:
                """Convert field data to bytearray for sending - updates specific fields"""
                value_word = self._build_value_word(data, current_state)
                value_bytes = value_word.to_bytes(2, byteorder='little')
                return bytearray(value_bytes)

            def _parse_fields(self, value_word: int) -> Dict:
                """Parse all configured fields from the value word"""
                fields = {}

                for field_name, field_config in self.CONFIG.items():
                    field_type = field_config.get("type", FieldType.FLAG)

                    if field_type == FieldType.FLAG:
                        bit_position = field_config["bit"]
                        fields[field_name] = bool(
                            value_word & (1 << bit_position))

                    elif field_type == FieldType.BITS:
                        bit_mask = field_config["mask"]
                        bit_shift = field_config.get("shift", 0)
                        field_value = (value_word & bit_mask) >> bit_shift

                        # Map to human-readable values
                        value_map = field_config.get("values", {})
                        fields[field_name] = value_map.get(
                            field_value, field_value)

                    elif field_type == FieldType.VALUE:
                        bit_mask = field_config["mask"]
                        bit_shift = field_config.get("shift", 0)
                        fields[field_name] = (
                            value_word & bit_mask) >> bit_shift

                return fields

            def _build_value_word(self, field_data: Dict, current_state: int = 0) -> int:
                """Build value word from field values - modifies current state"""
                value_word = current_state  # Start from current state

                for field_name, value in field_data.items():
                    if field_name not in self.CONFIG:
                        continue

                    config = self.CONFIG[field_name]
                    field_type = config.get("type", FieldType.FLAG)

                    if field_type == FieldType.FLAG:
                        if value:
                            value_word |= (1 << config["bit"])
                        else:
                            # Clear the bit if False
                            value_word &= ~(1 << config["bit"])

                    elif field_type in (FieldType.BITS, FieldType.VALUE):
                        bit_mask = config["mask"]
                        bit_shift = config.get("shift", 0)

                        # Clear then set only the target field
                        value_word &= ~bit_mask
                        value_word |= (value << bit_shift) & bit_mask

                return value_word

        DynamicConfigParser.__name__ = parser_name
        return DynamicConfigParser
