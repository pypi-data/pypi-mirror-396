# NOTE: for status parsers: prefer to use flags when there is no bitfields in configuration description.
from enum import Flag, Enum
from typing import Any, Dict, List, Type
from can import Message
from ..base import BaseParser


class Severity(Enum):
    CRITICAL = "critical"
    INFO = "info"
    WARNING = "warning"


class Polarity(Enum):
    ACTIVE_HIGH = "active_high"  # 1 = active/problem
    ACTIVE_LOW = "active_low"    # 1 = normal/good


class StatusParserFactory:
    """Factory for creating READ-ONLY status parsers using Flag enums"""

    @classmethod
    def create_parser(cls, parser_name: str, status_config: Dict, enum_class: Type[Flag]) -> Type[BaseParser]:
        """
        Create a status parser class from configuration

        Args:
            parser_name: Name of the parser class
            status_config: Status configuration dictionary
            enum_class: Flag enum class for status bits
        """

        class DynamicStatusParser(BaseParser):
            # Add new fields
            STATUS_METADATA = status_config
            STATUS_ENUM = enum_class

            def parse_read(self, msg: Message) -> Dict:
                """Parse response message into status information"""
                if len(msg.data) < 4:
                    raise ValueError(f"{parser_name} data too short")

                status_bytes = msg.data[2:4]
                status_word = int.from_bytes(status_bytes, byteorder='little')

                # Create Flag enum from status word
                status_flags = enum_class(0)
                for flag in enum_class:
                    if self._is_flag_active(status_word, flag):
                        status_flags |= flag

                return {
                    "raw_value": status_word,
                    "status": status_flags,
                    "active_states": self._get_active_states(status_flags),
                    "has_warnings": self._has_warnings(status_flags),
                    "has_critical": self._has_critical(status_flags),
                }

            def _is_flag_active(self, status_word: int, flag: Flag) -> bool:
                """Check if a flag is active considering its polarity"""
                metadata = self.STATUS_METADATA.get(flag, {})
                # Default is ACTIVE HIGH
                polarity = metadata.get("polarity", Polarity.ACTIVE_HIGH)
                # Get exactly bit responsible for current polarity
                bit_set = bool(status_word & flag.value)
                # Evaluate
                if polarity == Polarity.ACTIVE_HIGH:
                    return bit_set  # 1 = active
                else:  # ACTIVE_LOW
                    return not bit_set  # 0 = active

            def _get_active_states(self, status: Flag) -> List[Dict]:
                """Get all active states with metadata"""
                active_states = []
                for state in self.STATUS_ENUM:
                    if state in status:
                        metadata = self.STATUS_METADATA.get(state, {})
                        active_states.append({
                            "state": state,
                            "name": metadata.get("name", state.name),
                            "description": metadata.get("description", ""),
                            "severity": metadata.get("severity")
                        })
                return active_states

            def _has_warnings(self, status: Flag) -> bool:
                """Check if any states have WARNING severity"""
                return self._check_severity(status, "warning")

            def _has_critical(self, status: Flag) -> bool:
                """Check if any states have CRITICAL severity"""
                return self._check_severity(status, "critical")

            def _check_severity(self, status: Flag, target_severity: str) -> bool:
                """Check if any active states match the target severity using bitwise operations"""
                # Get the raw integer value of active flags
                active_bits = status.value

                # Iterate only through flags that are actually present
                for state in self.STATUS_ENUM:
                    # Fast bitwise check
                    if active_bits & state.value:
                        metadata = self.STATUS_METADATA.get(state, {})
                        state_severity = metadata.get("severity")

                        if isinstance(state_severity, Enum):
                            state_severity = state_severity.value

                        if state_severity == target_severity:
                            return True

                return False

            def parse_write(self, data: Any) -> bytearray:
                raise NotImplementedError(f"{parser_name} is read-only")

        DynamicStatusParser.__name__ = parser_name
        return DynamicStatusParser
