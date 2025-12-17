"""Tests for constants module."""

import pytest

from serialcables_hermes.constants import (
    CHANNELS_PER_CHIP,
    CHIPS_PER_CARD,
    COMMAND_PROMPT,
    DEFAULT_BAUDRATE,
    EQ_VALUES,
    FG_VALUES,
    SW_VALUES,
    CardType,
    Channel,
    DeviceWidth,
    DualPortState,
    LEDState,
    LoadMode,
    PowerDisableLevel,
)


class TestCardType:
    """Tests for CardType enum."""

    def test_values(self):
        assert CardType.X8.value == "x8"
        assert CardType.X16.value == "x16"


class TestLoadMode:
    """Tests for LoadMode enum."""

    def test_values(self):
        assert LoadMode.SHORT.value == "s"
        assert LoadMode.MEDIUM.value == "m"
        assert LoadMode.LONG.value == "l"


class TestChannel:
    """Tests for Channel enum."""

    def test_values(self):
        assert Channel.A.value == "a"
        assert Channel.B.value == "b"
        assert Channel.BOTH.value == ""


class TestDualPortState:
    """Tests for DualPortState enum."""

    def test_values(self):
        assert DualPortState.ON.value == "on"
        assert DualPortState.OFF.value == "off"


class TestPowerDisableLevel:
    """Tests for PowerDisableLevel enum."""

    def test_values(self):
        assert PowerDisableLevel.HIGH.value == "h"
        assert PowerDisableLevel.LOW.value == "l"


class TestLEDState:
    """Tests for LEDState enum."""

    def test_values(self):
        assert LEDState.ON.value == "on"
        assert LEDState.OFF.value == "off"


class TestDeviceWidth:
    """Tests for DeviceWidth enum."""

    def test_values(self):
        assert DeviceWidth.X4.value == "X4"
        assert DeviceWidth.X8.value == "X8"
        assert DeviceWidth.X16.value == "X16"
        assert DeviceWidth.NONE.value == "None"


class TestEQValues:
    """Tests for EQ_VALUES lookup table."""

    def test_range(self):
        assert len(EQ_VALUES) == 16
        assert 0 in EQ_VALUES
        assert 15 in EQ_VALUES

    def test_values(self):
        assert EQ_VALUES[0] == 2.3
        assert EQ_VALUES[15] == 20.8


class TestFGValues:
    """Tests for FG_VALUES lookup table."""

    def test_range(self):
        assert len(FG_VALUES) == 4
        assert 0 in FG_VALUES
        assert 3 in FG_VALUES

    def test_values(self):
        assert FG_VALUES[0] == -2.8
        assert FG_VALUES[3] == -0.2


class TestSWValues:
    """Tests for SW_VALUES lookup table."""

    def test_range(self):
        assert len(SW_VALUES) == 8
        assert 0 in SW_VALUES
        assert 7 in SW_VALUES

    def test_values(self):
        assert SW_VALUES[0] == 1050
        assert SW_VALUES[7] == 1630


class TestChipsPerCard:
    """Tests for CHIPS_PER_CARD."""

    def test_x8(self):
        assert CHIPS_PER_CARD[CardType.X8] == 4

    def test_x16(self):
        assert CHIPS_PER_CARD[CardType.X16] == 8


class TestOtherConstants:
    """Tests for other constants."""

    def test_channels_per_chip(self):
        assert CHANNELS_PER_CHIP == 4

    def test_command_prompt(self):
        assert COMMAND_PROMPT == "Cmd>"

    def test_default_baudrate(self):
        assert DEFAULT_BAUDRATE == 115200
