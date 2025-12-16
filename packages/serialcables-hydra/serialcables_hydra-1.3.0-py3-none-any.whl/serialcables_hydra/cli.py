"""
Command-line interface for Serial Cables HYDRA
"""

import argparse
import sys
from .controller import JBOFController


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Serial Cables HYDRA Controller CLI")
    parser.add_argument("--port", "-p", required=True, help="Serial port")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()

    controller = JBOFController(port=args.port)
    if not controller.connect():
        print("Failed to connect to HYDRA system")
        sys.exit(1)

    # Execute command
    if args.command == "status":
        info = controller.get_system_info()
        print(f"HYDRA System: {info.model}")
        print(f"Firmware: {info.firmware_version}")

    controller.disconnect()


if __name__ == "__main__":
    main()
