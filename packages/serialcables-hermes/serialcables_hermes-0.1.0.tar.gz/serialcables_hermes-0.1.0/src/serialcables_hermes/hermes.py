"""
Hermes - PCIe Gen6 EDSFF Redriver Card API.

This module provides the main Hermes class for communicating with
Serial Cables PCIe Gen6 EDSFF Redriver cards via USB serial interface.
"""

import logging
import time
from typing import List, Optional, Union

import serial
import serial.tools.list_ports

from .constants import (
    CHIPS_PER_CARD,
    COMMAND_PROMPT,
    COMMAND_TIMEOUT,
    DEFAULT_BAUDRATE,
    DEFAULT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    EQ_VALUES,
    FG_VALUES,
    SW_VALUES,
    CardType,
    Channel,
    DualPortState,
    LEDState,
    LoadMode,
    PowerDisableLevel,
)
from .exceptions import (
    ConnectionError,
    InvalidChipError,
    InvalidValueError,
    TimeoutError,
    ValidationError,
)
from .models import (
    BISTResult,
    CardInfo,
    CardStatus,
    DualPortStatus,
    EDSFFDetection,
    EQSettings,
    FGSettings,
    I2CReadResult,
    I2CWriteResult,
    LoadConfiguration,
    PERSTResult,
    ResetResult,
    SaveResult,
    SWSettings,
    SystemInfo,
    VersionInfo,
)
from .parsers import (
    detect_card_type,
    parse_bist,
    parse_detect,
    parse_dual,
    parse_eq,
    parse_fg,
    parse_hled,
    parse_iicw,
    parse_iicwr,
    parse_load,
    parse_lsd,
    parse_perst,
    parse_pwrdis,
    parse_save,
    parse_sw,
    parse_ver,
)

logger = logging.getLogger(__name__)


