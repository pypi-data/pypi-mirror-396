import unittest
from npbcharger.parsers.factories.config_factory import ConfigParserFactory, FieldType


class TestConfigFactory(unittest.TestCase):

    def setUp(self):
        # Create test config with all field types
        self.test_config = {
            "FLAG_FIELD": {
                "type": FieldType.FLAG,
                "bit": 0,
                "name": "Test Flag",
            },
            "BITS_FIELD": {
                "type": FieldType.BITS,
                "mask": 0x06,  # bits 1-2
                "shift": 1,
                "values": {
                    0: "Mode 0",
                    1: "Mode 1",
                    2: "Mode 2",
                    3: "Mode 3"
                }
            },
            "VALUE_FIELD": {
                "type": FieldType.VALUE,
                "mask": 0x00F0,  # bits 4-7
                "shift": 4,
            }
        }

        # Create parser using factory
        self.TestParser = ConfigParserFactory.create_parser(
            "TestConfigParser", self.test_config
        )
        self.parser = self.TestParser()

    def test_field_parsing(self):
        """Test parsing all field types"""

        test_value = (1 << 0) | (2 << 1) | (5 << 4)

        from can import Message
        msg = Message(data=bytearray([0x00, 0x00]) +
                      bytearray(test_value.to_bytes(2, "little")))
        result = self.parser.parse_read(msg)

        self.assertEqual(result["fields"]["FLAG_FIELD"], True)
        self.assertEqual(result["fields"]["BITS_FIELD"], "Mode 2")
        self.assertEqual(result["fields"]["VALUE_FIELD"], 5)

    def test_write_complete_overwrite(self):
        """Test complete configuration overwrite"""
        field_data = {
            "FLAG_FIELD": True,
            "BITS_FIELD": 1,
            "VALUE_FIELD": 3
        }

        result = self.parser.parse_write(field_data)

        expected = (1 << 0) | (1 << 1) | (3 << 4)
        expected_bytes = expected.to_bytes(2, byteorder='little')

        self.assertEqual(result, bytearray(expected_bytes))

    def test_write_partial_update(self):
        """Test partial field updates"""
        current_state = (1 << 0) | (2 << 1) | (5 << 4)

        # Update only BITS_FIELD
        updates = {"BITS_FIELD": 3}
        result = self.parser.parse_write_update(updates, current_state)

        # Should preserve FLAG_FIELD and VALUE_FIELD, update BITS_FIELD
        expected = (1 << 0) | (3 << 1) | (5 << 4)
        expected_bytes = expected.to_bytes(2, byteorder='little')

        self.assertEqual(result, bytearray(expected_bytes))
