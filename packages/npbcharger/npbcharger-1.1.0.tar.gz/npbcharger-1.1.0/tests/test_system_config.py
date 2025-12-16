import unittest
from can import Message

from npbcharger.parsers import SystemConfigParser


class TestSystemConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = SystemConfigParser()

    def test_parser_creation(self):
        """Test that parser was created with correct configuration"""
        self.assertIsNotNone(self.parser.CONFIG)
        self.assertIn("OPERATION_INIT", self.parser.CONFIG)
        self.assertIn("EEP_OFF", self.parser.CONFIG)

    def test_common_scenarios(self):
        """Test common real-world scenarios"""
        test_cases = [
            # Default configuration
            (0x0000, "Power on with 00h: OFF", False),
            # Typical configuration
            (0x0402, "Power on with 01h: ON", True),
        ]

        for config_word, expected_init, expected_eep in test_cases:
            with self.subTest(config_word=hex(config_word)):
                msg = Message(data=bytearray([0x00, 0x00]) +
                              bytearray(config_word.to_bytes(2, 'little')))
                result = self.parser.parse_read(msg)

                self.assertEqual(
                    result["fields"]["OPERATION_INIT"], expected_init)
                self.assertEqual(result["fields"]["EEP_OFF"], expected_eep)

    def test_write_common_values(self):
        """Test writing common configuration values"""
        common_configs = [
            {"OPERATION_INIT": 0, "EEP_OFF": False},
            {"OPERATION_INIT": 2, "EEP_OFF": True},
        ]

        for config in common_configs:
            with self.subTest(config=config):
                result = self.parser.parse_write(config)
                self.assertIsInstance(result, bytearray)
                self.assertEqual(len(result), 2)
