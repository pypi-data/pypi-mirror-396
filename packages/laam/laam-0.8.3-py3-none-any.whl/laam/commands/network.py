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

    # "addresses"
    network_addresses = ssub.add_parser("addresses", help="List addresses")
    network_addresses.set_defaults(func=handle_addresses)
    network_addresses.add_argument("--json", action="store_true", help="Output in json")

    # "hostname"
    network_hostname = ssub.add_parser("hostname", help="Hostname")
    network_hostname.set_defaults(func=handle_hostname)

    # "interfaces"
    network_interfaces = ssub.add_parser("interfaces", help="List interfaces")
    network_interfaces.set_defaults(func=handle_interfaces)
    network_interfaces.add_argument(
        "--json", action="store_true", help="Output in json"
    )

    # "routes"
    network_routes = ssub.add_parser("routes", help="List routes")
    network_routes.set_defaults(func=handle_routes)
    network_routes.add_argument("--json", action="store_true", help="Output in json")

    # "settings"
    network_settings = ssub.add_parser("settings", help="Settings")
    network_settings.set_defaults(func=handle_settings)


def handle_addresses(options, laa) -> int:
    try:
        addresses = laa.network.addresses()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(addresses))
    else:
        print("Addresses:")
        for name in addresses:
            print(f"* {name}")
            for addr in addresses[name]:
                print(f"  * {addr['flags']}\t{addr['ip']}/{addr['prefix']}")
    return 0


def handle_hostname(options, laa) -> int:
    try:
        hostname = laa.network.hostname()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(hostname["hostname"])
    return 0


def handle_interfaces(options, laa) -> int:
    try:
        interfaces = laa.network.interfaces()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(interfaces))
    else:
        print("Interfaces:")
        for s in interfaces:
            if s["mac"]:
                print(f"* {s['name']} ({s['type']}): {s['status']} [{s['mac']}]")
            else:
                print(f"* {s['name']} ({s['type']}): {s['status']}")
    return 0


def handle_routes(options, laa) -> int:
    try:
        routes = laa.network.routes()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(routes))
    else:
        print("Routes:")
        for name in routes:
            if not routes[name]:
                continue
            print(f"* {name}")
            for r in routes[name]:
                if r["via"]:
                    print(
                        f"  * {r['src']} => {r['dst']}/{r['dst_prefix']} via {r['via']} type {r['type']} protocol {r['protocol']}"
                    )
                else:
                    print(
                        f"  * {r['src']} => {r['dst']}/{r['dst_prefix']} type {r['type']} protocol {r['protocol']}"
                    )
    return 0


def handle_settings(options, laa) -> int:
    try:
        settings = laa.network.settings()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(settings)
    return 0


def help_string():
    return "Manage network"
