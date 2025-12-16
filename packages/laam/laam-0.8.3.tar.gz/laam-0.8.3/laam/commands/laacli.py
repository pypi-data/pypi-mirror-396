# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import json
import sys

import laam.exceptions


def configure_parser(parser):
    ssub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "button"
    btn = ssub.add_parser("button", help="Virtual buttons")
    btn.set_defaults(func=handle_button)
    btn.add_argument("button", choices=["1", "2", "power", "reset"], help="Button")
    btn.add_argument("state", choices=["on", "off", "status"], help="State")
    btn.add_argument("--json", action="store_true", help="Output in json")

    # "led"
    led = ssub.add_parser("led", help="User LED")
    led.set_defaults(func=handle_led)
    led.add_argument("state", choices=["on", "off"], help="LED color")
    led.add_argument("--json", action="store_true", help="Output in json")

    # "power"
    pwr = ssub.add_parser("power", help="Power rails")
    pwr.set_defaults(func=handle_power)
    pwr.add_argument("vbus", choices=["1v8", "3v3", "5v", "12v"], help="Rail")
    pwr.add_argument("state", choices=["on", "off", "reset", "status"], help="State")
    pwr.add_argument("--json", action="store_true", help="Output in json")

    # "rev"
    rev = ssub.add_parser("rev", help="LAA revision")
    rev.set_defaults(func=handle_rev)
    rev.add_argument("--json", action="store_true", help="Output in json")

    # "screenshot"
    screenshot = ssub.add_parser("screenshot", help="OLED screenshot")
    screenshot.set_defaults(func=handle_screenshot)
    screenshot.add_argument(
        "filename", type=argparse.FileType("wb"), help="Store the screenshot bitmap"
    )
    screenshot.add_argument("--json", action="store_true", help="Output in json")

    # "temp"
    temp = ssub.add_parser("temp", help="Query temperature (°C)")
    temp.set_defaults(func=handle_temp)
    temp.add_argument("probe", choices=["amb", "dut", "sys"], help="Probe")
    temp.add_argument("--json", action="store_true", help="Output in json")

    # "usb"
    usb = ssub.add_parser("usb", help="USB hub")
    usb.set_defaults(func=handle_usb)
    usb.add_argument("port", type=int, help="USB port, 0 will be the hub itself")
    usb.add_argument(
        "state", choices=["on", "off", "reset", "start", "status"], help="State"
    )
    usb.add_argument("--json", action="store_true", help="Output in json")

    # "usbg-ms"
    usbgms = ssub.add_parser("usbg-ms", help="USB Gadget Mass storage")
    usbgms.set_defaults(func=handle_usbg_ms)
    usbgms.add_argument("state", choices=["on", "off", "status"], help="State")
    usbgms.add_argument("filename", help="Disk image to mount", default="", nargs="?")
    usbgms.add_argument("--json", action="store_true", help="Output in json")

    # "watt"
    watt = ssub.add_parser("watt", help="Power consumption")
    watt.set_defaults(func=handle_watt)
    watt.add_argument("vbus", choices=["1v8", "3v3", "5v", "12v"], help="Rail")
    watt.add_argument("--json", action="store_true", help="Output in json")


def print_and_return(data, asjson):
    if asjson:
        print(json.dumps(data))
    else:
        if data["stdout"]:
            print(data["stdout"])
        if data["stderr"]:
            print(data["stderr"], file=sys.stderr)
    return data["code"]


def handle_button(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.button(options.button, options.state),
            getattr(options, "json", False),
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_led(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.led(options.state), getattr(options, "json", False)
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_power(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.power(options.vbus, options.state),
            getattr(options, "json", False),
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_rev(options, laa) -> int:
    try:
        return print_and_return(laa.laacli.rev(), getattr(options, "json", False))
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_screenshot(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.screenshot(options.filename), getattr(options, "json", False)
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_temp(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.temp(options.probe), getattr(options, "json", False)
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_usb(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.usb(options.port, options.state), getattr(options, "json", False)
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_usbg_ms(options, laa) -> int:
    if options.state == "on" and not options.filename:
        print(
            "laam laacli usbg-ms: error: filename is required when state is 'on'",
            file=sys.stderr,
        )
        return 2
    try:
        return print_and_return(
            laa.laacli.usbg_ms(options.state, options.filename),
            getattr(options, "json", False),
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_watt(options, laa) -> int:
    try:
        return print_and_return(
            laa.laacli.watt(options.vbus), getattr(options, "json", False)
        )
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def help_string():
    return "Run laacli commands on the LAA"
