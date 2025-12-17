"""
Data models for the Hermes API.

This module defines dataclasses for structured response data from the
PCIe Gen6 EDSFF Redriver card CLI commands.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .constants import CardType, DeviceWidth, LoadMode


@dataclass
class ThermalInfo:
    """Thermal sensor information from the redriver card."""

    temperature_celsius: float

    def __str__(self) -> str:
        return f"{self.temperature_celsius}°C"


@dataclass
class FanInfo:
    """Fan speed information."""

    speed_rpm: int

    def __str__(self) -> str:
        return f"{self.speed_rpm} RPM"


@dataclass
class CurrentInfo:
    """12V current consumption information."""

    current_amps: float

    @property
    def current_milliamps(self) -> float:
        """Return current in milliamps."""
        return self.current_amps * 1000

    @property
    def power_watts(self) -> float:
        """Estimate power consumption at 12V."""
        return self.current_amps * 12.0

    def __str__(self) -> str:
        return f"{self.current_amps:.3f} A"


@dataclass
class CardStatus:
    """Complete card status from 'lsd' command."""

    thermal: ThermalInfo
    fan: FanInfo
    current: CurrentInfo

    def __str__(self) -> str:
        return (
            f"Temperature: {self.thermal}\n"
            f"Fan Speed: {self.fan}\n"
            f"12V Current: {self.current}"
        )


@dataclass
class ChannelEQ:
    """EQ settings for a single channel."""

    channel: int
    eq_step: int
    eq_db: float

    def __str__(self) -> str:
        return f"CH{self.channel}: {self.eq_db} dB (step {self.eq_step})"


@dataclass
class ChipEQ:
    """EQ settings for a single redriver chip."""

    chip: int
    channels: List[ChannelEQ] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Chip{self.chip}:"]
        for ch in self.channels:
            lines.append(f"  {ch}")
        return "\n".join(lines)


@dataclass
class EQSettings:
    """Complete EQ settings for all chips."""

    chips: List[ChipEQ] = field(default_factory=list)

    def get_chip(self, chip_num: int) -> Optional[ChipEQ]:
        """Get settings for a specific chip."""
        for chip in self.chips:
            if chip.chip == chip_num:
                return chip
        return None

    def __str__(self) -> str:
        return "\n".join(str(chip) for chip in self.chips)


@dataclass
class ChannelFG:
    """Flat gain settings for a single channel."""

    channel: int
    fg_step: int
    fg_db: float

    def __str__(self) -> str:
        return f"CH{self.channel}: {self.fg_db} dB (step {self.fg_step})"


@dataclass
class ChipFG:
    """Flat gain settings for a single redriver chip."""

    chip: int
    channels: List[ChannelFG] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Chip{self.chip}:"]
        for ch in self.channels:
            lines.append(f"  {ch}")
        return "\n".join(lines)


@dataclass
class FGSettings:
    """Complete flat gain settings for all chips."""

    chips: List[ChipFG] = field(default_factory=list)

    def get_chip(self, chip_num: int) -> Optional[ChipFG]:
        """Get settings for a specific chip."""
        for chip in self.chips:
            if chip.chip == chip_num:
                return chip
        return None

    def __str__(self) -> str:
        return "\n".join(str(chip) for chip in self.chips)


@dataclass
class ChannelSW:
    """Swing settings for a single channel."""

    channel: int
    sw_step: int
    swing_mv: int

    def __str__(self) -> str:
        return f"CH{self.channel}: {self.swing_mv} mV (step {self.sw_step})"


@dataclass
class ChipSW:
    """Swing settings for a single redriver chip."""

    chip: int
    channels: List[ChannelSW] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Chip{self.chip}:"]
        for ch in self.channels:
            lines.append(f"  {ch}")
        return "\n".join(lines)


@dataclass
class SWSettings:
    """Complete swing settings for all chips."""

    chips: List[ChipSW] = field(default_factory=list)

    def get_chip(self, chip_num: int) -> Optional[ChipSW]:
        """Get settings for a specific chip."""
        for chip in self.chips:
            if chip.chip == chip_num:
                return chip
        return None

    def __str__(self) -> str:
        return "\n".join(str(chip) for chip in self.chips)


@dataclass
class ChannelTuning:
    """Complete tuning parameters for a single channel."""

    chip: int
    channel: int
    eq_step: int
    eq_db: float
    fg_step: int
    fg_db: float
    sw_step: int
    swing_mv: int

    def __str__(self) -> str:
        return (
            f"Chip{self.chip}, CH:{self.channel}, "
            f"EQ: {self.eq_db} dB, FG: {self.fg_db} dB, SW: {self.swing_mv} mV"
        )


@dataclass
class ProductInfo:
    """Product identification information."""

    company: str
    model: str
    serial_number: str

    def __str__(self) -> str:
        return f"{self.company} {self.model} (S/N: {self.serial_number})"


@dataclass
class MCUInfo:
    """MCU firmware information."""

    version: str
    build_time: str

    def __str__(self) -> str:
        return f"Version {self.version} (Built: {self.build_time})"


@dataclass
class VersionInfo:
    """Complete version information from 'ver' command."""

    product: ProductInfo
    mcu: MCUInfo

    def __str__(self) -> str:
        return f"Product: {self.product}\nMCU: {self.mcu}"


@dataclass
class I2CDevice:
    """I2C device status from BIST."""

    channel: int
    device_name: str
    address: int
    status: str

    @property
    def is_ok(self) -> bool:
        """Check if device passed BIST."""
        return self.status.upper() == "OK"

    def __str__(self) -> str:
        return f"CH{self.channel} {self.device_name} @ 0x{self.address:02X}: {self.status}"


@dataclass
class BISTResult:
    """Built-In Self Test results."""

    devices: List[I2CDevice] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """Check if all devices passed BIST."""
        return all(dev.is_ok for dev in self.devices)

    @property
    def failed_devices(self) -> List[I2CDevice]:
        """Get list of failed devices."""
        return [dev for dev in self.devices if not dev.is_ok]

    def __str__(self) -> str:
        status = "PASS" if self.all_passed else "FAIL"
        lines = [f"BIST Result: {status}"]
        for dev in self.devices:
            lines.append(f"  {dev}")
        return "\n".join(lines)


@dataclass
class LoadConfiguration:
    """Load configuration mode information."""

    mode: LoadMode
    description: str

    def __str__(self) -> str:
        return f"{self.mode.name}: {self.description}"


@dataclass
class DualPortStatus:
    """Dual port enable status."""

    enabled: bool

    def __str__(self) -> str:
        return "Enabled" if self.enabled else "Disabled"


@dataclass
class EDSFFDetection:
    """EDSFF device detection result."""

    width: DeviceWidth
    present: bool

    def __str__(self) -> str:
        if not self.present:
            return "No EDSFF device detected"
        return f"EDSFF device detected: {self.width.value}"


@dataclass
class SystemInfo:
    """Complete system information from 'sysinfo' command."""

    version: VersionInfo
    status: CardStatus
    bist: BISTResult

    def __str__(self) -> str:
        return (
            f"=== System Information ===\n"
            f"{self.version}\n\n"
            f"=== Status ===\n"
            f"{self.status}\n\n"
            f"=== BIST ===\n"
            f"{self.bist}"
        )


@dataclass
class I2CReadResult:
    """Result from I2C/SMBus read operation."""

    address: int
    data: List[int]

    def __str__(self) -> str:
        hex_data = " ".join(f"0x{b:02X}" for b in self.data)
        return f"Read from 0x{self.address:02X}: {hex_data}"

    def as_bytes(self) -> bytes:
        """Return data as bytes object."""
        return bytes(self.data)


@dataclass
class I2CWriteResult:
    """Result from I2C/SMBus write operation."""

    address: int
    bytes_written: int
    success: bool

    def __str__(self) -> str:
        status = "Success" if self.success else "Failed"
        return f"Write to 0x{self.address:02X}: {self.bytes_written} bytes - {status}"


@dataclass
class ResetResult:
    """Result from MCU reset operation."""

    success: bool

    def __str__(self) -> str:
        return "MCU Reset Successful" if self.success else "MCU Reset Failed"


@dataclass
class PERSTResult:
    """Result from PERST operation."""

    channel: str
    success: bool

    def __str__(self) -> str:
        ch_str = f"Channel {self.channel}" if self.channel else "Both channels"
        status = "Success" if self.success else "Failed"
        return f"PERST# {ch_str}: {status}"


@dataclass
class SaveResult:
    """Result from save configuration operation."""

    success: bool

    def __str__(self) -> str:
        return "Configuration Saved" if self.success else "Save Failed"


@dataclass
class CardInfo:
    """High-level card information combining multiple queries."""

    card_type: CardType
    version: VersionInfo
    status: CardStatus
    detection: EDSFFDetection
    dual_port: DualPortStatus

    @property
    def num_chips(self) -> int:
        """Get number of redriver chips based on card type."""
        from .constants import CHIPS_PER_CARD

        return CHIPS_PER_CARD[self.card_type]

    def __str__(self) -> str:
        return (
            f"=== {self.card_type.value.upper()} Redriver Card ===\n"
            f"{self.version}\n\n"
            f"{self.status}\n\n"
            f"EDSFF: {self.detection}\n"
            f"Dual Port: {self.dual_port}"
        )
