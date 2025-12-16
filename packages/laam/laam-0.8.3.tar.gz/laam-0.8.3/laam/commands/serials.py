# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import asyncio
import json
import re
import sys

import laam.exceptions


def configure_parser(parser):
    ssub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "serials list"
    serials_list = ssub.add_parser("list", help="List serials")
    serials_list.set_defaults(func=handle_list)
    serials_list.add_argument("--filter", default=None, help="Filter by path")
    serials_list.add_argument("--json", action="store_true", help="Output in json")

    # "serials connect"
    serials_connect = ssub.add_parser("connect", help="Connect to serial")
    serials_connect.set_defaults(func=handle_connect)
    serials_connect.add_argument("name", help="name of the serial")
    serials_connect.add_argument(
        "--readonly", "--ro", action="store_true", help="Start the connection read-only"
    )

    # "serials show"
    serials_show = ssub.add_parser("show", help="Serial details")
    serials_show.set_defaults(func=handle_show)
    serials_show.add_argument("--json", action="store_true", help="Output in json")
    serials_show.add_argument("name", help="name of the serial")


def handle_list(options, laa) -> int:
    try:
        serials = laa.serials.list(options.filter)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(serials))
    else:
        serials_dict = {}
        for s in serials:
            baudrate = int(re.split("[neomsNEOMS]", s["speed"])[0])
            serials_dict.setdefault(s["path"], {})[baudrate] = (
                s["name"],
                s["port"],
                s["speed"],
            )

        print("Serials:")
        for s in serials_dict:
            print(f"* {s}")
            for speed in serials_dict[s]:
                d = serials_dict[s][speed]
                print(f"  * {d[0]}")
                print(f"    - port : {d[1]}")
                print(f"    - speed: {d[2]}")
    return 0


def handle_connect(options, laa) -> int:
    print(f"Connecting to {options.ws_url} serial {options.name}")
    try:
        result = asyncio.run(
            laa.serials.connect_async_fun(options.name, options.readonly)
        )
    except NameError:
        raise
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"\nUnable to connect: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nLeaving...")
        return 1

    print("\nLeaving...")
    return result


def handle_show(options, laa) -> int:
    try:
        serial = laa.serials.get(options.name)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(serial))
    else:
        print(f"name : {serial['name']}")
        print(f"path : {serial['path']}")
        print(f"port : {serial['port']}")
        print(f"speed:{serial['speed']}")
    return 0


def help_string():
    return "Manage DUT serials"
