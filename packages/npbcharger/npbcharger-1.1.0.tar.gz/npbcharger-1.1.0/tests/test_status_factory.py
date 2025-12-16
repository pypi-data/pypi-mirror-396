import unittest
from enum import Flag
from can import Message

from npbcharger.parsers.factories import StatusParserFactory, Severity, Polarity


class TestStatusFactory(unittest.TestCase):

    def setUp(self):
        # Create a test flag enum
        class TestStatus(Flag):
            ERROR = 1 << 0
            WARNING = 1 << 1
            READY = 1 << 2

        self.TestStatus = TestStatus

        # Create test config
        self.test_config = {
            TestStatus.ERROR: {
                "name": "Error State",
                "severity": Severity.CRITICAL,
                "polarity": Polarity.ACTIVE_HIGH,
            },
            TestStatus.WARNING: {
                "name": "Warning State",
                "severity": Severity.WARNING,
                "polarity": Polarity.ACTIVE_HIGH,
            },
            TestStatus.READY: {
                "name": "Ready State",
                "severity": Severity.INFO,
                "polarity": Polarity.ACTIVE_LOW,  # 0 = active
            }
        }

        # Create parser using factory
        self.TestParser = StatusParserFactory.create_parser(
            "TestParser", self.test_config, TestStatus
        )
        self.parser = self.TestParser()

    def test_flag_activation_active_high(self):
        """Test active high polarity"""
        # ERROR is active high - bit 0 set = active
        msg = Message(data=bytearray([0x00, 0x00, 0x01, 0x00]))  # bit 0 set
        result = self.parser.parse_read(msg)
        self.assertTrue(self.TestStatus.ERROR in result["status"])

    def test_flag_activation_active_low(self):
        """Test active low polarity"""
        # READY is active low - bit 2 clear = active
        msg = Message(data=bytearray([0x00, 0x00, 0x00, 0x00]))  # bit 2 clear
        result = self.parser.parse_read(msg)
        self.assertTrue(self.TestStatus.READY in result["status"])

    def test_severity_detection(self):
        """Test severity detection logic"""
        # ERROR (critical) + WARNING (warning) active
        msg = Message(data=bytearray([0x00, 0x00, 0x03, 0x00]))  # bits 0-1 set
        result = self.parser.parse_read(msg)

        self.assertTrue(result["has_critical"])
        self.assertTrue(result["has_warnings"])
        # 3 as ready state is low polarity
        self.assertEqual(len(result["active_states"]), 3)

    def test_active_states_metadata(self):
        """Test active states metadata structure"""
        msg = Message(data=bytearray([0x00, 0x00, 0x01, 0x00]))  # ERROR active
        result = self.parser.parse_read(msg)

        active_state = result["active_states"][0]
        self.assertEqual(active_state["name"], "Error State")
        self.assertEqual(active_state["severity"], Severity.CRITICAL)
