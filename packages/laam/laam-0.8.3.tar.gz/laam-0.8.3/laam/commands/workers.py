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

    # "dockerfile"
    workers_dockerfile = ssub.add_parser("dockerfile", help="LAVA worker Dockerfile")
    workers_dockerfile.set_defaults(func=handle_dockerfile)
    workers_dockerfile.add_argument("id", type=int, help="Worker id")

    # "list"
    workers_list = ssub.add_parser("list", help="List workers")
    workers_list.set_defaults(func=handle_list)
    workers_list.add_argument("--json", action="store_true", help="Output in json")

    # "logs"
    workers_logs = ssub.add_parser("logs", help="Worker logs")
    workers_logs.set_defaults(func=handle_logs)
    workers_logs.add_argument("id", type=int, help="Worker id")
    workers_logs.add_argument("--json", action="store_true", help="Output in json")

    # "show"
    workers_show = ssub.add_parser("show", help="Worker details")
    workers_show.set_defaults(func=handle_show)
    workers_show.add_argument("id", type=int, help="Worker id")
    workers_show.add_argument("--json", action="store_true", help="Output in json")

    # "test"
    workers_test = ssub.add_parser("test", help="Test connection to server")
    workers_test.set_defaults(func=handle_test)
    workers_test.add_argument("id", type=int, help="Worker id")
    workers_test.add_argument("--json", action="store_true", help="Output in json")


def handle_dockerfile(options, laa) -> int:
    try:
        dockerfile = laa.workers.dockerfile(options.id)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(dockerfile)
    return 0


def handle_list(options, laa) -> int:
    try:
        workers = laa.workers.list()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(workers))
    else:
        print("Workers:")
        for w in workers:
            print(f"* {w['id']}: {w['name']} - {w['server_url']}")


def handle_logs(options, laa) -> int:
    try:
        logs = laa.workers.logs(options.id)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(logs))
    else:
        for l in logs:
            msg = l["dt_iso"]
            priority = 6
            with contextlib.suppress(ValueError):
                priority = int(l.get("priority", 6))
            if l.get("pid"):
                msg += f" [{l['pid']}]"
            if l.get("logger"):
                msg += f" [{l['logger']}]"
            msg += f" {get_color(priority)}{l['message']}{Color.end.value}"
            print(msg)

    return 0


def handle_show(options, laa) -> int:
    try:
        worker = laa.workers.get(options.id)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(worker))
    else:
        print(f"id        : {worker['id']}")
        print(f"name      : {worker['name']}")
        print(f"running   : {worker['running']}")
        print(f"server url: {worker['server_url']}")
        print(f"token     : {worker['token']}")


def handle_test(options, laa) -> int:
    try:
        test = laa.workers.test(options.id)
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(test))
    return 0 if test["connected"] else 1


def help_string():
    return "Manage workers"
