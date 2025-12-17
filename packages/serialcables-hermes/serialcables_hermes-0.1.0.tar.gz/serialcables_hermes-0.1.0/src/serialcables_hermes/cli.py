"""
Command-line interface for the Hermes API.

This module provides a CLI for interacting with Serial Cables PCIe Gen6
EDSFF Redriver cards from the terminal.
"""

import argparse
import json
import sys
from typing import Any

from .constants import (
    EQ_VALUES,
    FG_VALUES,
    SW_VALUES,
    Channel,
    DualPortState,
    LEDState,
    LoadMode,
    PowerDisableLevel,
)
from .exceptions import HermesError
from .hermes import Hermes


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="hermes",
        description="Serial Cables PCIe Gen6 EDSFF Redriver Card CLI",
    )

    parser.add_argument(
        "-p",
        "--port",
        help="Serial port (e.g., /dev/ttyUSB0, COM3)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List devices
    subparsers.add_parser("list", help="List available serial ports")

    # Version info
    subparsers.add_parser("version", help="Show version information")

    # Status
    subparsers.add_parser("status", help="Show card status (temperature, fan, current)")

    # System info
    subparsers.add_parser("sysinfo", help="Show complete system information")

    # BIST
    subparsers.add_parser("bist", help="Run Built-In Self Test")

    # Detect
    subparsers.add_parser("detect", help="Detect attached EDSFF device")

    # EQ commands
    eq_parser = subparsers.add_parser("eq", help="EQ settings")
    eq_parser.add_argument("chip", nargs="?", help='Chip number (0-7) or "all"')
    eq_parser.add_argument("value", nargs="?", type=int, help="EQ step value (0-15)")
    eq_parser.add_argument("--help-values", action="store_true", help="Show EQ value table")

    # FG commands
    fg_parser = subparsers.add_parser("fg", help="Flat gain settings")
    fg_parser.add_argument("chip", nargs="?", help='Chip number (0-7) or "all"')
    fg_parser.add_argument("value", nargs="?", type=int, help="FG step value (0-3)")
    fg_parser.add_argument("--help-values", action="store_true", help="Show FG value table")

    # SW commands
    sw_parser = subparsers.add_parser("sw", help="Swing settings")
    sw_parser.add_argument("chip", nargs="?", help='Chip number (0-7) or "all"')
    sw_parser.add_argument("value", nargs="?", type=int, help="SW step value (0-7)")
    sw_parser.add_argument("--help-values", action="store_true", help="Show SW value table")

    # Load configuration
    load_parser = subparsers.add_parser("load", help="Load preset configuration")
    load_parser.add_argument(
        "mode",
        nargs="?",
        choices=["s", "m", "l", "short", "medium", "long"],
        help="Configuration mode",
    )

    # Save configuration
    subparsers.add_parser("save", help="Save current configuration")

    # PERST
    perst_parser = subparsers.add_parser("perst", help="Send PERST# signal")
    perst_parser.add_argument(
        "channel", nargs="?", choices=["a", "b"], help="Channel (a, b, or both)"
    )

    # Dual port
    dual_parser = subparsers.add_parser("dual", help="Dual port control")
    dual_parser.add_argument(
        "state", nargs="?", choices=["on", "off"], help="Enable/disable dual port"
    )

    # Power disable
    pwrdis_parser = subparsers.add_parser("pwrdis", help="Power disable control")
    pwrdis_parser.add_argument("level", choices=["h", "l", "high", "low"], help="PWRDIS level")

    # Host LED
    hled_parser = subparsers.add_parser("hled", help="Host LED control")
    hled_parser.add_argument("state", choices=["on", "off"], help="LED state")

    # Reset
    subparsers.add_parser("reset", help="Reset MCU")

    # Raw command
    raw_parser = subparsers.add_parser("raw", help="Send raw command")
    raw_parser.add_argument("cmd", help="Raw command string")

    return parser


def output_result(result, as_json: bool = False) -> None:
    """Output result in appropriate format."""
    if as_json:
        if hasattr(result, "__dict__"):
            # Convert dataclass to dict
            def to_dict(obj):
                if hasattr(obj, "__dict__"):
                    d = {}
                    for k, v in obj.__dict__.items():
                        if not k.startswith("_"):
                            d[k] = to_dict(v)
                    return d
                elif isinstance(obj, list):
                    return [to_dict(item) for item in obj]
                elif hasattr(obj, "value"):  # Enum
                    return obj.value
                else:
                    return obj

            print(json.dumps(to_dict(result), indent=2))
        else:
            print(json.dumps(result))
    else:
        print(result)


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    # Handle list command without connection
    if args.command == "list":
        devices = Hermes.list_devices()
        if args.json:
            print(json.dumps(devices))
        else:
            if devices:
                print("Available serial ports:")
                for dev in devices:
                    print(f"  {dev}")
            else:
                print("No serial ports found")
        return 0

    # Handle help-values for eq/fg/sw
    if args.command == "eq" and getattr(args, "help_values", False):
        print("EQ Step Values:")
        for step, db in EQ_VALUES.items():
            print(f"  {step:2d}: {db:5.1f} dB")
        return 0

    if args.command == "fg" and getattr(args, "help_values", False):
        print("Flat Gain Step Values:")
        for step, db in FG_VALUES.items():
            print(f"  {step}: {db:5.1f} dB")
        return 0

    if args.command == "sw" and getattr(args, "help_values", False):
        print("Swing Step Values:")
        for step, mv in SW_VALUES.items():
            print(f"  {step}: {mv:4d} mV")
        return 0

    # All other commands need a port
    port = args.port
    if port is None:
        port = Hermes.find_device()
        if port is None:
            print("Error: No device found. Specify port with -p/--port", file=sys.stderr)
            return 1

    try:
        with Hermes(port) as hermes:
            result: Any = None

            if args.command == "version":
                result = hermes.get_version()

            elif args.command == "status":
                result = hermes.get_status()

            elif args.command == "sysinfo":
                result = hermes.get_system_info()

            elif args.command == "bist":
                result = hermes.run_bist()

            elif args.command == "detect":
                result = hermes.detect_edsff()

            elif args.command == "eq":
                if args.chip is not None and args.value is not None:
                    chip = args.chip if args.chip == "all" else int(args.chip)
                    result = hermes.set_eq(chip, args.value)
                else:
                    result = hermes.get_eq_settings()

            elif args.command == "fg":
                if args.chip is not None and args.value is not None:
                    chip = args.chip if args.chip == "all" else int(args.chip)
                    result = hermes.set_fg(chip, args.value)
                else:
                    result = hermes.get_fg_settings()

            elif args.command == "sw":
                if args.chip is not None and args.value is not None:
                    chip = args.chip if args.chip == "all" else int(args.chip)
                    result = hermes.set_sw(chip, args.value)
                else:
                    result = hermes.get_sw_settings()

            elif args.command == "load":
                if args.mode:
                    mode_map = {
                        "s": LoadMode.SHORT,
                        "short": LoadMode.SHORT,
                        "m": LoadMode.MEDIUM,
                        "medium": LoadMode.MEDIUM,
                        "l": LoadMode.LONG,
                        "long": LoadMode.LONG,
                    }
                    mode = mode_map[args.mode]
                    result = hermes.load_configuration(mode)
                else:
                    result = hermes.get_current_configuration()

            elif args.command == "save":
                result = hermes.save_configuration()

            elif args.command == "perst":
                channel = None
                if args.channel:
                    channel = Channel.A if args.channel == "a" else Channel.B
                result = hermes.send_perst(channel)

            elif args.command == "dual":
                if args.state:
                    state = DualPortState.ON if args.state == "on" else DualPortState.OFF
                    result = hermes.set_dual_port(state)
                else:
                    result = hermes.get_dual_port_status()

            elif args.command == "pwrdis":
                level_map = {
                    "h": PowerDisableLevel.HIGH,
                    "high": PowerDisableLevel.HIGH,
                    "l": PowerDisableLevel.LOW,
                    "low": PowerDisableLevel.LOW,
                }
                level = level_map[args.level]
                success = hermes.set_power_disable(level)
                result = "Success" if success else "Failed"

            elif args.command == "hled":
                led_state = LEDState.ON if args.state == "on" else LEDState.OFF
                success = hermes.set_host_led(led_state)
                result = "Success" if success else "Failed"

            elif args.command == "reset":
                result = hermes.reset_mcu()

            elif args.command == "raw":
                result = hermes.send_raw_command(args.cmd)

            if result is not None:
                output_result(result, args.json)

        return 0

    except HermesError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAborted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
