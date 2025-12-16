# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import json
import os
import pathlib
import sys

import laam.exceptions


def configure_parser(parser):
    ssub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "list"
    files_list = ssub.add_parser("list", help="List files")
    files_list.set_defaults(func=handle_list)
    files_list.add_argument("--json", action="store_true", help="Output in json")

    # "pull"
    files_pull = ssub.add_parser("pull", help="Pull a file")
    files_pull.set_defaults(func=handle_pull)
    files_pull.add_argument("name", help="filename")
    files_pull.add_argument("file", type=pathlib.Path)
    files_pull.add_argument(
        "--force", "-f", action="store_true", help="Overwrite file if already exists"
    )

    # "push"
    files_push = ssub.add_parser("push", help="Push a file")
    files_push.set_defaults(func=handle_push)
    files_push.add_argument("file", type=argparse.FileType("rb"))
    files_push.add_argument("name", help="filename")

    # "rm"
    files_rm = ssub.add_parser("rm", help="Remove a file")
    files_rm.set_defaults(func=handle_rm)
    files_rm.add_argument("name", help="filename")


def handle_list(options, laa) -> int:
    try:
        files = laa.files.list()
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1

    if options.json:
        print(json.dumps(files))
    else:
        print("Files:")
        for s in files:
            print(f"* {s}")
    return 0


def handle_pull(options, laa) -> int:
    if os.path.exists(options.file) and not options.force:
        overwrite = input(
            "The file already exists on this machine, do you want to overwrite it [y/n]? "
        )
        if overwrite != "y":
            print("Not overwriting the file, exiting", file=sys.stderr)
            return 1

        options.force = True

    if os.path.exists(options.file) and options.force:
        print("The file will be overwritten")

    try:
        return int(not laa.files.pull(options.name, options.file, options.force))
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_push(options, laa) -> int:
    try:
        return int(not laa.files.push(options.name, options.file))
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def handle_rm(options, laa) -> int:
    try:
        return int(not laa.files.remove(options.name))
    except laam.exceptions.LAAError as exc:
        print(exc, file=sys.stderr)
        return 1


def help_string():
    return "Manage files in /var/lib/lava/dispatcher/tmp"
