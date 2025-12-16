"""Data models for JBOF Controller"""

from dataclasses import dataclass
from typing import List


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
