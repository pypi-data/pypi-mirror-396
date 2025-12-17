"""
Response parsers for the Hermes API.

This module provides parsing functions for converting CLI command responses
into structured data models.
"""

import re
from typing import Optional, Tuple

from .constants import (
    EQ_VALUES,
    FG_VALUES,
    SW_VALUES,
    CardType,
    DeviceWidth,
    LoadMode,
)
from .exceptions import ParseError
from .models import (
    BISTResult,
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
    ThermalInfo,
    VersionInfo,
)


def parse_lsd(response: str) -> CardStatus:
    """
    Parse the 'lsd' command response.

    Expected format:
        ★ ReDriver Card Information ★
        [ Thermal ]
         · SSD Temperature    : 29° C
        [ Fan Speed ]
         · Fan                : 5150  RPM
        [ Current ]
         · 12V Current        : 0.316 A
    """
    try:
        # Parse temperature
        temp_match = re.search(r"SSD Temperature\s*:\s*([\d.]+)\s*°?\s*C", response)
        if not temp_match:
            raise ParseError("Could not parse temperature from lsd response")
        temperature = float(temp_match.group(1))

        # Parse fan speed
        fan_match = re.search(r"Fan\s*:\s*(\d+)\s*RPM", response)
        if not fan_match:
            raise ParseError("Could not parse fan speed from lsd response")
        fan_speed = int(fan_match.group(1))

        # Parse current
        current_match = re.search(r"12V Current\s*:\s*([\d.]+)\s*A", response)
        if not current_match:
            raise ParseError("Could not parse current from lsd response")
        current = float(current_match.group(1))

        return CardStatus(
            thermal=ThermalInfo(temperature_celsius=temperature),
            fan=FanInfo(speed_rpm=fan_speed),
            current=CurrentInfo(current_amps=current),
        )
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse lsd response: {e}")


def parse_ver(response: str) -> VersionInfo:
    """
    Parse the 'ver' command response.

    Expected format:
        ─────────── Product Info ───────────
        Company       : Serial Cables
        Model         : GEN6 E3 HOR REDRIVER
        Serial No.    : R6PE3251201002
        ─────────── MCU Info ───────────
        Version       : 0.0.3
        Build Time    : Dec  3 2025 13:49:14
    """
    try:
        # Parse company
        company_match = re.search(r"Company\s*:\s*(.+?)(?:\n|$)", response)
        company = company_match.group(1).strip() if company_match else "Unknown"

        # Parse model
        model_match = re.search(r"Model\s*:\s*(.+?)(?:\n|$)", response)
        model = model_match.group(1).strip() if model_match else "Unknown"

        # Parse serial number
        serial_match = re.search(r"Serial No\.\s*:\s*(.+?)(?:\n|$)", response)
        serial = serial_match.group(1).strip() if serial_match else "Unknown"

        # Parse version
        version_match = re.search(r"Version\s*:\s*(.+?)(?:\n|$)", response)
        version = version_match.group(1).strip() if version_match else "Unknown"

        # Parse build time
        build_match = re.search(r"Build Time\s*:\s*(.+?)(?:\n|$)", response)
        build_time = build_match.group(1).strip() if build_match else "Unknown"

        return VersionInfo(
            product=ProductInfo(
                company=company,
                model=model,
                serial_number=serial,
            ),
            mcu=MCUInfo(
                version=version,
                build_time=build_time,
            ),
        )
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse ver response: {e}")


def parse_eq(response: str) -> EQSettings:
    """
    Parse the 'eq' command response.

    Expected format:
        Chip0 CH=0 EQ=  5.4 dB
        Chip0 CH=1 EQ=  5.4 dB
        ...
    """
    try:
        settings = EQSettings()
        chip_data: dict[int, list[ChannelEQ]] = {}

        # Pattern: Chip<num> CH=<ch> EQ= <value> dB
        pattern = r"Chip(\d+)\s+CH[=]?(\d+)\s+EQ[=]?\s*([\d.]+)\s*dB"

        for match in re.finditer(pattern, response):
            chip_num = int(match.group(1))
            channel = int(match.group(2))
            eq_db = float(match.group(3))

            # Find the step value from the dB value
            eq_step = next((k for k, v in EQ_VALUES.items() if abs(v - eq_db) < 0.1), 0)

            if chip_num not in chip_data:
                chip_data[chip_num] = []

            chip_data[chip_num].append(
                ChannelEQ(
                    channel=channel,
                    eq_step=eq_step,
                    eq_db=eq_db,
                )
            )

        # Build structured response
        for chip_num in sorted(chip_data.keys()):
            settings.chips.append(
                ChipEQ(
                    chip=chip_num,
                    channels=sorted(chip_data[chip_num], key=lambda x: x.channel),
                )
            )

        return settings
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse eq response: {e}")


