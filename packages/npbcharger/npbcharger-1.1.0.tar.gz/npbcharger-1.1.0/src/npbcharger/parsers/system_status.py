from enum import Flag, Enum
from .factories.status_factory import StatusParserFactory, Severity, Polarity


class SystemStatus(Flag):
    DC_OK = 1 << 1        # Bit 1: The DC output status
    INITIAL_STATE = 1 << 5        # Bit 5: Initial stage indication
    EEPER = 1 << 6        # Bit 6: EEPROM access Error


# Configuration for fault status
SYSTEM_STATUS_CONFIG = {
    SystemStatus.DC_OK: {
        "name": "The DC output status",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_LOW,
    },
    SystemStatus.INITIAL_STATE: {
        "name": "Initial stage indication",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    SystemStatus.EEPER: {
        "name": "EEPROM access Error",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    }
}

# Create the parser using factory
SystemStatusParser = StatusParserFactory.create_parser(
    "SystemStatusParser",
    SYSTEM_STATUS_CONFIG,
    SystemStatus
)
