import unittest
from can import Message
from npbcharger.parsers import ChargeStatusParser
from npbcharger.parsers import ChargeStatus


class TestChargeStatusParser(unittest.TestCase):

    def setUp(self):
        self.parser = ChargeStatusParser()

    def _create_message(self, status_word: int) -> Message:
        """Helper to create CAN message with charge status command header"""
        status_bytes = status_word.to_bytes(2, byteorder='little')
        return Message(data=bytearray([0xB8, 0x00]) + bytearray(status_bytes))

    def test_parser_creation(self):
        """Test that parser was created with correct enum and metadata"""
        self.assertIsNotNone(self.parser.STATUS_ENUM)
        self.assertIsNotNone(self.parser.STATUS_METADATA)
        self.assertEqual(self.parser.STATUS_ENUM, ChargeStatus)

    def test_normal_operation(self):
        """Test parsing when no charge status flags are active"""
        msg = self._create_message(0x0000)
        result = self.parser.parse_read(msg)

        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["status"], ChargeStatus(0))
        self.assertEqual(len(result["active_states"]), 0)
        self.assertFalse(result["has_critical"])
        self.assertFalse(result["has_warnings"])

    def test_common_charging_scenarios(self):
        """Test realistic charging scenarios"""
        test_cases = [
            # (scenario_name, status_bits, expected_active_names, has_critical, has_warnings)
            ("CC Charging", ChargeStatus.CCM.value, [
             "Constant Current Mode"], False, False),
            ("CV Charging", ChargeStatus.CVM.value, [
             "Constant Voltage Mode"], False, False),
            ("Float Charging", ChargeStatus.FVM.value,
             ["Float Mode"], False, False),
            ("Fully Charged", ChargeStatus.FULLM.value,
             ["Fully Charged"], False, False),
            ("CC Timeout", ChargeStatus.CCTOF.value,
             ["CC Mode Timeout"], False, True),
            ("Critical Fault", ChargeStatus.NTCER.value,
             ["NTC Short Circuit"], True, False),
            ("Mixed Critical and Warning",
             ChargeStatus.NTCER.value | ChargeStatus.CCTOF.value,
             ["NTC Short Circuit", "CC Mode Timeout"], True, True),
        ]

        for scenario_name, status_bits, expected_names, expected_critical, expected_warnings in test_cases:
            with self.subTest(scenario=scenario_name):
                msg = self._create_message(status_bits)
                result = self.parser.parse_read(msg)

                # Check severity detection
                self.assertEqual(result["has_critical"], expected_critical)
                self.assertEqual(result["has_warnings"], expected_warnings)

                # Check active state names
                active_names = [state["name"]
                                for state in result["active_states"]]
                self.assertEqual(sorted(active_names), sorted(expected_names))

    def test_all_charging_modes_simultaneous(self):
        """Test multiple charging modes active at once"""
        status_bits = ChargeStatus.CCM.value | ChargeStatus.CVM.value | ChargeStatus.FVM.value
        msg = self._create_message(status_bits)
        result = self.parser.parse_read(msg)

        self.assertEqual(len(result["active_states"]), 3)
        self.assertFalse(result["has_critical"])
        self.assertFalse(result["has_warnings"])

        # Verify all charging modes are present
        active_names = [state["name"] for state in result["active_states"]]
        expected_names = ["Constant Current Mode",
                          "Constant Voltage Mode", "Float Mode"]
        self.assertEqual(sorted(active_names), sorted(expected_names))

    def test_write_not_implemented(self):
        """Test that write parsing raises NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.parser.parse_write("some_data")

    def test_invalid_data_length(self):
        """Test handling of messages that are too short"""
        short_msg = Message(data=bytearray(b'\xB8\x00'))  # Only command bytes
        with self.assertRaises(ValueError):
            self.parser.parse_read(short_msg)


if __name__ == '__main__':
    unittest.main()