def parse_fg(response: str) -> FGSettings:
    """
    Parse the 'fg' command response.

    Expected format:
        Chip0 CH=0 FG=  0.2 dB
        Chip0 CH=1 FG=  0.2 dB
        ...
    """
    try:
        settings = FGSettings()
        chip_data: dict[int, list[ChannelFG]] = {}

        # Pattern: Chip<num> CH=<ch> FG= <value> dB
        pattern = r"Chip(\d+)\s+CH[=]?(\d+)\s+FG[=]?\s*([-\d.]+)\s*dB"

        for match in re.finditer(pattern, response):
            chip_num = int(match.group(1))
            channel = int(match.group(2))
            fg_db = float(match.group(3))

            # Find the step value from the dB value
            fg_step = next(
                (k for k, v in FG_VALUES.items() if abs(v - fg_db) < 0.1),
                3,  # Default to step 3 (-0.2 dB)
            )

            if chip_num not in chip_data:
                chip_data[chip_num] = []

            chip_data[chip_num].append(
                ChannelFG(
                    channel=channel,
                    fg_step=fg_step,
                    fg_db=fg_db,
                )
            )

        for chip_num in sorted(chip_data.keys()):
            settings.chips.append(
                ChipFG(
                    chip=chip_num,
                    channels=sorted(chip_data[chip_num], key=lambda x: x.channel),
                )
            )

        return settings
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse fg response: {e}")


def parse_sw(response: str) -> SWSettings:
    """
    Parse the 'sw' command response.

    Expected format:
        Chip0 CH=0 SW= 1630 mv
        Chip0 CH=1 SW= 1630 mv
        ...
    """
    try:
        settings = SWSettings()
        chip_data: dict[int, list[ChannelSW]] = {}

        # Pattern: Chip<num> CH=<ch> SW= <value> mv
        pattern = r"Chip(\d+)\s+CH[=]?(\d+)\s+SW[=]?\s*(\d+)\s*mv"

        for match in re.finditer(pattern, response):
            chip_num = int(match.group(1))
            channel = int(match.group(2))
            swing_mv = int(match.group(3))

            # Find the step value from the mV value
            sw_step = next(
                (k for k, v in SW_VALUES.items() if v == swing_mv), 7  # Default to step 7 (1630 mV)
            )

            if chip_num not in chip_data:
                chip_data[chip_num] = []

            chip_data[chip_num].append(
                ChannelSW(
                    channel=channel,
                    sw_step=sw_step,
                    swing_mv=swing_mv,
                )
            )

        for chip_num in sorted(chip_data.keys()):
            settings.chips.append(
                ChipSW(
                    chip=chip_num,
                    channels=sorted(chip_data[chip_num], key=lambda x: x.channel),
                )
            )

        return settings
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse sw response: {e}")


def parse_tune_result(response: str) -> ChannelTuning:
    """
    Parse the 'tune' command result.

    Expected format:
        Chip0, CH:0, EQ:  2.3 dB, FG: -2.8 dB, SW: 1050 mv
    """
    try:
        pattern = (
            r"Chip(\d+),\s*CH[:]?(\d+),\s*"
            r"EQ[:]?\s*([\d.]+)\s*dB,\s*"
            r"FG[:]?\s*([-\d.]+)\s*dB,\s*"
            r"SW[:]?\s*(\d+)\s*mv"
        )

        match = re.search(pattern, response)
        if not match:
            raise ParseError("Could not parse tune result")

        chip = int(match.group(1))
        channel = int(match.group(2))
        eq_db = float(match.group(3))
        fg_db = float(match.group(4))
        swing_mv = int(match.group(5))

        # Find step values
        eq_step = next((k for k, v in EQ_VALUES.items() if abs(v - eq_db) < 0.1), 0)
        fg_step = next((k for k, v in FG_VALUES.items() if abs(v - fg_db) < 0.1), 3)
        sw_step = next((k for k, v in SW_VALUES.items() if v == swing_mv), 7)

        return ChannelTuning(
            chip=chip,
            channel=channel,
            eq_step=eq_step,
            eq_db=eq_db,
            fg_step=fg_step,
            fg_db=fg_db,
            sw_step=sw_step,
            swing_mv=swing_mv,
        )
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse tune result: {e}")


