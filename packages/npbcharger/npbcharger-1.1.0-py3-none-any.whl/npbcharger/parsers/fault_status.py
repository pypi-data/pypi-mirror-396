from enum import Flag, Enum
from .factories.status_factory import StatusParserFactory, Severity, Polarity


class FaultStatus(Flag):
    OTP = 1 << 1        # Bit 1: Over temperature protection
    OVP = 1 << 2        # Bit 2: Output over voltage protection
    OLP = 1 << 3        # Bit 3: Output over current protection
    SHORT = 1 << 4      # Bit 4: Output short circuit protection
    AC_FAIL = 1 << 5    # Bit 5: AC abnormal flag
    OP_OFF = 1 << 6    # Bit 6: Output turned off
    HI_TEMP = 1 << 7    # Bit 7: Internal high temperature protection


# Configuration for fault status
FAULT_STATUS_CONFIG = {
    FaultStatus.OTP: {
        "name": "Over Temperature Protection",
        "description": "Internal temperature abnormal",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.OVP: {
        "name": "Over Voltage Protection",
        "description": "Output voltage exceeded maximum limit",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.OLP: {
        "name": "Over Current Protection",
        "description": "Output current exceeded maximum limit",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.SHORT: {
        "name": "Short Circuit Protection",
        "description": "Output short circuit detected",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.AC_FAIL: {
        "name": "AC Input Failure",
        "description": "AC input voltage abnormal or missing",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.OP_OFF: {
        "name": "Output Disabled",
        "description": "Output is turned off",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    FaultStatus.HI_TEMP: {
        "name": "High Temperature",
        "description": "Internal temperature abnormal",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    }
}

# Create the parser using factory
FaultStatusParser = StatusParserFactory.create_parser(
    "FaultStatusParser",
    FAULT_STATUS_CONFIG,
    FaultStatus
)
