# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import json
import sys

import laam.exceptions


def configure_parser(parser):
    ssub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "usbs list"
    usbs_list = ssub.add_parser("list", help="List USB devices")
    usbs_list.set_defaults(func=handle_list)
    usbs_list.add_argument("--json", action="store_true", help="Output in json")

    # "usbs show"
    usbs_show = ssub.add_parser("show", help="USB details")
    usbs_show.set_defaults(func=handle_show)
    usbs_show.add_argument("bus", help="usb bus")
    usbs_show.add_argument("device", help="usb device")


def handle_list(options, laa) -> int:
    try:
        usbs = laa.usbs.list()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(usbs))
    else:
        for u in usbs:
            print(f"Bus {u['bus']} Device {u['device']}: ID {u['id']} {u['tag']}")
    return 0


def handle_show(options, laa) -> int:
    try:
        usb_text = laa.usbs.get(options.bus, options.device)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(usb_text)
    return 0


def help_string():
    return "List USB devices"
