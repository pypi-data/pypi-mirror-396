from .factories.config_factory import FieldType, ConfigParserFactory

SYSTEM_CONFIG = {
    # Low byte field
    "OPERATION_INIT": {
        "type": FieldType.BITS,
        "mask": 0x06,  # Bits 1-2 of low byte
        "shift": 1,
        "name": "Initial operational behavior",
        "description": "Initial operational behavior",
        "values": {
            0: "Power on with 00h: OFF",
            1: "Power on with 01h: ON",
            2: "Power on with the last setting",
            3: "No used"
        }
    },

    # High byte field
    "EEP_OFF": {
        "type": FieldType.FLAG,
        "bit": 10,  # Bit 1 of high byte
        "name": "Disable to write voltage and current parameters to EEPROM",
        "description": "0 - Write the voltage and current parameters into EEPROM in real time"
    },
}

SystemConfigParser = ConfigParserFactory.create_parser(
    "SystemConfigParser",
    SYSTEM_CONFIG,
    # No enum_class parameter for field-based parsers
)