def parse_load(response: str) -> LoadConfiguration:
    """
    Parse the 'load' command response.

    Expected format:
        Currently loaded 'Medium' configuration.
    or:
        Successfully loaded 'Medium' configuration.
    """
    try:
        pattern = r"(?:Currently|Successfully)\s+loaded\s+'(\w+)'\s+configuration"
        match = re.search(pattern, response)

        if match:
            mode_str = match.group(1).lower()
            mode_map = {
                "short": LoadMode.SHORT,
                "medium": LoadMode.MEDIUM,
                "long": LoadMode.LONG,
            }
            mode = mode_map.get(mode_str, LoadMode.MEDIUM)

            desc_map = {
                LoadMode.SHORT: 'Less than 9" trace length',
                LoadMode.MEDIUM: '6-9" trace length (factory default)',
                LoadMode.LONG: '10-12" trace length',
            }

            return LoadConfiguration(mode=mode, description=desc_map[mode])

        raise ParseError("Could not parse load configuration")
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse load response: {e}")


def parse_save(response: str) -> SaveResult:
    """Parse the 'save' command response."""
    success = "success" in response.lower() or "save configuration success" in response.lower()
    return SaveResult(success=success)


def parse_perst(response: str) -> PERSTResult:
    """
    Parse the 'perst' command response.

    Expected format:
        Reset E3 success
    or:
        Reset channel a of E3 success
    """
    try:
        success = "success" in response.lower()

        channel_match = re.search(r"channel\s+([ab])", response.lower())
        channel = channel_match.group(1).upper() if channel_match else "BOTH"

        return PERSTResult(channel=channel, success=success)
    except Exception as e:
        raise ParseError(f"Failed to parse perst response: {e}")


def parse_dual(response: str) -> DualPortStatus:
    """
    Parse the 'dual' command response.

    Expected format:
        E3 dual port: off
    or:
        Set EDSFF dual port: on success.
    """
    try:
        if "on" in response.lower():
            return DualPortStatus(enabled=True)
        elif "off" in response.lower():
            return DualPortStatus(enabled=False)
        else:
            raise ParseError("Could not determine dual port status")
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse dual response: {e}")


def parse_detect(response: str) -> EDSFFDetection:
    """
    Parse the 'detect' command response.

    Expected format:
        E3 present detection: X4
    or:
        E3 present detection: X8
    """
    try:
        pattern = r"present detection[:]?\s*(X\d+|None)"
        match = re.search(pattern, response, re.IGNORECASE)

        if match:
            width_str = match.group(1).upper()
            width_map = {
                "X4": DeviceWidth.X4,
                "X8": DeviceWidth.X8,
                "X16": DeviceWidth.X16,
                "NONE": DeviceWidth.NONE,
            }
            width = width_map.get(width_str, DeviceWidth.NONE)
            present = width != DeviceWidth.NONE
            return EDSFFDetection(width=width, present=present)

        return EDSFFDetection(width=DeviceWidth.NONE, present=False)
    except Exception as e:
        raise ParseError(f"Failed to parse detect response: {e}")


def parse_bist(response: str) -> BISTResult:
    """
    Parse the 'bist' command response.

    Expected format:
        Channel  Device     Address  Status
        ----------------------------------------
        CH0      PS7161-1   0x3A     OK
        CH0      PS7161-2   0x5A     OK
        ...
    """
    try:
        result = BISTResult()

        # Pattern: CH<n>  <device>  0x<addr>  <status>
        pattern = r"CH(\d+)\s+(\S+)\s+0x([0-9A-Fa-f]+)\s+(\w+)"

        for match in re.finditer(pattern, response):
            channel = int(match.group(1))
            device_name = match.group(2)
            address = int(match.group(3), 16)
            status = match.group(4)

            result.devices.append(
                I2CDevice(
                    channel=channel,
                    device_name=device_name,
                    address=address,
                    status=status,
                )
            )

        return result
    except Exception as e:
        raise ParseError(f"Failed to parse bist response: {e}")


