#!/usr/bin/env python3
"""
JBOF Monitoring Utility
Continuous monitoring and alerting for Serial Cables PCIe Gen6 JBOF
"""

import time
import argparse
import csv
from datetime import datetime
from typing import Dict, List, Optional, TextIO
from csv import DictWriter
from .controller import JBOFController


class JBOFMonitor:
    """Monitor class for continuous JBOF monitoring"""

    def __init__(
        self, controller: JBOFController, interval: int = 5, log_file: Optional[str] = None
    ):
        """
        Initialize the monitor

        Args:
            controller: JBOFController instance
            interval: Monitoring interval in seconds
            log_file: Optional CSV file path for logging
        """
        self.controller = controller
        self.interval = interval
        self.log_file = log_file
        self.csv_writer: Optional[DictWriter] = None
        self.csv_file: Optional[TextIO] = None

        # Alert thresholds
        self.temp_warning = 45.0  # °C
        self.temp_critical = 55.0  # °C
        self.voltage_min = 11.5  # V
        self.voltage_max = 12.5  # V
        self.fan_min_rpm = 3000

        if self.log_file:
            self._init_csv_logging()

    def _init_csv_logging(self) -> None:
        """Initialize CSV logging"""
        if self.log_file is None:
            return
        self.csv_file = open(self.log_file, "w", newline="")
        fieldnames = [
            "timestamp",
            "mcu_temp",
            "psu_voltage",
            "fan1_rpm",
            "fan2_rpm",
            "slot1_temp",
            "slot1_power",
            "slot1_present",
            "slot2_temp",
            "slot2_power",
            "slot2_present",
            "slot3_temp",
            "slot3_power",
            "slot3_present",
            "slot4_temp",
            "slot4_power",
            "slot4_present",
            "slot5_temp",
            "slot5_power",
            "slot5_present",
            "slot6_temp",
            "slot6_power",
            "slot6_present",
            "slot7_temp",
            "slot7_power",
            "slot7_present",
            "slot8_temp",
            "slot8_power",
            "slot8_present",
            "alerts",
        ]
        if self.csv_file is not None:
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()

    def check_alerts(self, env_data: Dict, slots: List) -> List[str]:
        """
        Check for alert conditions

        Args:
            env_data: Environmental data dictionary
            slots: List of slot information

        Returns:
            List of alert messages
        """
        alerts = []

        # Check temperatures
        for location, temp in env_data["temperatures"].items():
            if temp >= self.temp_critical:
                alerts.append(
                    f"CRITICAL: {location} temperature {temp}°C exceeds critical threshold"
                )
            elif temp >= self.temp_warning:
                alerts.append(f"WARNING: {location} temperature {temp}°C exceeds warning threshold")

        # Check voltage
        psu_voltage = env_data["voltages"].get("psu_12v", 0)
        if psu_voltage > 0:
            if psu_voltage < self.voltage_min:
                alerts.append(f"CRITICAL: PSU voltage {psu_voltage}V below minimum")
            elif psu_voltage > self.voltage_max:
                alerts.append(f"CRITICAL: PSU voltage {psu_voltage}V above maximum")

        # Check fan speeds
        for fan, rpm in env_data["fan_speeds"].items():
            if rpm < self.fan_min_rpm:
                alerts.append(f"WARNING: {fan} speed {rpm} RPM below minimum")

        return alerts

    def format_display(self, env_data: Dict, slots: List, alerts: List[str]) -> str:
        """
        Format monitoring data for display

        Args:
            env_data: Environmental data
            slots: Slot information
            alerts: Alert messages

        Returns:
            Formatted display string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display = f"\n{'=' * 60}\n"
        display += f"JBOF Monitor - {timestamp}\n"
        display += f"{'=' * 60}\n\n"

        # System status
        display += "System Status:\n"
        display += f"  PSU Voltage: {env_data['voltages'].get('psu_12v', 0):.2f} V\n"
        display += f"  MCU Temp: {env_data['temperatures'].get('mcu', 0):.1f}°C\n"
        display += f"  Fan 1: {env_data['fan_speeds'].get('fan_1', 0)} RPM\n"
        display += f"  Fan 2: {env_data['fan_speeds'].get('fan_2', 0)} RPM\n\n"

        # Slot status
        display += "Slot Status:\n"
        display += "  Slot | Present | Temp  | Power | Voltage | Current\n"
        display += "  -----|---------|-------|-------|---------|--------\n"

        for slot in slots:
            slot_key = f"slot_{slot.slot_number}"
            temp = env_data["temperatures"].get(slot_key, 0)
            power = env_data["powers"].get(slot_key, 0)
            voltage = env_data["voltages"].get(slot_key, 0)
            current = env_data["currents"].get(slot_key, 0)

            display += f"   {slot.slot_number:2d}  | {'Yes' if slot.present else 'No ':>3s}     | "
            display += f"{temp:5.1f}°C | {power:5.1f}W | {voltage:6.2f}V | {current:5.2f}A\n"

        # Alerts
        if alerts:
            display += f"\nAlerts ({len(alerts)}):\n"
            for alert in alerts:
                display += f"  ! {alert}\n"
        else:
            display += "\n✓ No alerts - System operating normally\n"

        return display

    def log_to_csv(self, env_data: Dict, slots: List, alerts: List[str]) -> None:
        """Log monitoring data to CSV"""
        if not self.csv_writer:
            return

        row = {
            "timestamp": datetime.now().isoformat(),
            "mcu_temp": env_data["temperatures"].get("mcu", 0),
            "psu_voltage": env_data["voltages"].get("psu_12v", 0),
            "fan1_rpm": env_data["fan_speeds"].get("fan_1", 0),
            "fan2_rpm": env_data["fan_speeds"].get("fan_2", 0),
            "alerts": ";".join(alerts) if alerts else "",
        }

        # Add slot data
        for slot in slots:
            slot_key = f"slot_{slot.slot_number}"
            row[f"slot{slot.slot_number}_temp"] = env_data["temperatures"].get(slot_key, 0)
            row[f"slot{slot.slot_number}_power"] = env_data["powers"].get(slot_key, 0)
            row[f"slot{slot.slot_number}_present"] = 1 if slot.present else 0

        if self.csv_writer is not None:
            self.csv_writer.writerow(row)
        if self.csv_file is not None:
            self.csv_file.flush()

    def run(self, duration: Optional[int] = None) -> None:
        """
        Run the monitor

        Args:
            duration: Optional duration in seconds (runs forever if None)
        """
        start_time = time.time()

        try:
            while True:
                # Get current data
                env_data = self.controller.get_environmental_data()
                slots = self.controller.show_slot_info()

                # Check for alerts
                alerts = self.check_alerts(env_data, slots)

                # Display status
                print(self.format_display(env_data, slots, alerts))

                # Log to CSV if configured
                self.log_to_csv(env_data, slots, alerts)

                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break

                # Wait for next interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
        finally:
            if self.csv_file:
                self.csv_file.close()


def main() -> int:
    """Main entry point for the monitoring utility"""
    parser = argparse.ArgumentParser(description="JBOF Monitoring Utility")
    parser.add_argument(
        "--port", "-p", required=True, help="Serial port (e.g., /dev/ttyUSB0 or COM3)"
    )
    parser.add_argument(
        "--interval", "-i", type=int, default=5, help="Monitoring interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        help="Monitoring duration in seconds (runs forever if not specified)",
    )
    parser.add_argument("--log", "-l", help="CSV log file path")
    parser.add_argument(
        "--temp-warning",
        type=float,
        default=45.0,
        help="Temperature warning threshold in °C (default: 45)",
    )
    parser.add_argument(
        "--temp-critical",
        type=float,
        default=55.0,
        help="Temperature critical threshold in °C (default: 55)",
    )

    args = parser.parse_args()

    # Create controller
    controller = JBOFController(port=args.port)

    # Connect to JBOF
    if not controller.connect():
        print(f"Failed to connect to JBOF on {args.port}")
        return 1

    print(f"Connected to JBOF on {args.port}")

    # Create and configure monitor
    monitor = JBOFMonitor(controller, interval=args.interval, log_file=args.log)
    monitor.temp_warning = args.temp_warning
    monitor.temp_critical = args.temp_critical

    # Run monitor
    try:
        monitor.run(duration=args.duration)
    finally:
        controller.disconnect()
        print("Disconnected from JBOF")

    return 0


if __name__ == "__main__":
    exit(main())
