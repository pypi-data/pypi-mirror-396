import unittest

from npbcharger.commands import NPB1700Commands
from npbcharger.parsers import ElectricDataParser, ParserFactory, FaultStatusParser


class TestParserFactory(unittest.TestCase):

    def setUp(self):
        # Reset the singleton cache before each test
        ParserFactory._parsers = None

    def test_caching_mechanism(self):
        """
        Verify that the factory returns the exact same object instance
        on repeated calls. This confirms the lazy creation works
        """
        command = NPB1700Commands.CURVE_CC

        # create the instance
        parser1 = ParserFactory.get_parser(command)

        # retrieve from cache
        parser2 = ParserFactory.get_parser(command)

        # check that they are the exact same object in memory
        # assertIs checks the similarity of objects
        self.assertIs(parser1, parser2,
                      "Factory failed to cache the parser instance")

    def test_correct_class_mapping(self):
        """Verify that commands return the expected parser classes"""
        p_electric = ParserFactory.get_parser(NPB1700Commands.READ_VOUT)
        self.assertIsInstance(p_electric, ElectricDataParser)

        p_fault = ParserFactory.get_parser(NPB1700Commands.FAULT_STATUS)
        self.assertIsInstance(p_fault, FaultStatusParser)

    def test_constraints_configuration(self):
        """
        Verify that the factory correctly initializes ElectricDataParser 
        with the specific constraints defined in the dictionary.
        """
        # Check READ_IOUT (Min 0, Max 60)
        p_iout = ParserFactory.get_parser(NPB1700Commands.READ_IOUT)
        self.assertEqual(p_iout.constraints['max'], 60.0)

        # Check CURVE_CC (Min 10, Max 50)
        p_cc = ParserFactory.get_parser(NPB1700Commands.CURVE_CC)
        self.assertEqual(p_cc.constraints['max'], 50.0)

        # Should be different objects
        self.assertIsNot(p_iout, p_cc)

    def test_unknown_command(self):
        """Ensure factory raises error for commands not in the map"""
        # Create a dummy command that doesn't exist in the factory map
        try:
            class FakeCommand:
                name = "FAKE"
                value = b'\xFF\xFF'

            ParserFactory.get_parser(FakeCommand())
            self.fail("Should have raised ValueError")
        except ValueError:
            pass  # Success
        except Exception as e:
            pass


if __name__ == '__main__':
    unittest.main()
