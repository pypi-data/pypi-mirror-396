"""
PCIe Gen6 8-Bay JBOF Controller Library
For Serial Cables, LLC PCIe Gen6 8Bays Passive JBOF

Author: Serial Cables Engineering
Version: 1.0.0
"""

import serial
import time
import re
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlotNumber(Enum):
    """Valid slot numbers for the JBOF"""

    SLOT1 = 1
    SLOT2 = 2
    SLOT3 = 3
    SLOT4 = 4
    SLOT5 = 5
    SLOT6 = 6
    SLOT7 = 7
    SLOT8 = 8
    ALL = "all"


class PowerState(Enum):
    """Power states"""

    ON = "on"
    OFF = "off"


class SignalLevel(Enum):
    """Signal levels for PWRDIS"""

    HIGH = "h"
    LOW = "l"


class BuzzerState(Enum):
    """Buzzer control states"""

    ON = "on"
    OFF = "off"
    ENABLE = "en"
    DISABLE = "dis"


@dataclass
class MCTPResponse:
    """Response from an MCTP packet transmission"""

    success: bool
    packets_sent: int
    response_packets: List[List[int]]  # List of response packet byte arrays
    raw_response: str


@dataclass
class NVMeSerialNumber:
    """NVMe drive serial number retrieved via MCTP"""

    slot: int
    serial_number: str
    success: bool
    raw_packets: List[List[int]]
    error: Optional[str] = None


@dataclass
class NVMeHealthStatus:
    """NVMe drive health status retrieved via MCTP"""

    slot: int
    success: bool
    raw_packets: List[List[int]]
    # Health status fields (from NVMe-MI Health Status Poll)
    composite_temperature: Optional[int] = None  # Kelvin
    composite_temperature_celsius: Optional[float] = None
    available_spare: Optional[int] = None  # Percentage
    available_spare_threshold: Optional[int] = None  # Percentage
    percentage_used: Optional[int] = None  # Percentage
    critical_warning: Optional[int] = None  # Bit field
    error: Optional[str] = None


@dataclass
class SlotInfo:
    """Information about a single slot"""

    slot_number: int
    paddle_card: str
    interposer: str
    edsff_type: str
    present: bool
    power_status: str = "unknown"
    temperature: float = 0.0
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0


@dataclass
class SystemInfo:
    """Complete system information"""

    company: str
    model: str
    serial_number: str
    firmware_version: str
    build_time: str
    slots: List[SlotInfo]
    fan1_rpm: int
    fan2_rpm: int
    psu_voltage: float


