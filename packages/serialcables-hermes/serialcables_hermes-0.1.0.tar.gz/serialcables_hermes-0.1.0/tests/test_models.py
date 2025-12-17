"""Tests for data models."""

import pytest

from serialcables_hermes.constants import CardType, DeviceWidth, LoadMode
from serialcables_hermes.models import (
    BISTResult,
    CardInfo,
    CardStatus,
    ChannelEQ,
    ChipEQ,
    CurrentInfo,
    DualPortStatus,
    EDSFFDetection,
    EQSettings,
    FanInfo,
    I2CDevice,
    LoadConfiguration,
    MCUInfo,
    ProductInfo,
    ThermalInfo,
    VersionInfo,
)


class TestThermalInfo:
    """Tests for ThermalInfo model."""

    def test_create(self):
        info = ThermalInfo(temperature_celsius=35.5)
        assert info.temperature_celsius == 35.5

    def test_str(self):
        info = ThermalInfo(temperature_celsius=35.5)
        assert "35.5" in str(info)


class TestFanInfo:
    """Tests for FanInfo model."""

    def test_create(self):
        info = FanInfo(speed_rpm=5000)
        assert info.speed_rpm == 5000


class TestCurrentInfo:
    """Tests for CurrentInfo model."""

    def test_create(self):
        info = CurrentInfo(current_amps=0.5)
        assert info.current_amps == 0.5


class TestCardStatus:
    """Tests for CardStatus model."""

    def test_create(self):
        status = CardStatus(
            thermal=ThermalInfo(temperature_celsius=30),
            fan=FanInfo(speed_rpm=5000),
            current=CurrentInfo(current_amps=0.3),
        )
        assert status.thermal.temperature_celsius == 30
        assert status.fan.speed_rpm == 5000
        assert status.current.current_amps == 0.3


class TestVersionInfo:
    """Tests for VersionInfo model."""

    def test_create(self):
        info = VersionInfo(
            product=ProductInfo(
                company="Serial Cables",
                model="GEN6 REDRIVER",
                serial_number="ABC123",
            ),
            mcu=MCUInfo(version="1.0.0", build_time="2025-01-01"),
        )
        assert info.product.company == "Serial Cables"
        assert info.mcu.version == "1.0.0"


class TestEQSettings:
    """Tests for EQSettings model."""

    def test_create_empty(self):
        settings = EQSettings()
        assert len(settings.chips) == 0

    def test_create_with_chips(self):
        settings = EQSettings(
            chips=[
                ChipEQ(
                    chip=0,
                    channels=[
                        ChannelEQ(channel=0, eq_step=3, eq_db=5.4),
                        ChannelEQ(channel=1, eq_step=3, eq_db=5.4),
                    ],
                )
            ]
        )
        assert len(settings.chips) == 1
        assert settings.chips[0].chip == 0
        assert len(settings.chips[0].channels) == 2


class TestBISTResult:
    """Tests for BISTResult model."""

    def test_create_empty(self):
        result = BISTResult()
        assert len(result.devices) == 0

    def test_with_devices(self):
        result = BISTResult(
            devices=[
                I2CDevice(channel=0, device_name="DEV1", address=0x50, status="OK"),
                I2CDevice(channel=0, device_name="DEV2", address=0x51, status="OK"),
            ]
        )
        assert len(result.devices) == 2
        assert result.devices[0].status == "OK"

    def test_device_status(self):
        result = BISTResult(
            devices=[
                I2CDevice(channel=0, device_name="DEV1", address=0x50, status="OK"),
                I2CDevice(channel=0, device_name="DEV2", address=0x51, status="FAIL"),
            ]
        )
        assert result.devices[1].status == "FAIL"


class TestEDSFFDetection:
    """Tests for EDSFFDetection model."""

    def test_present(self):
        detection = EDSFFDetection(width=DeviceWidth.X8, present=True)
        assert detection.present is True
        assert detection.width == DeviceWidth.X8

    def test_not_present(self):
        detection = EDSFFDetection(width=DeviceWidth.NONE, present=False)
        assert detection.present is False


class TestLoadConfiguration:
    """Tests for LoadConfiguration model."""

    def test_create(self):
        config = LoadConfiguration(mode=LoadMode.MEDIUM, description="6-9 inches")
        assert config.mode == LoadMode.MEDIUM


class TestCardInfo:
    """Tests for CardInfo model."""

    def test_create(self):
        info = CardInfo(
            card_type=CardType.X8,
            version=VersionInfo(
                product=ProductInfo(company="SC", model="M", serial_number="S"),
                mcu=MCUInfo(version="1.0", build_time="now"),
            ),
            status=CardStatus(
                thermal=ThermalInfo(temperature_celsius=25),
                fan=FanInfo(speed_rpm=4000),
                current=CurrentInfo(current_amps=0.2),
            ),
            detection=EDSFFDetection(width=DeviceWidth.X8, present=True),
            dual_port=DualPortStatus(enabled=False),
        )
        assert info.card_type == CardType.X8
