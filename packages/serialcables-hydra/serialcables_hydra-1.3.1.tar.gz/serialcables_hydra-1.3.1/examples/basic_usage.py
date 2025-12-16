#!/usr/bin/env python3
"""
Example usage script for the Serial Cables PCIe Gen6 JBOF Controller

This script demonstrates how to:
- Connect to the JBOF enclosure
- Query system information and status
- Control slot power
- Monitor environmental data
- Control LEDs and fans
- Run diagnostics
"""

import time
import logging
from serialcables_hydra import JBOFController, PowerState, BuzzerState

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main example function demonstrating JBOF controller usage"""

    # Initialize the controller
    # Update the port to match your system:
    # - Linux: '/dev/ttyUSB0' or '/dev/ttyACM0'
    # - Windows: 'COM3' or 'COM4'
    # - macOS: '/dev/tty.usbserial-*'
    jbof = JBOFController(port="/dev/ttyUSB0", baudrate=115200)

    try:
        # ========================================
        # Connect to the JBOF
        # ========================================
        if not jbof.connect():
            logger.error("Failed to connect to JBOF")
            return

        logger.info("Successfully connected to JBOF")

        # ========================================
        # Get version information
        # ========================================
        logger.info("Getting version information...")
        version_info = jbof.get_version_info()
        for key, value in version_info.items():
            logger.info(f"  {key}: {value}")

        # ========================================
        # Get slot information
        # ========================================
        logger.info("\nGetting slot information...")
        slots = jbof.show_slot_info()
        for slot in slots:
            logger.info(f"  Slot {slot.slot_number}:")
            logger.info(f"    Paddle Card: {slot.paddle_card}")
            logger.info(f"    Interposer: {slot.interposer}")
            logger.info(f"    EDSFF Type: {slot.edsff_type}")
            logger.info(f"    Present: {slot.present}")

        # ========================================
        # Get environmental data
        # ========================================
        logger.info("\nGetting environmental data...")
        env_data = jbof.get_environmental_data()

        logger.info("  Temperatures:")
        for location, temp in env_data["temperatures"].items():
            logger.info(f"    {location}: {temp}°C")

        logger.info("  Fan Speeds:")
        for fan, rpm in env_data["fan_speeds"].items():
            logger.info(f"    {fan}: {rpm} RPM")

        logger.info("  Power Readings:")
        for slot, power in env_data["powers"].items():
            logger.info(f"    {slot}: {power} W")

        # ========================================
        # Check clock input status
        # ========================================
        logger.info("\nChecking clock input status...")
        clock_status = jbof.check_clock_input()
        for slot, has_clock in clock_status.items():
            logger.info(f"  Slot {slot}: {'Clock present' if has_clock else 'No clock'}")

        # ========================================
        # Example: Control slot power
        # ========================================
        logger.info("\nControlling slot power...")

        # Power off slot 1
        if jbof.slot_power(1, PowerState.OFF):
            logger.info("  Slot 1 powered off successfully")
            time.sleep(2)

        # Power on slot 1
        if jbof.slot_power(1, PowerState.ON):
            logger.info("  Slot 1 powered on successfully")

        # Get current power status
        power_status = jbof.get_slot_power_status()
        logger.info("  Current power status:")
        for slot, status in power_status.items():
            logger.info(f"    Slot {slot}: {status}")

        # ========================================
        # Example: Control LEDs
        # ========================================
        logger.info("\nControlling LEDs...")

        # Turn on fault LED for slot 2
        if jbof.control_fault_led(2, PowerState.ON):
            logger.info("  Slot 2 fault LED turned on")
            time.sleep(2)

        # Turn off fault LED
        if jbof.control_fault_led(2, PowerState.OFF):
            logger.info("  Slot 2 fault LED turned off")

        # ========================================
        # Example: Fan control
        # ========================================
        logger.info("\nControlling fans...")

        # Set fan 1 to 50% speed
        if jbof.set_fan_speed(1, 50):
            logger.info("  Fan 1 set to 50% speed")
            time.sleep(3)

        # Set fan 1 back to 100%
        if jbof.set_fan_speed(1, 100):
            logger.info("  Fan 1 set to 100% speed")

        # ========================================
        # Example: Run diagnostics
        # ========================================
        logger.info("\nRunning diagnostics...")
        diag_results = jbof.run_diagnostics()
        for device, status in diag_results.items():
            logger.info(f"  {device}: {status}")

        # ========================================
        # Example: Buzzer test
        # ========================================
        logger.info("\nTesting buzzer...")

        # Turn on buzzer briefly
        if jbof.control_buzzer(BuzzerState.ON):
            logger.info("  Buzzer turned on")
            time.sleep(1)

        if jbof.control_buzzer(BuzzerState.OFF):
            logger.info("  Buzzer turned off")

        # ========================================
        # Get complete system information
        # ========================================
        logger.info("\nGetting complete system information...")
        sys_info = jbof.get_system_info()
        logger.info(f"  Model: {sys_info.model}")
        logger.info(f"  Firmware: {sys_info.firmware_version}")
        logger.info(f"  PSU Voltage: {sys_info.psu_voltage} V")
        logger.info(f"  Fan 1: {sys_info.fan1_rpm} RPM")
        logger.info(f"  Fan 2: {sys_info.fan2_rpm} RPM")

        for slot in sys_info.slots:
            if slot.present:
                logger.info(f"  Slot {slot.slot_number}: {slot.temperature}°C, {slot.power}W")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Always disconnect when done
        jbof.disconnect()
        logger.info("Disconnected from JBOF")


if __name__ == "__main__":
    main()
