"""
Serial Cables HYDRA Controller Library
Python library for controlling Serial Cables PCIe Gen6 HYDRA JBOF systems.
"""

from .controller import (
    JBOFController,
    PowerState,
    BuzzerState,
    SignalLevel,
    SlotNumber,
    SlotInfo,
    SystemInfo,
    MCTPResponse,
    NVMeSerialNumber,
    NVMeHealthStatus,
)
from .monitor import JBOFMonitor

__version__ = "1.3.0"
__author__ = "Serial Cables Engineering"
__email__ = "hydra@serialcables.com"

__all__ = [
    "JBOFController",
    "JBOFMonitor",
    "PowerState",
    "BuzzerState",
    "SignalLevel",
    "SlotNumber",
    "SlotInfo",
    "SystemInfo",
    "MCTPResponse",
    "NVMeSerialNumber",
    "NVMeHealthStatus",
]
