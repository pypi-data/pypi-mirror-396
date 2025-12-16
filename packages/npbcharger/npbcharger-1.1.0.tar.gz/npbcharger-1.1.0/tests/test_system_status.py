import unittest
from can import Message

from npbcharger.parsers import SystemStatusParser, SystemStatus


class TestSystemStatusParser(unittest.TestCase):

    def setUp(self):
        self.parser = SystemStatusParser()

    def test_parser_creation(self):
        """Test that parser was created with correct enum"""
        self.assertIsNotNone(self.parser.STATUS_ENUM)
        self.assertIsNotNone(self.parser.STATUS_METADATA)

    def test_common_status_scenarios(self):
        """Test common status scenarios"""
        test_cases = [
            # Normal operation
            (0x0002, [], False, False),
            # DC_OK fault (active low - bit clear means fault)
            (0x0000, [SystemStatus.DC_OK], True, False),
            # EEPROM error
            (0x0040, [SystemStatus.EEPER], True, False),
        ]

        for status_word, expected_active, has_critical, has_warnings in test_cases:
            with self.subTest(status_word=hex(status_word)):
                msg = Message(data=bytearray([0x00, 0x00]) +
                              bytearray(status_word.to_bytes(2, 'little')))
                result = self.parser.parse_read(msg)

                self.assertEqual(result["has_critical"], has_critical)
                self.assertEqual(result["has_warnings"], has_warnings)

                for expected_state in expected_active:
                    self.assertTrue(expected_state in result["status"])
