#!/usr/bin/env python3
"""
Test suite for JBOF Controller Library
Note: These tests require a connected JBOF device or mock serial interface
"""

import unittest
from unittest.mock import MagicMock, patch
import serial
from serialcables_hydra import JBOFController, PowerState, BuzzerState, SlotInfo, SystemInfo


class TestJBOFController(unittest.TestCase):
    """Test cases for JBOFController"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = JBOFController(port="/dev/ttyUSB0")

    @patch("serial.Serial")
    def test_connect(self, mock_serial):
        """Test connection establishment"""
        mock_serial.return_value = MagicMock()

        result = self.controller.connect()

        self.assertTrue(result)
        mock_serial.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )

    @patch("serial.Serial")
    def test_disconnect(self, mock_serial):
        """Test disconnection"""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        self.controller.connect()
        self.controller.disconnect()

        mock_conn.close.assert_called_once()

    @patch("serial.Serial")
    def test_system_power_on(self, mock_serial):
        """Test system power on command"""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"Power on the JBOF enclosure.\r\nCmd>"
        mock_serial.return_value = mock_conn

        self.controller.connect()
        result = self.controller.system_power(PowerState.ON)

        self.assertTrue(result)
        mock_conn.write.assert_called_with(b"syspwr on\r\n")

    @patch("serial.Serial")
    def test_slot_power_control(self, mock_serial):
        """Test slot power control"""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"Slot 01 turn off success.\r\nCmd>"
        mock_serial.return_value = mock_conn

        self.controller.connect()
        result = self.controller.slot_power(1, PowerState.OFF)

        self.assertTrue(result)
        mock_conn.write.assert_called_with(b"ssdpwr 1 off\r\n")

    @patch("serial.Serial")
    def test_parse_environmental_data(self, mock_serial):
        """Test parsing of environmental data"""
        mock_response = """
        * Board Information *
        Thermal:
        - MCU Temperature : 25° C
        - Slot1 Temperature : 26° C
        - Slot2 Temperature : 27° C

        Fan Speed:
        - Switch Fan1 : 5500 RPM
        - Switch Fan2 : 5480 RPM

        Voltage Sensors:
        - 12V Voltage : 12.420 V

        Board Current:
        - Slot 1 Bus Voltage : 12.23 V
        - Slot 1 Load Current : 0.164 A
        - Slot 1 Load Power : 2.014 W
        Cmd>
        """

        mock_conn = MagicMock()
        mock_conn.read.return_value = mock_response.encode()
        mock_conn.in_waiting = len(mock_response)
        mock_serial.return_value = mock_conn

        self.controller.connect()
        data = self.controller.get_environmental_data()

        self.assertEqual(data["temperatures"]["mcu"], 25.0)
        self.assertEqual(data["temperatures"]["slot_1"], 26.0)
        self.assertEqual(data["fan_speeds"]["fan_1"], 5500)
        self.assertEqual(data["voltages"]["psu_12v"], 12.420)
        self.assertEqual(data["powers"]["slot_1"], 2.014)

    @patch("serial.Serial")
    def test_parse_slot_info(self, mock_serial):
        """Test parsing of slot information"""
        mock_response = """
        Slot01: PC: SC, INT: NONE, EDSFF: NONE, Present: No
        Slot02: PC: SC, INT: NONE, EDSFF: X4  , Present: Yes
        Slot03: PC: SC, INT: U2  , EDSFF: NONE, Present: Yes
        Cmd>
        """

        mock_conn = MagicMock()
        mock_conn.read.return_value = mock_response.encode()
        mock_conn.in_waiting = len(mock_response)
        mock_serial.return_value = mock_conn

        self.controller.connect()
        slots = self.controller.show_slot_info()

        self.assertEqual(len(slots), 3)
        self.assertEqual(slots[0].slot_number, 1)
        self.assertFalse(slots[0].present)
        self.assertEqual(slots[1].slot_number, 2)
        self.assertTrue(slots[1].present)
        self.assertEqual(slots[1].edsff_type, "X4")

    @patch("serial.Serial")
    def test_fan_speed_control(self, mock_serial):
        """Test fan speed control"""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"Set duty 100 Success.\r\nCmd>"
        mock_serial.return_value = mock_conn

        self.controller.connect()
        result = self.controller.set_fan_speed(1, 100)

        self.assertTrue(result)
        mock_conn.write.assert_called_with(b"pwmctrl 1 100\r\n")

    @patch("serial.Serial")
    def test_buzzer_control(self, mock_serial):
        """Test buzzer control"""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"OK, turn on buzzer\r\nCmd>"
        mock_serial.return_value = mock_conn

        self.controller.connect()
        result = self.controller.control_buzzer(BuzzerState.ON)

        self.assertTrue(result)
        mock_conn.write.assert_called_with(b"buz on\r\n")

    @patch("serial.Serial")
    def test_clock_status(self, mock_serial):
        """Test clock input status check"""
        mock_response = """
        Slot 1 clk input: Yes
        Slot 2 clk input: Yes
        Slot 3 clk input: No
        Slot 4 clk input: No
        Slot 5 clk input: No
        Slot 6 clk input: No
        Slot 7 clk input: No
        Slot 8 clk input: No
        Cmd>
        """

        mock_conn = MagicMock()
        mock_conn.read.return_value = mock_response.encode()
        mock_conn.in_waiting = len(mock_response)
        mock_serial.return_value = mock_conn

        self.controller.connect()
        clock_status = self.controller.check_clock_input()

        self.assertTrue(clock_status[1])
        self.assertTrue(clock_status[2])
        self.assertFalse(clock_status[3])

    def test_slot_number_validation(self):
        """Test slot number validation"""
        with self.assertRaises(ValueError):
            self.controller.set_fan_speed(3, 50)  # Invalid fan ID

        with self.assertRaises(ValueError):
            self.controller.set_fan_speed(1, 150)  # Invalid duty cycle

    @patch("serial.Serial")
    def test_i2c_operations(self, mock_serial):
        """Test I2C read/write operations"""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"Write Data [0] = ff\r\nCmd>"
        mock_serial.return_value = mock_conn

        self.controller.connect()

        # Test I2C write
        result = self.controller.i2c_write(0xD4, 1, [0xFF])
        self.assertTrue(result)
        mock_conn.write.assert_called_with(b"iicw d4 1 ff\r\n")

        # Test I2C read
        mock_conn.read.return_value = b"Data [0] = 8\r\nData [1] = 33\r\nCmd>"
        mock_conn.in_waiting = 30

        data = self.controller.i2c_read(0xD4, 1, 0x00, 2)
        self.assertEqual(data, [8, 33])


class TestDataClasses(unittest.TestCase):
    """Test data class structures"""

    def test_slot_info(self):
        """Test SlotInfo dataclass"""
        slot = SlotInfo(
            slot_number=1, paddle_card="SC", interposer="U2", edsff_type="NONE", present=True
        )

        self.assertEqual(slot.slot_number, 1)
        self.assertEqual(slot.paddle_card, "SC")
        self.assertTrue(slot.present)

    def test_system_info(self):
        """Test SystemInfo dataclass"""
        slot1 = SlotInfo(1, "SC", "NONE", "X4", True)
        slot2 = SlotInfo(2, "SC", "U2", "NONE", False)

        sys_info = SystemInfo(
            company="Serial Cables",
            model="PCIe Gen6 8Bays JBOF",
            serial_number="SN123456",
            firmware_version="0.0.2",
            build_time="Aug 7 2025 14:39:36",
            slots=[slot1, slot2],
            fan1_rpm=5500,
            fan2_rpm=5480,
            psu_voltage=12.42,
        )

        self.assertEqual(sys_info.company, "Serial Cables")
        self.assertEqual(len(sys_info.slots), 2)
        self.assertEqual(sys_info.fan1_rpm, 5500)
        self.assertEqual(sys_info.psu_voltage, 12.42)


class TestEnumerations(unittest.TestCase):
    """Test enumeration values"""

    def test_power_state(self):
        """Test PowerState enum"""
        self.assertEqual(PowerState.ON.value, "on")
        self.assertEqual(PowerState.OFF.value, "off")

    def test_buzzer_state(self):
        """Test BuzzerState enum"""
        self.assertEqual(BuzzerState.ON.value, "on")
        self.assertEqual(BuzzerState.OFF.value, "off")
        self.assertEqual(BuzzerState.ENABLE.value, "en")
        self.assertEqual(BuzzerState.DISABLE.value, "dis")


def run_integration_tests(port="/dev/ttyUSB0"):
    """
    Run integration tests with actual hardware

    Args:
        port: Serial port for connected JBOF
    """
    print("Running integration tests with hardware...")
    controller = JBOFController(port=port)

    try:
        # Test connection
        assert controller.connect(), "Failed to connect"
        print("✓ Connection established")

        # Test version info
        version = controller.get_version_info()
        assert "version" in version, "Version info missing"
        print(f"✓ Version info retrieved: {version['version']}")

        # Test slot info
        slots = controller.show_slot_info()
        assert len(slots) == 8, "Expected 8 slots"
        print(f"✓ Slot info retrieved: {len(slots)} slots")

        # Test environmental data
        env = controller.get_environmental_data()
        assert "temperatures" in env, "Temperature data missing"
        print("✓ Environmental data retrieved")

        # Test power control (non-destructive)
        status = controller.get_slot_power_status()
        assert len(status) > 0, "Power status empty"
        print("✓ Power status retrieved")

        # Test diagnostics
        diag = controller.run_diagnostics()
        print(f"✓ Diagnostics completed: {len(diag)} devices checked")

        print("\n✅ All integration tests passed!")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")

    finally:
        controller.disconnect()


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[""], exit=False, verbosity=2)

    # Optionally run integration tests
    # Uncomment and update port to run with actual hardware
    # run_integration_tests(port='/dev/ttyUSB0')
