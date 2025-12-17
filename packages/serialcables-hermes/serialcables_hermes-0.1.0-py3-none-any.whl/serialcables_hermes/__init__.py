"""
Serial Cables Hermes - PCIe Gen6 EDSFF Redriver Card API.

This package provides a Python API for communicating with Serial Cables
PCIe Gen6 EDSFF Redriver cards (PCI6-AD-x8EDSFF and PCI6-AD-x16EDSFF series).

Example usage:
    >>> from serialcables_hermes import Hermes
    >>>
    >>> # Auto-detect device
    >>> port = Hermes.find_device()
    >>>
    >>> # Connect and query
    >>> with Hermes(port) as hermes:
    ...     info = hermes.get_version()
    ...     print(f"Model: {info.product.model}")
    ...     print(f"Serial: {info.product.serial_number}")
    ...
    ...     status = hermes.get_status()
    ...     print(f"Temperature: {status.thermal}")
    ...     print(f"Current: {status.current}")
    ...
    ...     # Get EQ settings
    ...     eq = hermes.get_eq_settings()
    ...     print(eq)
    ...
    ...     # Set EQ for all chips
    ...     hermes.set_eq('all', 5)  # 8.2 dB
    ...
    ...     # Save configuration
    ...     hermes.save_configuration()

For detailed documentation, see https://github.com/serialcables/serialcables-hermes
"""

__version__ = "0.1.0"
__author__ = "Serial Cables, LLC"
__email__ = "support@serialcables.com"

# Constants and enums
from .constants import (
    CHIPS_PER_CARD,
    EQ_VALUES,
    FG_VALUES,
    SW_VALUES,
    CardType,
    Channel,
    DeviceWidth,
    DualPortState,
    LEDColor,
    LEDState,
    LoadMode,
    PowerDisableLevel,
)

# Exceptions
from .exceptions import (
    BISTFailureError,
    CommandError,
    ConfigurationError,
    ConnectionError,
    DeviceNotFoundError,
    DeviceNotReadyError,
    FirmwareUpdateError,
    HermesError,
    I2CError,
    InvalidChannelError,
    InvalidChipError,
    InvalidValueError,
    ParseError,
    TimeoutError,
    ValidationError,
)

# Main API class
from .hermes import Hermes

# Data models
from .models import (
    BISTResult,
    CardInfo,
    CardStatus,
    ChannelEQ,
    ChannelFG,
    ChannelSW,
    ChannelTuning,
    ChipEQ,
    ChipFG,
    ChipSW,
    CurrentInfo,
    DualPortStatus,
    EDSFFDetection,
    EQSettings,
    FanInfo,
    FGSettings,
    I2CDevice,
    I2CReadResult,
    I2CWriteResult,
    LoadConfiguration,
    MCUInfo,
    PERSTResult,
    ProductInfo,
    ResetResult,
    SaveResult,
    SWSettings,
    SystemInfo,
    ThermalInfo,
    VersionInfo,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__email__",
    # Main class
    "Hermes",
    # Models
    "BISTResult",
    "CardInfo",
    "CardStatus",
    "ChannelEQ",
    "ChannelFG",
    "ChannelSW",
    "ChannelTuning",
    "ChipEQ",
    "ChipFG",
    "ChipSW",
    "CurrentInfo",
    "DualPortStatus",
    "EDSFFDetection",
    "EQSettings",
    "FanInfo",
    "FGSettings",
    "I2CDevice",
    "I2CReadResult",
    "I2CWriteResult",
    "LoadConfiguration",
    "MCUInfo",
    "PERSTResult",
    "ProductInfo",
    "ResetResult",
    "SaveResult",
    "SWSettings",
    "SystemInfo",
    "ThermalInfo",
    "VersionInfo",
    # Constants/Enums
    "CardType",
    "Channel",
    "CHIPS_PER_CARD",
    "DeviceWidth",
    "DualPortState",
    "EQ_VALUES",
    "FG_VALUES",
    "LEDColor",
    "LEDState",
    "LoadMode",
    "PowerDisableLevel",
    "SW_VALUES",
    # Exceptions
    "BISTFailureError",
    "CommandError",
    "ConfigurationError",
    "ConnectionError",
    "DeviceNotFoundError",
    "DeviceNotReadyError",
    "FirmwareUpdateError",
    "HermesError",
    "I2CError",
    "InvalidChannelError",
    "InvalidChipError",
    "InvalidValueError",
    "ParseError",
    "TimeoutError",
    "ValidationError",
]