class JBOFController:
    """Controller class for Serial Cables PCIe Gen6 8-Bay JBOF"""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize the JBOF controller

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' or 'COM3')
            baudrate: Baud rate (default 115200)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self._response_buffer = ""

    def connect(self) -> bool:
        """
        Establish serial connection to the JBOF

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )
            logger.info(f"Connected to JBOF on {self.port}")
            time.sleep(0.5)  # Allow connection to stabilize
            self._flush_buffers()
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self) -> None:
        """Close the serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Disconnected from JBOF")

    def _flush_buffers(self) -> None:
        """Flush input and output buffers"""
        if self.serial_conn:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

    def _send_command(self, command: str) -> str:
        """
        Send a command and receive response

        Args:
            command: Command string to send

        Returns:
            Response string from the device
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Serial connection not established")

        # Clear any pending data
        self._flush_buffers()

        # Send command with CR/LF
        cmd_bytes = (command + "\r\n").encode("utf-8")
        self.serial_conn.write(cmd_bytes)
        logger.debug(f"Sent: {command}")

        # Read response
        response = ""
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            if self.serial_conn.in_waiting:
                chunk = self.serial_conn.read(self.serial_conn.in_waiting).decode(
                    "utf-8", errors="ignore"
                )
                response += chunk

                # "Cmd>" is the definitive completion marker - always wait for it
                # This ensures we capture full responses (e.g., MCTP receive packets
                # that come after "Command sent successfully.")
                if "Cmd>" in response:
                    break

            time.sleep(0.01)

        logger.debug(f"Received: {response}")
        return response.strip()

    # System Control Commands

    def system_power(self, state: PowerState) -> bool:
        """
        Control system power

        Args:
            state: PowerState.ON or PowerState.OFF

        Returns:
            True if successful
        """
        response = self._send_command(f"syspwr {state.value}")
        return "success" in response.lower() or f"Power {state.value}" in response

    def reset(self) -> bool:
        """
        Reset the JBOF enclosure

        Returns:
            True if reset initiated
        """
        response = self._send_command("reset")
        return "System Reset" in response

    # Slot Power Management

    def slot_power(self, slot: Union[int, str], state: PowerState) -> bool:
        """
        Control power for specific slot(s)

        Args:
            slot: Slot number (1-8) or "all"
            state: PowerState.ON or PowerState.OFF

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        response = self._send_command(f"ssdpwr {slot_str} {state.value}")
        return "success" in response.lower()

    def get_slot_power_status(self) -> Dict[int, str]:
        """
        Get power status for all slots

        Returns:
            Dictionary of slot number to power status
        """
        response = self._send_command("ssdpwr")
        status = {}

        for line in response.split("\n"):
            match = re.search(r"Slot\s+(\d+)\s+power\s+status:\s+turn\s+(\w+)", line, re.IGNORECASE)
            if match:
                slot_num = int(match.group(1))
                power_state = match.group(2)
                status[slot_num] = power_state

        return status

    # Reset Commands

    def smbus_reset(self, slot: Union[int, str]) -> bool:
        """
        Send SMBus reset signal to selected slot(s)

        Args:
            slot: Slot number (1-8) or "all"

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        response = self._send_command(f"smbrst {slot_str}")
        return "success" in response.lower()

    def ssd_reset(self, slot: Union[int, str], channel: Optional[str] = None) -> bool:
        """
        Send PERST# reset signal to selected slot(s)

        Args:
            slot: Slot number (1-8) or "all"
            channel: Optional channel 'a' or 'b' (both if None)

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        cmd = f"ssdrst {slot_str}"
        if channel:
            cmd += f" {channel}"
        response = self._send_command(cmd)
        return "success" in response.lower()

    # Environmental Monitoring

    def get_environmental_data(self) -> Dict:
        """
        Get environmental data (temperatures, voltages, currents, fan speeds)

        Returns:
            Dictionary containing all environmental data
        """
        response = self._send_command("lsd")
        data: Dict[str, Dict[str, float]] = {
            "temperatures": {},
            "fan_speeds": {},
            "voltages": {},
            "currents": {},
            "powers": {},
        }

        lines = response.split("\n")

        for line in lines:
            # Parse temperatures
            temp_match = re.search(r"Slot(\d+)\s+Temperature\s*:\s*([\d.]+)", line)
            if temp_match:
                slot = int(temp_match.group(1))
                temp = float(temp_match.group(2))
                data["temperatures"][f"slot_{slot}"] = temp

            # Parse MCU temperature
            mcu_temp_match = re.search(r"MCU\s+Temperature\s*:\s*([\d.]+)", line)
            if mcu_temp_match:
                data["temperatures"]["mcu"] = float(mcu_temp_match.group(1))

            # Parse fan speeds
            fan_match = re.search(r"Switch\s+Fan(\d+)\s*:\s*(\d+)\s*RPM", line)
            if fan_match:
                fan_num = int(fan_match.group(1))
                rpm = int(fan_match.group(2))
                data["fan_speeds"][f"fan_{fan_num}"] = rpm

            # Parse voltages
            voltage_match = re.search(r"12V\s+Voltage\s*:\s*([\d.]+)\s*V", line)
            if voltage_match:
                data["voltages"]["psu_12v"] = float(voltage_match.group(1))

            # Parse slot voltages/currents/powers
            slot_power_match = re.search(
                r"Slot\s+(\d+)\s+Bus\s+Voltage\s*:\s*([\d.]+)\s*V.*?"
                r"Slot\s+\d+\s+Load\s+Current\s*:\s*([\d.]+)\s*A.*?"
                r"Slot\s+\d+\s+Load\s+Power\s*:\s*([\d.]+)\s*W",
                line,
            )
            if slot_power_match:
                slot = int(slot_power_match.group(1))
                data["voltages"][f"slot_{slot}"] = float(slot_power_match.group(2))
                data["currents"][f"slot_{slot}"] = float(slot_power_match.group(3))
                data["powers"][f"slot_{slot}"] = float(slot_power_match.group(4))

        return data

    # Slot Information

    def show_slot_info(self) -> List[SlotInfo]:
        """
        Get detailed information about all slots

        Returns:
            List of SlotInfo objects
        """
        response = self._send_command("showslot")
        slots = []

        for line in response.split("\n"):
            match = re.search(
                r"Slot(\d+):\s+PC:\s+(\w+),\s+INT:\s+(\w+),\s+EDSFF:\s+(\w+),\s+Present:\s+(\w+)",
                line,
            )
            if match:
                slot_info = SlotInfo(
                    slot_number=int(match.group(1)),
                    paddle_card=match.group(2),
                    interposer=match.group(3),
                    edsff_type=match.group(4),
                    present=(match.group(5).lower() == "yes"),
                )
                slots.append(slot_info)

        return slots

    # LED Control

    def control_host_led(self, slot: Union[int, str], state: PowerState) -> bool:
        """
        Control host LED on EDSFF drives

        Args:
            slot: Slot number (1-8) or "all"
            state: PowerState.ON or PowerState.OFF

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        response = self._send_command(f"hled {slot_str} {state.value}")
        return "success" in response.lower()

    def control_fault_led(self, slot: Union[int, str], state: PowerState) -> bool:
        """
        Control fault LEDs

        Args:
            slot: Slot number (1-8) or "all"
            state: PowerState.ON or PowerState.OFF

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        response = self._send_command(f"fled {slot_str} {state.value}")
        return "success" in response.lower()

    # Fan Control

    def set_fan_speed(self, fan_id: int, duty_cycle: int) -> bool:
        """
        Set fan PWM duty cycle

        Args:
            fan_id: Fan ID (1 or 2)
            duty_cycle: PWM duty cycle (0-100%)

        Returns:
            True if successful
        """
        if not 1 <= fan_id <= 2:
            raise ValueError("Fan ID must be 1 or 2")
        if not 0 <= duty_cycle <= 100:
            raise ValueError("Duty cycle must be between 0 and 100")

        response = self._send_command(f"pwmctrl {fan_id} {duty_cycle}")
        return "success" in response.lower()

    # Other Controls

    def control_buzzer(self, state: BuzzerState) -> bool:
        """
        Control buzzer

        Args:
            state: BuzzerState value

        Returns:
            True if successful
        """
        response = self._send_command(f"buz {state.value}")
        return (
            "turn" in response.lower()
            or "enable" in response.lower()
            or "disable" in response.lower()
        )

    def check_clock_input(self) -> Dict[int, bool]:
        """
        Check clock input status for all slots

        Returns:
            Dictionary of slot number to clock present status
        """
        response = self._send_command("clk")
        clock_status = {}

        for line in response.split("\n"):
            match = re.search(r"Slot\s+(\d+)\s+clk\s+input:\s+(\w+)", line)
            if match:
                slot = int(match.group(1))
                has_clock = match.group(2).lower() == "yes"
                clock_status[slot] = has_clock

        return clock_status

    def get_version_info(self) -> Dict[str, str]:
        """
        Get product and firmware version information

        Returns:
            Dictionary containing version information
        """
        response = self._send_command("ver")
        info = {}

        for line in response.split("\n"):
            if "Company" in line:
                info["company"] = line.split(":")[-1].strip()
            elif "Model" in line:
                info["model"] = line.split(":")[-1].strip()
            elif "Serial No" in line:
                info["serial_number"] = line.split(":")[-1].strip()
            elif "Version" in line and "Version" not in info:
                info["version"] = line.split(":")[-1].strip()
            elif "Build Time" in line:
                info["build_time"] = line.split(":", 1)[-1].strip()

        return info

    def run_diagnostics(self) -> Dict[str, str]:
        """
        Run on-board device diagnostics

        Returns:
            Dictionary of device addresses to status
        """
        response = self._send_command("bist")
        diagnostics = {}

        for line in response.split("\n"):
            match = re.search(r"CH\d+\s+(\S+)\s+0x(\w+)\s+(\w+)", line)
            if match:
                device = match.group(1)
                address = match.group(2)
                status = match.group(3)
                diagnostics[f"{device}@0x{address}"] = status

        return diagnostics

    def get_system_info(self) -> SystemInfo:
        """
        Get complete system information

        Returns:
            SystemInfo object with all system details
        """
        _ = self._send_command("sysinfo")

        # Parse version info
        version_info = self.get_version_info()

        # Parse slot information
        slots = self.show_slot_info()

        # Get environmental data for additional details
        env_data = self.get_environmental_data()

        # Update slot info with environmental data
        for slot in slots:
            slot_key = f"slot_{slot.slot_number}"
            if slot_key in env_data["temperatures"]:
                slot.temperature = env_data["temperatures"][slot_key]
            if slot_key in env_data["voltages"]:
                slot.voltage = env_data["voltages"][slot_key]
            if slot_key in env_data["currents"]:
                slot.current = env_data["currents"][slot_key]
            if slot_key in env_data["powers"]:
                slot.power = env_data["powers"][slot_key]

        return SystemInfo(
            company=version_info.get("company", "Serial Cables"),
            model=version_info.get("model", "PCIe Gen6 8Bays JBOF"),
            serial_number=version_info.get("serial_number", ""),
            firmware_version=version_info.get("version", ""),
            build_time=version_info.get("build_time", ""),
            slots=slots,
            fan1_rpm=env_data["fan_speeds"].get("fan_1", 0),
            fan2_rpm=env_data["fan_speeds"].get("fan_2", 0),
            psu_voltage=env_data["voltages"].get("psu_12v", 0.0),
        )

    # I2C/SMBus Commands

    def i2c_write(self, address: int, slot: int, data: List[int]) -> bool:
        """
        Write data to I2C/SMBus device

        Args:
            address: Device address (hex)
            slot: Slot number (1-8)
            data: List of bytes to write

        Returns:
            True if successful
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        hex_data = " ".join(f"{b:02x}" for b in data)
        response = self._send_command(f"iicw {address:02x} {slot} {hex_data}")
        return "Write Data" in response

    def i2c_read(self, address: int, slot: int, register: int, length: int) -> List[int]:
        """
        Read data from I2C/SMBus device

        Args:
            address: Device address (hex)
            slot: Slot number (1-8)
            register: Register address to read from
            length: Number of bytes to read (max 128)

        Returns:
            List of bytes read
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")
        if not 1 <= length <= 128:
            raise ValueError("Read length must be between 1 and 128")

        response = self._send_command(f"iicwr {address:02x} {slot} {length} {register:02x}")

        # Parse response for data bytes
        data = []
        for line in response.split("\n"):
            match = re.search(r"Data\s*\[\d+\]\s*=\s*0x(\w+)", line)
            if match:
                data.append(int(match.group(1), 16))

        return data

    # Dual Port Control

    def set_dual_port(self, slot: Union[int, str], enabled: bool) -> bool:
        """
        Toggle SSD dual-port enable line

        Args:
            slot: Slot number (1-8) or "all"
            enabled: True to enable, False to disable

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        state = "on" if enabled else "off"
        response = self._send_command(f"dual {slot_str} {state}")
        return "dual port:" in response.lower()

    def set_pwrdis(self, slot: Union[int, str], level: SignalLevel) -> bool:
        """
        Control PWRDIS signal

        Args:
            slot: Slot number (1-8) or "all"
            level: SignalLevel.HIGH to disable power, SignalLevel.LOW to enable

        Returns:
            True if successful
        """
        slot_str = str(slot) if isinstance(slot, int) else slot
        response = self._send_command(f"pwrdis {slot_str} {level.value}")
        return "success" in response.lower() or "pwrdis level" in response.lower()

    # NVMe-MI / MCTP Commands

    def send_mctp_packet(
        self, dest_eid: int, mctp_frame: List[int], timeout: Optional[float] = None
    ) -> MCTPResponse:
        """
        Send an NVMe-MI packet via MCTP to a destination endpoint.

        Args:
            dest_eid: Destination Endpoint ID (slot number, typically 1-8)
            mctp_frame: Raw MCTP frame bytes as a list of integers (0-255)
            timeout: Optional timeout override for this command (seconds).
                     MCTP operations may need longer timeouts than default.

        Returns:
            MCTPResponse containing:
                - success: True if command sent successfully
                - packets_sent: Number of packets sent
                - response_packets: List of response packet byte arrays
                - raw_response: The raw response string from the device

        Example:
            # Send an NVMe-MI Health Status Poll command
            frame = [0x3a, 0x0f, 0x11, 0x21, 0x01, 0x00, 0x00, 0xfc,
                     0x84, 0x00, 0x00, 0x00, 0x04, 0x45, 0x00, 0x00,
                     0xcd, 0x21, 0xec, 0x1e, 0xc1]
            response = controller.send_mctp_packet(dest_eid=7, mctp_frame=frame)
            if response.success and response.response_packets:
                print(f"Response: {response.response_packets[0]}")
        """
        if not mctp_frame:
            raise ValueError("MCTP frame cannot be empty")

        # Validate all bytes are in valid range
        for i, byte in enumerate(mctp_frame):
            if not 0 <= byte <= 255:
                raise ValueError(f"Invalid byte value at index {i}: {byte}")

        # Build command: packet <dest_EID> <hex bytes separated by spaces>
        hex_bytes = " ".join(f"{b:x}" for b in mctp_frame)
        command = f"packet {dest_eid} {hex_bytes}"

        # Use custom timeout if provided, MCTP may need longer
        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(command)
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        # Parse the response
        success = "command sent successfully" in response.lower()
        packets_sent = 0
        response_packets: List[List[int]] = []

        # Parse number of packets sent
        sent_match = re.search(r"sending packet (\d+)/(\d+)", response.lower())
        if sent_match:
            packets_sent = int(sent_match.group(2))

        # Parse response packets
        # Format: "Receive packet N: XX XX XX XX ..."
        for line in response.split("\n"):
            recv_match = re.search(r"Receive packet \d+:\s*([0-9a-fA-F\s]+)", line, re.IGNORECASE)
            if recv_match:
                hex_str = recv_match.group(1).strip()
                # Parse space-separated hex bytes
                packet_bytes = []
                for hex_byte in hex_str.split():
                    try:
                        packet_bytes.append(int(hex_byte, 16))
                    except ValueError:
                        continue
                if packet_bytes:
                    response_packets.append(packet_bytes)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )

    def _parse_mctp_response(self, response: str) -> tuple:
        """
        Parse MCTP command response into success status and packet data.

        Args:
            response: Raw response string from the device

        Returns:
            Tuple of (success, packets_sent, response_packets)
        """
        success = "command sent successfully" in response.lower()
        packets_sent = 0
        response_packets: List[List[int]] = []

        # Parse number of packets sent
        sent_match = re.search(r"sending packet (\d+)/(\d+)", response.lower())
        if sent_match:
            packets_sent = int(sent_match.group(2))

        # Parse response packets
        # Format: "Receive packet N: XX XX XX XX ..."
        for line in response.split("\n"):
            recv_match = re.search(r"Receive packet \d+:\s*([0-9a-fA-F\s]+)", line, re.IGNORECASE)
            if recv_match:
                hex_str = recv_match.group(1).strip()
                # Parse space-separated hex bytes
                packet_bytes = []
                for hex_byte in hex_str.split():
                    try:
                        packet_bytes.append(int(hex_byte, 16))
                    except ValueError:
                        continue
                if packet_bytes:
                    response_packets.append(packet_bytes)

        return success, packets_sent, response_packets

    def mctp_get_serial_number(
        self, slot: int, timeout: Optional[float] = None
    ) -> NVMeSerialNumber:
        """
        Get NVMe drive serial number via MCTP.

        Uses the 'mctp <slot> sn' command to retrieve the drive's serial number.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds).
                     Default timeout may be insufficient for MCTP operations.

        Returns:
            NVMeSerialNumber containing:
                - slot: The slot number queried
                - serial_number: The drive's serial number (empty string if failed)
                - success: True if serial number was retrieved
                - raw_packets: List of raw response packet byte arrays
                - error: Error message if command failed

        Example:
            result = controller.mctp_get_serial_number(slot=1)
            if result.success:
                print(f"Drive serial number: {result.serial_number}")
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        # Use custom timeout if provided
        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} sn")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        # Parse the response
        success, _, response_packets = self._parse_mctp_response(response)

        serial_number = ""
        error = None

        if success and response_packets:
            # Extract serial number from response packet
            # Based on the example response, the serial number starts at byte offset 28
            # in the MCTP payload (after MCTP header and NVMe-MI header)
            # Response: 20 f 31 3b 1 0 0 d3 84 90 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            #           S  7  V  H  N  G  0  X  7  0  0  0  0  1  0  ...
            # The serial number is ASCII starting around byte 28
            try:
                all_bytes = []
                for pkt in response_packets:
                    all_bytes.extend(pkt)

                # NVMe-MI response structure:
                # Bytes 0-3: MCTP header
                # Bytes 4-7: NVMe-MI header
                # Bytes 8+: NVMe-MI payload (contains serial number as ASCII)
                # The serial number field is 20 bytes, ASCII, space-padded

                # Find the serial number in the payload
                # Looking at the example, serial number starts at byte 28:
                # "53 37 56 48 4e 47 30 58 37 30 30 30 30 31 30 20 20 20 20 20"
                # = "S7VHNG0X700010     "
                if len(all_bytes) >= 28:
                    # Extract 20 bytes for serial number (standard NVMe SN length)
                    sn_bytes = all_bytes[28:48]
                    serial_number = "".join(
                        chr(b) if 32 <= b <= 126 else "" for b in sn_bytes
                    ).strip()
            except (IndexError, ValueError) as e:
                error = f"Failed to parse serial number: {e}"
                success = False
        elif not success:
            error = "Command failed or no response received"

        return NVMeSerialNumber(
            slot=slot,
            serial_number=serial_number,
            success=success and bool(serial_number),
            raw_packets=response_packets,
            error=error,
        )

    def mctp_get_health_status(
        self, slot: int, timeout: Optional[float] = None
    ) -> NVMeHealthStatus:
        """
        Get NVMe drive health status via MCTP.

        Uses the 'mctp <slot> health' command to retrieve the drive's health status.
        Note: Not all NVMe drives support this command and may return an
        'Unsupported Command' error.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds).
                     Default timeout may be insufficient for MCTP operations.

        Returns:
            NVMeHealthStatus containing:
                - slot: The slot number queried
                - success: True if health status was retrieved
                - raw_packets: List of raw response packet byte arrays
                - composite_temperature: Drive temperature in Kelvin (if available)
                - composite_temperature_celsius: Drive temperature in Celsius
                - available_spare: Available spare percentage (if available)
                - available_spare_threshold: Spare threshold percentage (if available)
                - percentage_used: Percentage of drive life used (if available)
                - critical_warning: Critical warning bit field (if available)
                - error: Error message if command failed or unsupported

        Example:
            result = controller.mctp_get_health_status(slot=2)
            if result.success:
                print(f"Temperature: {result.composite_temperature_celsius}°C")
                print(f"Available spare: {result.available_spare}%")
            else:
                print(f"Health status unavailable: {result.error}")
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        # Use custom timeout if provided
        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} health")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        # Parse the response
        success, _, response_packets = self._parse_mctp_response(response)

        # Initialize health status fields
        composite_temp: Optional[int] = None
        composite_temp_celsius: Optional[float] = None
        available_spare: Optional[int] = None
        available_spare_threshold: Optional[int] = None
        percentage_used: Optional[int] = None
        critical_warning: Optional[int] = None
        error: Optional[str] = None

        if success and response_packets:
            try:
                all_bytes = []
                for pkt in response_packets:
                    all_bytes.extend(pkt)

                # NVMe-MI Health Status Poll response structure:
                # Bytes 0-3: MCTP header (20 0f XX 3b)
                # Bytes 4-7: NVMe-MI message header (01 00 00 XX)
                # Byte 8-11: NVMe-MI response header (84 88 00 00)
                # Byte 12+: NVMe-MI Health Status data
                #
                # From the example response:
                # 20 f 19 3b 1 0 0 c3 84 88 0 0 0 0 0 0 38 ff 22 0 21 3 0 0 f7 37 6f 25 f3
                # Health data starts at byte 12:
                # Byte 16-17: Composite Temperature (little-endian, Kelvin)
                # The format follows NVMe Health Information Log structure

                if len(all_bytes) >= 18:
                    # Check for unsupported command status in NVMe-MI header
                    # Status byte is typically at offset 9 (after MCTP + NVMe-MI headers)
                    nvme_mi_status = all_bytes[9] if len(all_bytes) > 9 else 0

                    # 0x80 in the status indicates success, other values may indicate error
                    if nvme_mi_status != 0x88:
                        # Try to extract health data anyway
                        pass

                    # Extract temperature (bytes 16-17, little-endian, in Kelvin)
                    if len(all_bytes) >= 18:
                        composite_temp = all_bytes[16] | (all_bytes[17] << 8)
                        # Convert to Celsius (Kelvin - 273.15)
                        if composite_temp > 0 and composite_temp < 1000:
                            composite_temp_celsius = round(composite_temp - 273.15, 1)

                    # Extract available spare (byte 18)
                    if len(all_bytes) >= 19:
                        available_spare = all_bytes[18]

                    # Extract available spare threshold (byte 19)
                    if len(all_bytes) >= 20:
                        available_spare_threshold = all_bytes[19]

                    # Extract percentage used (byte 20)
                    if len(all_bytes) >= 21:
                        percentage_used = all_bytes[20]

                    # Extract critical warning (byte 21)
                    if len(all_bytes) >= 22:
                        critical_warning = all_bytes[21]

            except (IndexError, ValueError) as e:
                error = f"Failed to parse health status: {e}"
                success = False
        elif not success:
            # Check if it's an unsupported command error
            if "unsupported" in response.lower():
                error = "Unsupported Command - drive does not support health status poll"
            else:
                error = "Command failed or no response received"

        return NVMeHealthStatus(
            slot=slot,
            success=success and composite_temp is not None,
            raw_packets=response_packets,
            composite_temperature=composite_temp,
            composite_temperature_celsius=composite_temp_celsius,
            available_spare=available_spare,
            available_spare_threshold=available_spare_threshold,
            percentage_used=percentage_used,
            critical_warning=critical_warning,
            error=error,
        )

    def mctp_pause(self, slot: int, timeout: Optional[float] = None) -> MCTPResponse:
        """
        Send MCTP pause command to a slot.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds)

        Returns:
            MCTPResponse containing success status and any response packets
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} pause")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        success, packets_sent, response_packets = self._parse_mctp_response(response)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )

    def mctp_resume(self, slot: int, timeout: Optional[float] = None) -> MCTPResponse:
        """
        Send MCTP resume command to a slot.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds)

        Returns:
            MCTPResponse containing success status and any response packets
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} resume")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        success, packets_sent, response_packets = self._parse_mctp_response(response)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )

    def mctp_abort(self, slot: int, timeout: Optional[float] = None) -> MCTPResponse:
        """
        Send MCTP abort command to a slot.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds)

        Returns:
            MCTPResponse containing success status and any response packets
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} abort")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        success, packets_sent, response_packets = self._parse_mctp_response(response)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )

    def mctp_status(self, slot: int, timeout: Optional[float] = None) -> MCTPResponse:
        """
        Get MCTP status for a slot.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds)

        Returns:
            MCTPResponse containing success status and any response packets
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} status")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        success, packets_sent, response_packets = self._parse_mctp_response(response)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )

    def mctp_replay(self, slot: int, timeout: Optional[float] = None) -> MCTPResponse:
        """
        Send MCTP replay command to a slot.

        Args:
            slot: Slot number (1-8)
            timeout: Optional timeout override for this command (seconds)

        Returns:
            MCTPResponse containing success status and any response packets
        """
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8")

        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        try:
            response = self._send_command(f"mctp {slot} replay")
        finally:
            if timeout is not None:
                self.timeout = original_timeout

        success, packets_sent, response_packets = self._parse_mctp_response(response)

        return MCTPResponse(
            success=success,
            packets_sent=packets_sent,
            response_packets=response_packets,
            raw_response=response,
        )
