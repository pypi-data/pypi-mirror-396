from typing import Dict, Optional
from ...commands import NPB1700Commands
from ..base import BaseParser


class ParserFactory:
    _parsers: Optional[Dict[NPB1700Commands, BaseParser]] = None

    @classmethod
    def get_parser(cls, command: NPB1700Commands) -> BaseParser:

        if cls._parsers is None:
            # Perform imports and creation (Lazy Loading)
            # Local imports prevent circular dependency errors during module load
            from ..electric_data import ElectricDataParser
            from ..fault_status import FaultStatusParser
            from ..charge_status import ChargeStatusParser
            from ..curve_config import CurveConfigParser
            from ..system_config import SystemConfigParser
            from ..system_status import SystemStatusParser
            from ..bytes_forward import BytesForward
            cls._parsers = {
                # Electric data read/write
                NPB1700Commands.CURVE_CC: ElectricDataParser(constraints={'min': 10.0, 'max': 50.0}, scaling_factor=0.01),
                NPB1700Commands.READ_IOUT: ElectricDataParser(constraints={'min': 0.0, 'max': 60.0}, scaling_factor=0.01),

                NPB1700Commands.CHG_RST_VBAT: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
                NPB1700Commands.CURVE_CV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
                NPB1700Commands.CURVE_FV: ElectricDataParser(constraints={'min': 21.0, 'max': 42.0}, scaling_factor=0.01),
                NPB1700Commands.READ_VOUT: ElectricDataParser(constraints={'min': 0.0, 'max': 42.0}, scaling_factor=0.01),

                NPB1700Commands.READ_TEMPERATURE_1: ElectricDataParser(constraints={'min': -40.0, 'max': 110.0}, scaling_factor=0.1),

                # Meaningful values on timeouts
                NPB1700Commands.CURVE_CC_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),
                NPB1700Commands.CURVE_CV_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),
                NPB1700Commands.CURVE_FV_TIMEOUT: ElectricDataParser(constraints={'min': 60.0, 'max': 64800.0}, scaling_factor=1),

                NPB1700Commands.OPERATION: ElectricDataParser(constraints={'min': 0.0, 'max': 1.0}, scaling_factor=1, raw_data_len=3),

                # Model id. 2 (command) + 6 (param) = 8 bytes len
                NPB1700Commands.MFR_MODEL_B0B5: BytesForward(),
                NPB1700Commands.MFR_MODEL_B6B11: BytesForward(),

                # Status
                NPB1700Commands.FAULT_STATUS: FaultStatusParser(),
                NPB1700Commands.CHG_STATUS: ChargeStatusParser(),
                NPB1700Commands.SYSTEM_STATUS: SystemStatusParser(),

                # Config
                NPB1700Commands.CURVE_CONFIG: CurveConfigParser(),
                NPB1700Commands.SYSTEM_CONFIG: SystemConfigParser(),
            }

        if command not in cls._parsers:
            raise ValueError(
                f"No parser available for command {command.name} (0x{command.value.hex()})")

        return cls._parsers[command]