class Hermes:
    """
    API for communicating with Serial Cables PCIe Gen6 EDSFF Redriver cards.

    The Hermes class provides methods for querying device information, tuning
    redriver parameters, and controlling EDSFF sideband signals via the on-board
    MCU CLI interface.

    Example:
        >>> with Hermes('/dev/ttyUSB0') as hermes:
        ...     info = hermes.get_version()
        ...     print(info)
        ...     status = hermes.get_status()
        ...     print(f"Temperature: {status.thermal}")
    """

    def __init__(
        self,
        port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        write_timeout: float = DEFAULT_WRITE_TIMEOUT,
    ):
        """
        Initialize connection to a Redriver card.

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Baud rate for serial communication (default: 115200)
            timeout: Read timeout in seconds (default: 2.0)
            write_timeout: Write timeout in seconds (default: 1.0)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self._serial: Optional[serial.Serial] = None
        self._card_type: Optional[CardType] = None

    def __enter__(self) -> "Hermes":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()

    @classmethod
    def list_devices(cls) -> List[str]:
        """
        List available serial ports that may be Redriver cards.

        Returns:
            List of serial port paths.
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            # Include USB serial devices
            if port.vid is not None:
                ports.append(port.device)
        return sorted(ports)

    @classmethod
    def find_device(cls) -> Optional[str]:
        """
        Find the first available Redriver card.

        Returns:
            Serial port path or None if not found.
        """
        devices = cls.list_devices()
        return devices[0] if devices else None

    @property
    def is_connected(self) -> bool:
        """Check if connected to the device."""
        return self._serial is not None and self._serial.is_open

    @property
    def card_type(self) -> Optional[CardType]:
        """Get the detected card type (X8 or X16)."""
        return self._card_type

    @property
    def num_chips(self) -> int:
        """Get the number of redriver chips based on card type."""
        if self._card_type is None:
            return 0
        return CHIPS_PER_CARD[self._card_type]

    def connect(self) -> None:
        """
        Open connection to the Redriver card.

        Raises:
            ConnectionError: If connection fails.
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
            )

            # Clear any pending data
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

            # Wait for device to be ready
            time.sleep(0.1)

            # Send empty command to sync
            self._send_command("")

            # Detect card type
            try:
                bist = self.run_bist()
                self._card_type = detect_card_type(bist)
                logger.info(f"Connected to {self._card_type.value} Redriver card on {self.port}")
            except Exception:
                # Default to X8 if detection fails
                self._card_type = CardType.X8
                logger.warning("Could not detect card type, defaulting to X8")

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def disconnect(self) -> None:
        """Close connection to the Redriver card."""
        if self._serial is not None:
            self._serial.close()
            self._serial = None
            self._card_type = None
            logger.info(f"Disconnected from {self.port}")

    def _send_command(
        self,
        command: str,
        timeout: float = COMMAND_TIMEOUT,
    ) -> str:
        """
        Send a command and wait for response until prompt.

        Args:
            command: CLI command to send
            timeout: Timeout in seconds

        Returns:
            Response string (excluding prompt)

        Raises:
            ConnectionError: If not connected
            TimeoutError: If command times out
            CommandError: If command fails
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")

        assert self._serial is not None  # Type narrowing for mypy

        # Clear input buffer
        self._serial.reset_input_buffer()

        # Send command with newline
        cmd_bytes = f"{command}\r\n".encode("utf-8")
        self._serial.write(cmd_bytes)
        self._serial.flush()

        logger.debug(f"Sent: {command}")

        # Read response until we see the prompt
        response = ""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Command '{command}' timed out after {timeout}s")

            if self._serial.in_waiting > 0:
                chunk = self._serial.read(self._serial.in_waiting)
                response += chunk.decode("utf-8", errors="replace")

                # Check for prompt indicating command completion
                if COMMAND_PROMPT in response:
                    break
            else:
                time.sleep(0.01)

        logger.debug(f"Received: {response[:100]}...")

        # Remove the command echo and prompt from response
        lines = response.split("\n")
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(command[:10]) and COMMAND_PROMPT not in line:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _validate_chip(self, chip: Union[int, str]) -> None:
        """Validate chip number for the current card type."""
        if isinstance(chip, str):
            if chip.lower() != "all":
                raise ValidationError(f"Invalid chip specifier: {chip}")
            return

        if not isinstance(chip, int):
            raise ValidationError(f"Chip must be int or 'all', got {type(chip)}")

        max_chips = self.num_chips if self._card_type else 8
        if chip < 0 or chip >= max_chips:
            raise InvalidChipError(chip, max_chips)

    def _validate_eq_value(self, value: int) -> None:
        """Validate EQ step value (0-15)."""
        if not isinstance(value, int) or value < 0 or value > 15:
            raise InvalidValueError("EQ", value, "0-15")

    def _validate_fg_value(self, value: int) -> None:
        """Validate flat gain step value (0-3)."""
        if not isinstance(value, int) or value < 0 or value > 3:
            raise InvalidValueError("FG", value, "0-3")

    def _validate_sw_value(self, value: int) -> None:
        """Validate swing step value (0-7)."""
        if not isinstance(value, int) or value < 0 or value > 7:
            raise InvalidValueError("SW", value, "0-7")

    # =========================================================================
    # Information Commands
    # =========================================================================

    def get_version(self) -> VersionInfo:
        """
        Get product and firmware version information.

        Returns:
            VersionInfo containing product and MCU information.
        """
        response = self._send_command("ver")
        return parse_ver(response)

    def get_status(self) -> CardStatus:
        """
        Get current card status (temperature, fan, current).

        Returns:
            CardStatus with thermal, fan, and current readings.
        """
        response = self._send_command("lsd")
        return parse_lsd(response)

    def get_system_info(self) -> SystemInfo:
        """
        Get complete system information.

        Returns:
            SystemInfo containing version, status, and BIST results.
        """
        response = self._send_command("sysinfo")

        # Parse individual sections
        version = parse_ver(response)
        status = parse_lsd(response)
        bist = parse_bist(response)

        return SystemInfo(version=version, status=status, bist=bist)

    def run_bist(self) -> BISTResult:
        """
        Run Built-In Self Test.

        Returns:
            BISTResult with status of all I2C devices.
        """
        response = self._send_command("bist")
        return parse_bist(response)

    def detect_edsff(self) -> EDSFFDetection:
        """
        Detect attached EDSFF device.

        Returns:
            EDSFFDetection with device width and presence.
        """
        response = self._send_command("detect")
        return parse_detect(response)

    def get_card_info(self) -> CardInfo:
        """
        Get comprehensive card information.

        Returns:
            CardInfo combining version, status, detection, and dual port info.
        """
        version = self.get_version()
        status = self.get_status()
        detection = self.detect_edsff()
        dual_port = self.get_dual_port_status()

        return CardInfo(
            card_type=self._card_type or CardType.X8,
            version=version,
            status=status,
            detection=detection,
            dual_port=dual_port,
        )

    # =========================================================================
    # EQ (Equalization) Commands
    # =========================================================================

    def get_eq_settings(self) -> EQSettings:
        """
        Get current EQ settings for all chips.

        Returns:
            EQSettings with per-chip, per-channel EQ values.
        """
        response = self._send_command("eq")
        return parse_eq(response)

    def set_eq(self, chip: Union[int, str], value: int) -> EQSettings:
        """
        Set EQ value for a chip or all chips.

        Args:
            chip: Chip number (0-7 for X16, 0-3 for X8) or 'all'
            value: EQ step value (0-15, corresponding to 2.3-20.8 dB)

        Returns:
            Updated EQSettings.
        """
        self._validate_chip(chip)
        self._validate_eq_value(value)

        chip_str = "all" if isinstance(chip, str) else str(chip)
        self._send_command(f"eq {chip_str} {value}")

        # Return current settings
        return self.get_eq_settings()

    def get_eq_help(self) -> dict:
        """
        Get EQ value reference table.

        Returns:
            Dictionary mapping step values to dB values.
        """
        return EQ_VALUES.copy()

    # =========================================================================
    # FG (Flat Gain) Commands
    # =========================================================================

    def get_fg_settings(self) -> FGSettings:
        """
        Get current flat gain settings for all chips.

        Returns:
            FGSettings with per-chip, per-channel FG values.
        """
        response = self._send_command("fg")
        return parse_fg(response)

    def set_fg(self, chip: Union[int, str], value: int) -> FGSettings:
        """
        Set flat gain value for a chip or all chips.

        Args:
            chip: Chip number (0-7 for X16, 0-3 for X8) or 'all'
            value: FG step value (0-3, corresponding to -2.8 to -0.2 dB)

        Returns:
            Updated FGSettings.
        """
        self._validate_chip(chip)
        self._validate_fg_value(value)

        chip_str = "all" if isinstance(chip, str) else str(chip)
        self._send_command(f"fg {chip_str} {value}")

        return self.get_fg_settings()

    def get_fg_help(self) -> dict:
        """
        Get flat gain value reference table.

        Returns:
            Dictionary mapping step values to dB values.
        """
        return FG_VALUES.copy()

    # =========================================================================
    # SW (Swing) Commands
    # =========================================================================

    def get_sw_settings(self) -> SWSettings:
        """
        Get current transmitter swing settings for all chips.

        Returns:
            SWSettings with per-chip, per-channel swing values.
        """
        response = self._send_command("sw")
        return parse_sw(response)

    def set_sw(self, chip: Union[int, str], value: int) -> SWSettings:
        """
        Set transmitter swing value for a chip or all chips.

        Args:
            chip: Chip number (0-7 for X16, 0-3 for X8) or 'all'
            value: SW step value (0-7, corresponding to 1050-1630 mV)

        Returns:
            Updated SWSettings.
        """
        self._validate_chip(chip)
        self._validate_sw_value(value)

        chip_str = "all" if isinstance(chip, str) else str(chip)
        self._send_command(f"sw {chip_str} {value}")

        return self.get_sw_settings()

    def get_sw_help(self) -> dict:
        """
        Get swing value reference table.

        Returns:
            Dictionary mapping step values to mV values.
        """
        return SW_VALUES.copy()

    # =========================================================================
    # Configuration Commands
    # =========================================================================

    def load_configuration(self, mode: LoadMode) -> LoadConfiguration:
        """
        Load a preset configuration based on trace length.

        Args:
            mode: LoadMode.SHORT (<9"), MEDIUM (6-9"), or LONG (10-12")

        Returns:
            LoadConfiguration confirming the loaded mode.
        """
        response = self._send_command(f"load {mode.value}")
        return parse_load(response)

    def get_current_configuration(self) -> LoadConfiguration:
        """
        Get the currently loaded configuration mode.

        Returns:
            LoadConfiguration with current mode.
        """
        response = self._send_command("load")
        return parse_load(response)

    def save_configuration(self) -> SaveResult:
        """
        Save current EQ, FG, and SW settings to flash.

        Settings will be automatically applied on next boot.

        Returns:
            SaveResult indicating success.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")
        assert self._serial is not None  # Type narrowing for mypy

        # Send save command and confirm
        self._serial.write(b"save\r\n")
        self._serial.flush()
        time.sleep(0.2)

        # Send confirmation
        self._serial.write(b"y\r\n")
        self._serial.flush()

        # Read response
        response = ""
        start_time = time.time()
        while time.time() - start_time < COMMAND_TIMEOUT:
            if self._serial.in_waiting > 0:
                chunk = self._serial.read(self._serial.in_waiting)
                response += chunk.decode("utf-8", errors="replace")
                if COMMAND_PROMPT in response:
                    break
            time.sleep(0.01)

        return parse_save(response)

    # =========================================================================
    # EDSFF Control Commands
    # =========================================================================

    def send_perst(self, channel: Optional[Channel] = None) -> PERSTResult:
        """
        Send PERST# signal with 30ms duration.

        Args:
            channel: Channel.A, Channel.B, or None for both channels.

        Returns:
            PERSTResult indicating success.
        """
        if channel is None or channel == Channel.BOTH:
            response = self._send_command("perst")
        else:
            response = self._send_command(f"perst {channel.value}")

        return parse_perst(response)

    def get_dual_port_status(self) -> DualPortStatus:
        """
        Get current dual port enable status.

        Returns:
            DualPortStatus with enabled state.
        """
        response = self._send_command("dual")
        return parse_dual(response)

    def set_dual_port(self, state: DualPortState) -> DualPortStatus:
        """
        Set dual port enable state.

        Args:
            state: DualPortState.ON or DualPortState.OFF

        Returns:
            Updated DualPortStatus.
        """
        response = self._send_command(f"dual {state.value}")
        return parse_dual(response)

    def set_power_disable(self, level: PowerDisableLevel) -> bool:
        """
        Set PWRDIS signal level.

        Args:
            level: PowerDisableLevel.HIGH (disable power) or LOW (enable power)

        Returns:
            True if successful.
        """
        response = self._send_command(f"pwrdis {level.value}")
        return parse_pwrdis(response)

    def set_host_led(self, state: LEDState) -> bool:
        """
        Control EDSFF host LED (amber).

        Args:
            state: LEDState.ON or LEDState.OFF

        Returns:
            True if successful.
        """
        response = self._send_command(f"hled {state.value}")
        return parse_hled(response)

    # =========================================================================
    # I2C/SMBus Commands
    # =========================================================================

    def i2c_read(
        self,
        address: int,
        read_bytes: int,
        register: int = 0,
    ) -> I2CReadResult:
        """
        Read data from an I2C device attached to EDSFF connector.

        Args:
            address: I2C device address (7-bit)
            read_bytes: Number of bytes to read (max 128)
            register: Starting register address

        Returns:
            I2CReadResult with read data.
        """
        if read_bytes < 1 or read_bytes > 128:
            raise ValidationError("read_bytes must be 1-128")

        cmd = f"iicwr {address:x} {read_bytes} {register:x}"
        response = self._send_command(cmd)

        result = parse_iicwr(response)
        result.address = address
        return result

    def i2c_write(
        self,
        address: int,
        data: Union[bytes, List[int]],
    ) -> I2CWriteResult:
        """
        Write data to an I2C device attached to EDSFF connector.

        Args:
            address: I2C device address (7-bit)
            data: Bytes to write (max 128)

        Returns:
            I2CWriteResult with write status.
        """
        if isinstance(data, bytes):
            data = list(data)

        if len(data) < 1 or len(data) > 128:
            raise ValidationError("data must be 1-128 bytes")

        hex_data = " ".join(f"{b:02x}" for b in data)
        cmd = f"iicw {address:x} {hex_data}"
        response = self._send_command(cmd)

        result = parse_iicw(response)
        result.address = address
        return result

    # =========================================================================
    # System Commands
    # =========================================================================

    def reset_mcu(self) -> ResetResult:
        """
        Reset the on-board MCU.

        Note: Connection may need to be re-established after reset.

        Returns:
            ResetResult indicating success.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")
        assert self._serial is not None  # Type narrowing for mypy

        try:
            self._serial.write(b"reset\r\n")
            self._serial.flush()
            time.sleep(0.5)

            # Wait for device to come back
            time.sleep(2.0)

            # Try to reconnect
            self._serial.reset_input_buffer()
            self._send_command("")

            return ResetResult(success=True)
        except Exception as e:
            logger.warning(f"Reset may have succeeded but reconnection failed: {e}")
            return ResetResult(success=True)

    def send_raw_command(self, command: str, timeout: float = COMMAND_TIMEOUT) -> str:
        """
        Send a raw CLI command and return the response.

        Useful for advanced users or unsupported commands.

        Args:
            command: Raw command string
            timeout: Response timeout in seconds

        Returns:
            Raw response string.
        """
        return self._send_command(command, timeout=timeout)
