import unittest
from can import Message


from npbcharger.parsers import FaultStatusParser, FaultStatus
from npbcharger.parsers.factories import Severity


class TestFaultStatusParser(unittest.TestCase):

    def setUp(self):
        self.parser = FaultStatusParser()

    def _create_message(self, status_word: int) -> Message:
        """Helper to create CAN message with fault status command header"""
        status_bytes = status_word.to_bytes(2, byteorder='little')
        return Message(data=bytearray([0x40, 0x00]) + bytearray(status_bytes))

    def test_parser_creation(self):
        """Test that parser was created with correct enum and metadata"""
        self.assertIsNotNone(self.parser.STATUS_ENUM)
        self.assertIsNotNone(self.parser.STATUS_METADATA)
        self.assertEqual(self.parser.STATUS_ENUM, FaultStatus)

    def test_normal_operation(self):
        """Test parsing when no faults are active"""
        msg = self._create_message(0x0000)
        result = self.parser.parse_read(msg)

        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["status"], FaultStatus(0))
        self.assertEqual(len(result["active_states"]), 0)
        self.assertFalse(result["has_critical"])
        self.assertFalse(result["has_warnings"])

    def test_common_fault_scenarios(self):
        """Test common fault scenarios"""
        test_cases = [
            # (scenario_name, status_bits, expected_active_names, has_critical, has_warnings)
            ("Over Temperature", FaultStatus.OTP.value, [
             "Over Temperature Protection"], True, False),
            ("Output Disabled", FaultStatus.OP_OFF.value,
             ["Output Disabled"], False, False),
            ("Over Voltage", FaultStatus.OVP.value, [
             "Over Voltage Protection"], True, False),
            ("Multiple Critical Faults",
             FaultStatus.OTP.value | FaultStatus.OVP.value,
             ["Over Temperature Protection", "Over Voltage Protection"], True, False),
            ("Mixed Critical and Info",
             FaultStatus.OTP.value | FaultStatus.OP_OFF.value,
             ["Over Temperature Protection", "Output Disabled"], True, False),
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

    def test_all_critical_faults_simultaneous(self):
        """Test multiple critical faults active at once"""
        status_bits = (FaultStatus.OTP.value | FaultStatus.OVP.value |
                       FaultStatus.OLP.value | FaultStatus.SHORT.value)
        msg = self._create_message(status_bits)
        result = self.parser.parse_read(msg)

        self.assertTrue(result["has_critical"])
        self.assertFalse(result["has_warnings"])
        self.assertEqual(len(result["active_states"]), 4)

    def test_active_states_metadata(self):
        """Test that active states have correct metadata structure"""
        msg = self._create_message(FaultStatus.OTP.value)
        result = self.parser.parse_read(msg)

        active_state = result["active_states"][0]
        self.assertEqual(active_state["state"], FaultStatus.OTP)
        self.assertEqual(active_state["name"], "Over Temperature Protection")
        self.assertEqual(active_state["severity"], Severity.CRITICAL)
        self.assertIn("description", active_state)  # Should have description

    def test_write_not_implemented(self):
        """Test that write parsing raises NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.parser.parse_write("some_data")

    def test_invalid_data_length(self):
        """Test handling of messages that are too short"""
        short_msg = Message(data=bytearray(b'\x40\x00'))  # Only command bytes
        with self.assertRaises(ValueError):
            self.parser.parse_read(short_msg)


if __name__ == '__main__':
    unittest.main()
