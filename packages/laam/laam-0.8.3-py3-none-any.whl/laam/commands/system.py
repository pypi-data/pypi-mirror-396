# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import contextlib
import json
import sys

import laam.exceptions
from laam.utils import Color, get_color


def configure_parser(parser):
    ssub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "logs"
    system_logs = ssub.add_parser("logs", help="Appliance logs")
    system_logs.set_defaults(func=handle_logs)
    system_logs.add_argument("--json", action="store_true", help="Output in json")

    # "fleet"
    system_fleet = ssub.add_parser("fleet", help="Bakfleet Information")
    system_fleet.set_defaults(func=handle_fleet)
    system_fleet.add_argument("--json", action="store_true", help="Output in json")

    # "version"
    system_version = ssub.add_parser("version", help="Appliance Version")
    system_version.set_defaults(func=handle_version)


def handle_version(options, laa) -> int:
    try:
        version = laa.system.version()
    except laam.exceptions.LAAError as exc:
        if exc.http_code == 404:
            # to be deleted after next LAA release (>v1.4.1)
            print("Not available in this version, please check available LAA updates")
        else:
            print(exc, file=sys.stderr)
        return 1

    print(version)
    return 0


def handle_fleet(options, laa) -> int:
    try:
        fleet = laa.system.fleet()
    except laam.exceptions.LAAError as exc:
        if exc.http_code == 404:
            # to be deleted after next LAA release (>v1.4.1)
            print("Not available in this version, please check available LAA updates")
        else:
            print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(fleet))
    else:
        print("Fleet:")
        print(f"* online: {fleet['online']}")
        print(f"* serial: {fleet['serial']}")
        print(f"* org   : {fleet['organization']}")
        print(f"* token : {fleet['token']}")
    return 0


def handle_logs(options, laa) -> int:
    try:
        logs = laa.system.logs()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(logs))
    else:
        for log in logs:
            msg = log["dt_iso"]
            priority = 6
            with contextlib.suppress(ValueError):
                priority = int(log.get("priority", 6))
            if log.get("pid"):
                msg += f" [{log['pid']}]"
            if log.get("logger"):
                msg += f" [{log['logger']}]"
            msg += f" {get_color(priority)}{log['message']}{Color.end.value}"
            print(msg)
    return 0


def help_string():
    return "Get LAA Info"
