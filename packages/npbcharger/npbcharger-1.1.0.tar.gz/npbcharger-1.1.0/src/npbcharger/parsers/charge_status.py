from enum import Flag
from .factories.status_factory import StatusParserFactory, Severity, Polarity


class ChargeStatus(Flag):
    """Charging status flags"""
    NTCER = 1 << 10
    BTNC = 1 << 11
    CCTOF = 1 << 13
    CVTOF = 1 << 14
    FVTOF = 1 << 15
    FULLM = 1 << 0
    CCM = 1 << 1
    CVM = 1 << 2
    FVM = 1 << 3
    WAKEUP_STOP = 1 << 6


# Configuration for charge status
CHARGE_STATUS_CONFIG = {
    ChargeStatus.NTCER: {
        "name": "NTC Short Circuit",
        "description": "Temperature compensation circuit shorted",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.BTNC: {
        "name": "No Battery",
        "description": "Battery not detected",
        "severity": Severity.CRITICAL,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.CCTOF: {
        "name": "CC Mode Timeout",
        "description": "Constant current charging timed out",
        "severity": Severity.WARNING,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.CVTOF: {
        "name": "CV Mode Timeout",
        "description": "Constant voltage charging timed out",
        "severity": Severity.WARNING,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.FVTOF: {
        "name": "Float Mode Timeout",
        "description": "Float charging timed out",
        "severity": Severity.WARNING,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.FULLM: {
        "name": "Fully Charged",
        "description": "Battery charging complete",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.CCM: {
        "name": "Constant Current Mode",
        "description": "Charging with constant current",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.CVM: {
        "name": "Constant Voltage Mode",
        "description": "Charging with constant voltage",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.FVM: {
        "name": "Float Mode",
        "description": "Maintaining battery with float voltage",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    },
    ChargeStatus.WAKEUP_STOP: {
        "name": "Wakeup Active",
        "description": "Battery wakeup sequence in progress",
        "severity": Severity.INFO,
        "polarity": Polarity.ACTIVE_HIGH,
    }
}

# Create the parser using factory
ChargeStatusParser = StatusParserFactory.create_parser(
    "ChargeStatusParser",
    CHARGE_STATUS_CONFIG,
    ChargeStatus
)
