"""
Custom exceptions for the Hermes API.

This module defines exception classes for error handling in the
serialcables-hermes package.
"""

from typing import Any


class HermesError(Exception):
    """Base exception for all Hermes-related errors."""

    pass


class ConnectionError(HermesError):
    """Raised when connection to the device fails."""

    pass


class TimeoutError(HermesError):
    """Raised when a command times out waiting for response."""

    pass


class CommandError(HermesError):
    """Raised when a command execution fails."""

    pass


class ParseError(HermesError):
    """Raised when response parsing fails."""

    pass


class ValidationError(HermesError):
    """Raised when input validation fails."""

    pass


class DeviceNotFoundError(ConnectionError):
    """Raised when the specified device is not found."""

    pass


class DeviceNotReadyError(HermesError):
    """Raised when the device is not in a ready state."""

    pass


class ConfigurationError(HermesError):
    """Raised when there is a configuration issue."""

    pass


class FirmwareUpdateError(HermesError):
    """Raised when firmware update fails."""

    pass


class I2CError(HermesError):
    """Raised when I2C/SMBus communication fails."""

    pass


class InvalidChipError(ValidationError):
    """Raised when an invalid chip number is specified."""

    def __init__(self, chip: int, max_chips: int):
        self.chip = chip
        self.max_chips = max_chips
        super().__init__(f"Invalid chip number {chip}. Must be 0-{max_chips - 1} or 'all'.")


class InvalidChannelError(ValidationError):
    """Raised when an invalid channel number is specified."""

    def __init__(self, channel: int, max_channels: int = 4):
        self.channel = channel
        self.max_channels = max_channels
        super().__init__(f"Invalid channel number {channel}. Must be 0-{max_channels - 1}.")


class InvalidValueError(ValidationError):
    """Raised when an invalid parameter value is specified."""

    def __init__(self, param_name: str, value: Any, valid_range: str):
        self.param_name = param_name
        self.value = value
        self.valid_range = valid_range
        super().__init__(f"Invalid {param_name} value: {value}. Valid range: {valid_range}.")


class BISTFailureError(HermesError):
    """Raised when Built-In Self Test detects a failure."""

    def __init__(self, failed_devices: list):
        self.failed_devices = failed_devices
        device_list = ", ".join(failed_devices)
        super().__init__(f"BIST failed for devices: {device_list}")
