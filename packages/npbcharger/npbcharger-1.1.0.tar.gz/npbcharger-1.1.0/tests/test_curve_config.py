import unittest
from can import Message

from npbcharger.parsers import CurveConfigParser


class TestCurveConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = CurveConfigParser()

    def _create_message(self, config_word: int) -> Message:
        """Helper to create CAN message with config data"""
        config_bytes = config_word.to_bytes(2, byteorder='little')
        return Message(data=bytearray([0x00, 0x00]) + bytearray(config_bytes))

    def test_parser_creation(self):
        """Test that parser was created with correct configuration"""
        self.assertIsNotNone(self.parser.CONFIG)
        # Just verify a couple key fields exist
        self.assertIn("CUVS", self.parser.CONFIG)
        self.assertIn("TCS", self.parser.CONFIG)
        self.assertIn("CUVE", self.parser.CONFIG)

    def test_default_configuration(self):
        """Test parsing when all fields are at default values"""
        msg = self._create_message(0x0000)
        result = self.parser.parse_read(msg)

        self.assertEqual(result["raw_value"], 0)
        self.assertEqual(result["fields"]["CUVS"], "Customized charging curve")
        self.assertEqual(result["fields"]["TCS"], "Disabled")
        self.assertFalse(result["fields"]["CUVE"])

    def test_common_configuration_scenarios(self):
        """Test common real-world configuration scenarios"""
        test_cases = [
            # (scenario_name, config_word, key_expected_fields)
            (
                "Custom Curve Enabled",
                0x0080,  # CUVE=True
                {"CUVS": "Customized charging curve", "CUVE": True}
            ),
            (
                "Preset Curve with Timeouts",
                0x0701,  # CCTOE,CVTOE,FVTOE=True, CUVS=1
                {"CUVS": "Preset charging curve #1", "CCTOE": True}
            ),
        ]

        for scenario_name, config_word, expected_fields in test_cases:
            with self.subTest(scenario=scenario_name):
                msg = self._create_message(config_word)
                result = self.parser.parse_read(msg)

                for field_name, expected_value in expected_fields.items():
                    self.assertEqual(
                        result["fields"][field_name], expected_value)

    def test_write_basic_configuration(self):
        """Test writing basic configuration"""
        field_data = {
            "CUVS": 1,
            "TCS": 1,
            "CUVE": True
        }

        result = self.parser.parse_write(field_data)
        self.assertIsInstance(result, bytearray)
        self.assertEqual(len(result), 2)

    def test_round_trip_consistency(self):
        """Test that write -> read produces consistent results"""
        test_configs = [0x0000, 0x0080, 0x0701]

        for config_word in test_configs:
            with self.subTest(config_word=hex(config_word)):
                write_data = self.parser.parse_write(config_word)
                read_back_word = int.from_bytes(write_data, byteorder='little')
                simulated_msg = self._create_message(read_back_word)
                read_result = self.parser.parse_read(simulated_msg)

                self.assertEqual(read_result["raw_value"], config_word)

    def test_invalid_data_length(self):
        """Test handling of messages that are too short"""
        short_msg = Message(data=bytearray(b'\x00\x00'))
        with self.assertRaises(ValueError):
            self.parser.parse_read(short_msg)


if __name__ == '__main__':
    unittest.main()