def parse_iicwr(response: str) -> I2CReadResult:
    """
    Parse the 'iicwr' command response.

    Expected format:
        Data [0] = 6
        Data [1] = bb
        ...
    """
    try:
        data = []

        # Extract address from command echo if present
        addr_match = re.search(r"iicwr\s+([0-9a-fA-F]+)", response)
        address = int(addr_match.group(1), 16) if addr_match else 0

        # Pattern: Data [n] = <hex>
        pattern = r"Data\s*\[(\d+)\]\s*=\s*([0-9a-fA-F]+)"

        matches = list(re.finditer(pattern, response))
        if matches:
            # Sort by index and extract values
            for match in sorted(matches, key=lambda m: int(m.group(1))):
                data.append(int(match.group(2), 16))

        return I2CReadResult(address=address, data=data)
    except Exception as e:
        raise ParseError(f"Failed to parse iicwr response: {e}")


def parse_iicw(response: str) -> I2CWriteResult:
    """
    Parse the 'iicw' command response.

    Expected format:
        Write Data [0] = ff
    """
    try:
        # Count successful writes
        pattern = r"Write Data\s*\[\d+\]\s*=\s*[0-9a-fA-F]+"
        matches = list(re.finditer(pattern, response))
        bytes_written = len(matches)

        # Extract address
        addr_match = re.search(r"iicw\s+([0-9a-fA-F]+)", response)
        address = int(addr_match.group(1), 16) if addr_match else 0

        success = bytes_written > 0

        return I2CWriteResult(
            address=address,
            bytes_written=bytes_written,
            success=success,
        )
    except Exception as e:
        raise ParseError(f"Failed to parse iicw response: {e}")


def parse_reset(response: str) -> ResetResult:
    """Parse the 'reset' command response."""
    # Reset typically doesn't have much response, just check for errors
    success = "error" not in response.lower() and "fail" not in response.lower()
    return ResetResult(success=success)


def parse_hled(response: str) -> bool:
    """
    Parse the 'hled' command response.

    Returns True if command succeeded.
    """
    return "success" in response.lower()


def parse_pwrdis(response: str) -> bool:
    """
    Parse the 'pwrdis' command response.

    Returns True if command succeeded.
    """
    return "success" in response.lower()


def parse_eq_set(response: str) -> Tuple[Optional[int], float]:
    """
    Parse response from setting EQ value.

    Expected format:
        Set all chip EQ:  3.2 dB
    or:
        Set chip 1 EQ:  3.2 dB
    """
    try:
        pattern = r"Set\s+(?:all\s+chip|chip\s+(\d+))\s+EQ[:]?\s*([\d.]+)\s*dB"
        match = re.search(pattern, response)

        if match:
            chip = int(match.group(1)) if match.group(1) else None
            eq_db = float(match.group(2))
            return (chip, eq_db)

        raise ParseError("Could not parse EQ set response")
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse eq set response: {e}")


def parse_fg_set(response: str) -> Tuple[Optional[int], float]:
    """
    Parse response from setting FG value.

    Expected format:
        Set all chip FG: -2.0 dB
    or:
        Set chip 1 FG: -2.0 dB
    """
    try:
        pattern = r"Set\s+(?:all\s+chip|chip\s+(\d+))\s+FG[:]?\s*([-\d.]+)\s*dB"
        match = re.search(pattern, response)

        if match:
            chip = int(match.group(1)) if match.group(1) else None
            fg_db = float(match.group(2))
            return (chip, fg_db)

        raise ParseError("Could not parse FG set response")
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse fg set response: {e}")


def parse_sw_set(response: str) -> Tuple[Optional[int], int]:
    """
    Parse response from setting SW value.

    Expected format:
        Set all chip SW: 1150 mv
    or:
        Set chip 1 SW: 1150 mv
    """
    try:
        pattern = r"Set\s+(?:all\s+chip|chip\s+(\d+))\s+SW[:]?\s*(\d+)\s*mv"
        match = re.search(pattern, response)

        if match:
            chip = int(match.group(1)) if match.group(1) else None
            swing_mv = int(match.group(2))
            return (chip, swing_mv)

        raise ParseError("Could not parse SW set response")
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse sw set response: {e}")


def detect_card_type(bist_result: BISTResult) -> CardType:
    """
    Detect card type based on BIST results.

    X16 cards have 8 PS7161 chips, X8 cards have 4.
    """
    ps7161_count = sum(1 for dev in bist_result.devices if "PS7161" in dev.device_name)

    if ps7161_count >= 8:
        return CardType.X16
    else:
        return CardType.X8
