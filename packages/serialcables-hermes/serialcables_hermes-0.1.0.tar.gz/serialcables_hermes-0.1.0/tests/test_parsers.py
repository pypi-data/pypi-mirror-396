"""Tests for response parsers."""

import pytest

from serialcables_hermes.constants import CardType, DeviceWidth, LoadMode
from serialcables_hermes.parsers import (
    detect_card_type,
    parse_bist,
    parse_detect,
    parse_dual,
    parse_eq,
    parse_fg,
    parse_load,
    parse_lsd,
    parse_perst,
    parse_save,
    parse_sw,
    parse_ver,
)


class TestParseLsd:
    """Tests for parse_lsd."""

    def test_parse_lsd_valid(self):
        response = """★ ReDriver Card Information ★
        [ Thermal ]
         · SSD Temperature    : 29° C
        [ Fan Speed ]
         · Fan                : 5150  RPM
        [ Current ]
         · 12V Current        : 0.316 A"""

        result = parse_lsd(response)
        assert result.thermal.temperature_celsius == 29.0
        assert result.fan.speed_rpm == 5150
        assert result.current.current_amps == 0.316


class TestParseVer:
    """Tests for parse_ver."""

    def test_parse_ver_valid(self):
        response = """─────────── Product Info ───────────
        Company       : Serial Cables
        Model         : GEN6 E3 HOR REDRIVER
        Serial No.    : R6PE3251201002
        ─────────── MCU Info ───────────
        Version       : 0.0.3
        Build Time    : Dec  3 2025 13:49:14"""

        result = parse_ver(response)
        assert result.product.company == "Serial Cables"
        assert result.product.model == "GEN6 E3 HOR REDRIVER"
        assert result.product.serial_number == "R6PE3251201002"
        assert result.mcu.version == "0.0.3"
        assert result.mcu.build_time == "Dec  3 2025 13:49:14"


class TestParseEq:
    """Tests for parse_eq."""

    def test_parse_eq_valid(self):
        response = """Chip0 CH=0 EQ=  5.4 dB
        Chip0 CH=1 EQ=  5.4 dB
        Chip0 CH=2 EQ=  5.4 dB
        Chip0 CH=3 EQ=  5.4 dB
        Chip1 CH=0 EQ=  5.4 dB
        Chip1 CH=1 EQ=  5.4 dB
        Chip1 CH=2 EQ=  5.4 dB
        Chip1 CH=3 EQ=  5.4 dB"""

        result = parse_eq(response)
        assert len(result.chips) == 2
        assert result.chips[0].chip == 0
        assert len(result.chips[0].channels) == 4
        assert result.chips[0].channels[0].eq_db == 5.4

    def test_parse_eq_empty(self):
        result = parse_eq("")
        assert len(result.chips) == 0


class TestParseFg:
    """Tests for parse_fg."""

    def test_parse_fg_valid(self):
        response = """Chip0 CH=0 FG= -0.2 dB
        Chip0 CH=1 FG= -0.2 dB
        Chip0 CH=2 FG= -0.2 dB
        Chip0 CH=3 FG= -0.2 dB"""

        result = parse_fg(response)
        assert len(result.chips) == 1
        assert result.chips[0].channels[0].fg_db == -0.2


class TestParseSw:
    """Tests for parse_sw."""

    def test_parse_sw_valid(self):
        response = """Chip0 CH=0 SW= 1630 mv
        Chip0 CH=1 SW= 1630 mv
        Chip0 CH=2 SW= 1630 mv
        Chip0 CH=3 SW= 1630 mv"""

        result = parse_sw(response)
        assert len(result.chips) == 1
        assert result.chips[0].channels[0].swing_mv == 1630


class TestParseLoad:
    """Tests for parse_load."""

    def test_parse_load_medium(self):
        response = "Currently loaded 'Medium' configuration."
        result = parse_load(response)
        assert result.mode == LoadMode.MEDIUM

    def test_parse_load_short(self):
        response = "Successfully loaded 'Short' configuration."
        result = parse_load(response)
        assert result.mode == LoadMode.SHORT

    def test_parse_load_long(self):
        response = "Currently loaded 'Long' configuration."
        result = parse_load(response)
        assert result.mode == LoadMode.LONG


class TestParseSave:
    """Tests for parse_save."""

    def test_parse_save_success(self):
        response = "Save configuration success"
        result = parse_save(response)
        assert result.success is True

    def test_parse_save_failed(self):
        response = "Error"
        result = parse_save(response)
        assert result.success is False


class TestParsePerst:
    """Tests for parse_perst."""

    def test_parse_perst_both(self):
        response = "Reset E3 success"
        result = parse_perst(response)
        assert result.success is True
        assert result.channel == "BOTH"

    def test_parse_perst_channel_a(self):
        response = "Reset channel a of E3 success"
        result = parse_perst(response)
        assert result.success is True
        assert result.channel == "A"


class TestParseDual:
    """Tests for parse_dual."""

    def test_parse_dual_on(self):
        response = "E3 dual port: on"
        result = parse_dual(response)
        assert result.enabled is True

    def test_parse_dual_off(self):
        response = "E3 dual port: off"
        result = parse_dual(response)
        assert result.enabled is False


class TestParseDetect:
    """Tests for parse_detect."""

    def test_parse_detect_x8(self):
        response = "E3 present detection: X8"
        result = parse_detect(response)
        assert result.width == DeviceWidth.X8
        assert result.present is True

    def test_parse_detect_none(self):
        response = "E3 present detection: None"
        result = parse_detect(response)
        assert result.width == DeviceWidth.NONE
        assert result.present is False


class TestParseBist:
    """Tests for parse_bist."""

    def test_parse_bist_valid(self):
        response = """Channel  Device     Address  Status
        ----------------------------------------
        CH0      PS7161-1   0x3A     OK
        CH0      PS7161-2   0x5A     OK
        CH1      PCA9575    0x42     OK
        CH1      AT24C64    0xA0     OK"""

        result = parse_bist(response)
        assert len(result.devices) == 4
        assert result.devices[0].device_name == "PS7161-1"
        assert result.devices[0].address == 0x3A
        assert result.devices[0].status == "OK"


class TestDetectCardType:
    """Tests for detect_card_type."""

    def test_detect_x8(self):
        from serialcables_hermes.models import BISTResult, I2CDevice

        bist = BISTResult(
            devices=[
                I2CDevice(channel=0, device_name="PS7161-1", address=0x3A, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-2", address=0x5A, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-5", address=0x8E, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-6", address=0x6E, status="OK"),
            ]
        )
        assert detect_card_type(bist) == CardType.X8

    def test_detect_x16(self):
        from serialcables_hermes.models import BISTResult, I2CDevice

        bist = BISTResult(
            devices=[
                I2CDevice(channel=0, device_name="PS7161-1", address=0x3A, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-2", address=0x5A, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-3", address=0x62, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-4", address=0x64, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-5", address=0x8E, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-6", address=0x6E, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-7", address=0x66, status="OK"),
                I2CDevice(channel=0, device_name="PS7161-8", address=0x60, status="OK"),
            ]
        )
        assert detect_card_type(bist) == CardType.X16
