from .factories.config_factory import FieldType, ConfigParserFactory

CURVE_CONFIG = {
    # High byte fields
    "CCTOE": {
        "type": FieldType.FLAG,
        "bit": 8,  # Bit 0 of high byte
        "name": "Constant Voltage Timeout Enable",
        "description": "Constant voltage stage timeout indication enable"
    },
    "CVTOE": {
        "type": FieldType.FLAG,
        "bit": 9,  # Bit 1 of high byte
        "name": "Constant Current Timeout Enable",
        "description": "Constant current stage timeout indication enable"
    },
    "FVTOE": {
        "type": FieldType.FLAG,
        "bit": 10,  # Bit 1 of high byte
        "name": "Floating Voltage Timeout Enable",
        "description": "Floating voltage stage timeout indication enable"
    },
    "RSTE": {
        "type": FieldType.FLAG,
        "bit": 11,  # Bit 3 of high byte
        "name": "Restart Charge Enable",
        "description": "Restart to charge after the battery is full enable"
    },
    "CVTSSE": {
        "type": FieldType.FLAG,
        "bit": 13,  # Bit 5 of high byte
        "name": "CV Timeout Status Selection",
        "description": "CV Timeout Status Selection Enable"
    },

    # Low byte fields
    "CUVS": {
        "type": FieldType.BITS,
        "mask": 0x03,  # Bits 0-1 of low byte
        "shift": 0,
        "name": "Charge Curve Setting",
        "description": "Charge curve setting",
        "values": {
            0: "Customized charging curve",
            1: "Preset charging curve #1",
            2: "Preset charging curve #2",
            3: "Preset charging curve #3"
        }
    },
    "TCS": {
        "type": FieldType.BITS,
        "mask": 0x0C,  # Bits 2-3 of low byte
        "shift": 2,
        "name": "Temperature Compensation",
        "description": "Temperature compensation setting",
        "values": {
            0: "Disabled",
            1: "-3mV/°C/cell",
            2: "-4mV/°C/cell",
            3: "-5mV/°C/cell"
        }
    },
    "CUVE": {
        "type": FieldType.FLAG,
        "bit": 7,  # Bit 7 of low byte
        "name": "Charge Curve Enable",
        "description": "Charge curve function enable"
    }
}

CurveConfigParser = ConfigParserFactory.create_parser(
    "CurveConfigParser",
    CURVE_CONFIG,
    # No enum_class parameter for field-based parsers
)
