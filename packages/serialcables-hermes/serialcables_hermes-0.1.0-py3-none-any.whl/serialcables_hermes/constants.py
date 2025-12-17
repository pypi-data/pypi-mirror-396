"""
Constants and enumerations for the Hermes API.

This module defines constants, enumerations, and lookup tables used throughout
the serialcables-hermes package for PCIe Gen6 EDSFF Redriver card communication.
"""

from enum import Enum
from typing import Any, Dict, Tuple


class CardType(Enum):
    """EDSFF Redriver card types."""

    X8 = "x8"
    X16 = "x16"


class LoadMode(Enum):
    """Preset load configuration modes based on trace length."""

    SHORT = "s"  # Less than 9" trace length
    MEDIUM = "m"  # 6-9" trace length (factory default)
    LONG = "l"  # 10-12" trace length


class Channel(Enum):
    """PERST channel selection."""

    A = "a"  # PERST#0 on EDSFF Pin_B10
    B = "b"  # PERST#0 on EDSFF Pin_A11
    BOTH = ""  # Reset both channels


class DualPortState(Enum):
    """Dual port enable state."""

    ON = "on"
    OFF = "off"


class PowerDisableLevel(Enum):
    """PWRDIS signal level."""

    HIGH = "h"  # Disable SSD power
    LOW = "l"  # Enable SSD power


class LEDState(Enum):
    """Host LED state."""

    ON = "on"
    OFF = "off"


class LEDColor(Enum):
    """LED color definitions from EDSFF specification."""

    GREEN = "green"  # Device-driven, Power/Activity
    AMBER = "amber"  # Host LED signal
    BLUE = "blue"  # Host LED signal


class DeviceWidth(Enum):
    """Detected EDSFF device width."""

    X4 = "X4"
    X8 = "X8"
    X16 = "X16"
    NONE = "None"


# EQ setting values (0-15) mapped to dB values
EQ_VALUES: Dict[int, float] = {
    0: 2.3,
    1: 3.2,
    2: 4.3,
    3: 5.4,
    4: 7.2,
    5: 8.2,
    6: 9.5,
    7: 10.3,
    8: 12.0,
    9: 13.0,
    10: 13.9,
    11: 14.6,
    12: 16.3,
    13: 18.6,
    14: 19.9,
    15: 20.8,
}

# Flat gain setting values (0-3) mapped to dB values
FG_VALUES: Dict[int, float] = {
    0: -2.8,
    1: -2.0,
    2: -0.8,
    3: -0.2,
}

# Swing setting values (0-7) mapped to mV values
SW_VALUES: Dict[int, int] = {
    0: 1050,
    1: 1150,
    2: 1270,
    3: 1380,
    4: 1460,
    5: 1490,
    6: 1600,
    7: 1630,
}

# Number of redriver chips per card type
CHIPS_PER_CARD: Dict[CardType, int] = {
    CardType.X8: 4,  # Chips 0-3
    CardType.X16: 8,  # Chips 0-7
}

# Channels per redriver chip
CHANNELS_PER_CHIP: int = 4

# Command prompt string
COMMAND_PROMPT: str = "Cmd>"

# Default serial settings
DEFAULT_BAUDRATE: int = 115200
DEFAULT_TIMEOUT: float = 2.0
DEFAULT_WRITE_TIMEOUT: float = 1.0

# Command timeout settings
COMMAND_TIMEOUT: float = 5.0
RESET_TIMEOUT: float = 10.0
FDL_TIMEOUT: float = 60.0

# LED specifications from EDSFF standard
LED_SPECS: Dict[LEDColor, Dict[str, Any]] = {
    LEDColor.GREEN: {
        "driven_by": "Device",
        "function": "Power, Activity",
        "wavelength_nm": (515, 535),
        "intensity_mcd_min": 45,
    },
    LEDColor.AMBER: {
        "driven_by": "Host (LED signal)",
        "function": "Host defined",
        "wavelength_nm": (585, 600),
        "intensity_mcd_min": 40,
    },
    LEDColor.BLUE: {
        "driven_by": "Host (LED signal)",
        "function": "Host Defined",
        "wavelength_nm": (460, 475),
        "intensity_mcd_min": 20,
    },
}

# I2C device addresses for BIST (Built-In Self Test)
I2C_DEVICES_X16: Dict[str, Tuple[int, int]] = {
    # (channel, address)
    "PS7161-1": (0, 0x3A),
    "PS7161-2": (0, 0x5A),
    "PS7161-3": (0, 0x62),
    "PS7161-4": (0, 0x64),
    "PS7161-5": (0, 0x8E),
    "PS7161-6": (0, 0x6E),
    "PS7161-7": (0, 0x66),
    "PS7161-8": (0, 0x60),
    "PCA9575": (1, 0x42),
    "AT24C64": (1, 0xA0),
}

I2C_DEVICES_X8: Dict[str, Tuple[int, int]] = {
    "PS7161-1": (0, 0x3A),
    "PS7161-2": (0, 0x5A),
    "PS7161-5": (0, 0x8E),
    "PS7161-6": (0, 0x6E),
    "PCA9575": (1, 0x42),
    "AT24C64": (1, 0xA0),
}

# Board dimension specifications (in mm)
BOARD_DIMENSIONS: Dict[CardType, Dict[str, int]] = {
    CardType.X8: {"length": 225, "height": 111},
    CardType.X16: {"length": 255, "height": 111},
}

# Part number patterns
PART_NUMBERS: Dict[str, str] = {
    "PCI6-AD-x8EDSFF-E3-H-SC": "X8 Golden Finger to X8 EDSFF (Standard)",
    "PCI6-AD-x8EDSFF-E3-H-QA": "X8 Golden Finger to X8 EDSFF (Quarch)",
    "PCI6-AD-x16EDSFF-E3-H-SC": "X16 Golden Finger to X16 EDSFF (Standard)",
    "PCI6-AD-x16EDSFF-E3-H-QA": "X16 Golden Finger to X16 EDSFF (Quarch)",
}
