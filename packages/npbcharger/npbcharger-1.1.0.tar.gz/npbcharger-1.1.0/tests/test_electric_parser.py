import unittest
from can import Message

from npbcharger.parsers import ElectricDataParser


class TestElectricDataParser(unittest.TestCase):

    def setUp(self):
        self.parser = ElectricDataParser(scaling_factor=0.01)
        self.parser_constrained = ElectricDataParser(
            scaling_factor=0.01,
            constraints={'min': 21.0, 'max': 42.0}
        )

    def test_parse_read_voltage(self):
        # Test data: 0x0834 = 2100 * 0.01 = 21.00V
        msg = Message(data=bytearray(b'\xb1\x00\x34\x08'))  # CURVE_CV response
        result = self.parser.parse_read(msg)
        self.assertAlmostEqual(result, 21.00, places=2)

    def test_parse_read_current(self):
        # Test data: 0x07D0 = 2000 * 0.01 = 20.00A
        msg = Message(data=bytearray(b'\xb0\x00\xd0\x07'))  # CURVE_CC response
        result = self.parser.parse_read(msg)
        self.assertAlmostEqual(result, 20.00, places=2)

    def test_parse_write_voltage(self):
        result = self.parser.parse_write(21.5)
        expected = bytearray(b'\x66\x08')  # 2150 = 0x0866 little-endian
        self.assertEqual(result, expected)

    def test_parse_write_with_constraints(self):
        # Test min bound
        result_min = self.parser_constrained.parse_write(15.0)
        expected_min = bytearray(b'\x34\x08')  # 2100 = 0x0834 (21.00V)
        self.assertEqual(result_min, expected_min)

        # Test max bound
        result_max = self.parser_constrained.parse_write(50.0)
        expected_max = bytearray(b'\x68\x10')  # 4200 = 0x1068 (42.00V)
        self.assertEqual(result_max, expected_max)

    def test_parse_write_rounding(self):
        result = self.parser.parse_write(21.567)
        expected = bytearray(b'\x6D\x08')  # 2157 = 0x086D (21.57V)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
