"""Enumerations for JBOF Controller"""

from enum import Enum


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
