import unittest
from can import Message

from npbcharger.parsers.bytes_forward import BytesForward


class TestForwardBytesParser(unittest.TestCase):

    def _create_message(self, command_bytes: bytearray, data_bytes: bytes) -> Message:
        """Helper to create CAN message with command header and data."""
        data = command_bytes + bytearray(data_bytes)
        # Use an arbitrary CAN ID; only the data field matters for the parser
        return Message(arbitration_id=0x000C0103, dlc=len(data), data=data)

    def test_parse_read_scenarios(self):
        """Test successful parsing for 6-byte and other data lengths."""

        # --- Scenario 1: Model ID (6 data bytes) ---
        # 6 data bytes + 2 command bytes = 8 bytes total
        parser_6 = BytesForward(data_len=6)

        test_cases_6_byte = [
            # Full 6-byte string
            (bytearray([0x87, 0x00]), b'NPB-17', bytearray(b'NPB-17')),
            # String with null-padding (common for fixed-length string fields)
            (bytearray([0x88, 0x00]), b'00-24\x00', bytearray(b'00-24\x00')),
        ]

        for command, input_data, expected_output in test_cases_6_byte:
            with self.subTest(msg_len=6, data_repr=repr(input_data)):
                msg = self._create_message(command, input_data)
                result = parser_6.parse_read(msg)

                self.assertEqual(result, expected_output)
                self.assertIsInstance(result, bytearray)

        # Location ID
        # MFR_LOCATION_B0B2 has 3 bytes of data
        parser_3 = BytesForward(data_len=3)

        test_cases_3_byte = [
            (bytearray([0x85, 0x00]), b'HMN', bytearray(b'HMN')),
        ]

        for command, input_data, expected_output in test_cases_3_byte:
            with self.subTest(msg_len=3, data_repr=repr(input_data)):
                msg = self._create_message(command, input_data)
                result = parser_3.parse_read(msg)

                self.assertEqual(result, expected_output)

    def test_short_message_raises_error(self):
        """Test that a message shorter than expected data length raises ValueError."""

        # Expected total length is 8 (6 data + 2 command)
        parser = BytesForward(data_len=6)
        command = bytearray([0x87, 0x00])

        # Only 5 data bytes are sent (total length 7)
        short_data = b'NPB-1'
        msg = self._create_message(command, short_data)

        with self.assertRaisesRegex(ValueError, "data too short"):
            parser.parse_read(msg)

    def test_parse_write_not_implemented(self):
        """Test that parse_write raises NotImplementedError."""
        parser = BytesForward()
        with self.assertRaises(NotImplementedError):
            parser.parse_write(bytearray(b'123456'))


if __name__ == '__main__':
    unittest.main()
