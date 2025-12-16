import enum
CURVE_F = 0.01
COMMAND_LEN = 2


class NPB1700Commands(enum.Enum):
    """CAN Command Codes for Mean Well NPB-1700 Series in Little Endian Format.
        NOTE: Commented commands work only in PSU mode. Since NPB series may work only in charger mode they are irrelevant
    """
    # pylint: disable=invalid-name

    # --- Control Commands ---
    OPERATION = bytearray([0x00, 0x00])        # R/W, 1 byte - ON/OFF control
    # R/W, 2 - Output voltage setting (F=0.01)
    # VOUT_SET = bytearray([0x20, 0x00])
    # R/W, 2 - Output current setting (F=0.01)
    # IOUT_SET = bytearray([0x30, 0x00])

    # --- Status/Read Commands ---
    FAULT_STATUS = bytearray([0x40, 0x00])     # R, 2 - Abnormal status
    # R, 2 - Input voltage read value
    # READ_VIN = bytearray([0x50, 0x00])
    # R, 2 - Output voltage read value (F=0.01)
    READ_VOUT = bytearray([0x60, 0x00])
    # R, 2 - Output current read value (F=0.01)
    READ_IOUT = bytearray([0x61, 0x00])
    # R, 2 - Internal ambient temperature (F=0.1)
    READ_TEMPERATURE_1 = bytearray([0x62, 0x00])

    # --- Manufacturer Info Commands ---
    MFR_ID_B0B5 = bytearray([0x80, 0x00])      # R, 6 - Manufacturer's name
    MFR_ID_B6B11 = bytearray([0x81, 0x00])     # R, 6 - Manufacturer's name
    # R, 6 - Manufacturer's model name
    MFR_MODEL_B0B5 = bytearray([0x82, 0x00])
    # R, 6 - Manufacturer's model name
    MFR_MODEL_B6B11 = bytearray([0x83, 0x00])
    MFR_REVISION_B0B5 = bytearray([0x84, 0x00])  # R, 6 - Firmware revision
    # R/W, 3 - Manufacturer's factory location
    MFR_LOCATION_B0B2 = bytearray([0x85, 0x00])
    MFR_DATE_B0B5 = bytearray([0x86, 0x00])    # R/W, 6 - Manufacturer date
    MFR_SERIAL_B0B5 = bytearray([0x87, 0x00])  # R/W, 6 - Product serial number
    # R/W, 6 - Product serial number
    MFR_SERIAL_B6B11 = bytearray([0x88, 0x00])

    # --- Charging Curve Commands (Charger Mode) ---
    # R/W, 2 - Constant current setting (F=0.01)
    CURVE_CC = bytearray([0xB0, 0x00])
    # R/W, 2 - Constant voltage setting (F=0.01)
    CURVE_CV = bytearray([0xB1, 0x00])
    # R/W, 2 - Floating voltage setting (F=0.01)
    CURVE_FV = bytearray([0xB2, 0x00])
    # R/W, 2 - Taper current setting (F=0.01)
    CURVE_TC = bytearray([0xB3, 0x00])
    # R/W, 2 - Configuration setting of charge curve
    CURVE_CONFIG = bytearray([0xB4, 0x00])
    # R/W, 2 - CC charge timeout setting
    CURVE_CC_TIMEOUT = bytearray([0xB5, 0x00])
    # R/W, 2 - CV charge timeout setting
    CURVE_CV_TIMEOUT = bytearray([0xB6, 0x00])
    # R/W, 2 - FV charge timeout setting
    CURVE_FV_TIMEOUT = bytearray([0xB7, 0x00])
    # R, 2 - Charging status reporting
    CHG_STATUS = bytearray([0xB8, 0x00])
    # R/W, 2 - Voltage to restart charging after full
    CHG_RST_VBAT = bytearray([0xB9, 0x00])

    # --- System Commands ---
    SCALING_FACTOR = bytearray([0xC0, 0x00])   # R, 2 - Scaling ratio
    SYSTEM_STATUS = bytearray([0xC1, 0x00])    # R, 2 - System status
    SYSTEM_CONFIG = bytearray([0xC2, 0x00])    # R/W, 2 - System configuration
