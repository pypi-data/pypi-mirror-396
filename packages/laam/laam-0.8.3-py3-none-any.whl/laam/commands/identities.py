# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import os
import sys

import yaml


class ConfigurationError(Exception):
    pass


def configure_parser(parser):
    sub = parser.add_subparsers(
        dest="sub_cmd", help="Sub command", title="Sub command", required=True
    )

    # "add"
    config_add = sub.add_parser("add", help="add an identity")
    config_add.set_defaults(func=handle_add)
    config_add.add_argument("id", type=str, help="identity")
    config_add.add_argument(
        "--uri", type=str, required=True, help="URI of the baklaweb"
    )
    config_add.add_argument("--token", type=str, required=True, help="api token")

    # "update"
    config_add = sub.add_parser("update", help="update an identity")
    config_add.set_defaults(func=handle_update)
    config_add.add_argument("id", type=str, help="identity")
    config_add.add_argument("--uri", type=str, default=None, help="URI of the baklaweb")
    config_add.add_argument("--token", type=str, default=None, help="api token")

    # "delete"
    config_del = sub.add_parser("delete", help="delete an identity")
    config_del.set_defaults(func=handle_delete)
    config_del.add_argument("id", help="identity")

    # "list"
    config_list = sub.add_parser("list", help="list available identities")
    config_list.set_defaults(func=handle_list)

    # "show"
    config_show = sub.add_parser("show", help="show identity details")
    config_show.set_defaults(func=handle_show)
    config_show.add_argument("id", type=str, help="identity")


def help_string():
    return "Manage laam configuration"


def _load_configuration():
    config_dir = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    config_filename = os.path.expanduser(os.path.join(config_dir, "laam.yaml"))

    try:
        with open(config_filename, encoding="utf-8") as f_conf:
            data = yaml.safe_load(f_conf.read())
            if not isinstance(data, dict):
                raise ConfigurationError("Invalid configuration file")
            return data
    except (FileNotFoundError, KeyError, TypeError):
        return {}


def _save_configuration(config):
    config_dir = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    expanded_config_dir = os.path.expanduser(config_dir)
    config_filename = os.path.expanduser(os.path.join(config_dir, "laam.yaml"))

    if not os.path.exists(expanded_config_dir):
        os.makedirs(expanded_config_dir)

    with open(config_filename, "w", encoding="utf-8") as f_conf:
        yaml.safe_dump(config, f_conf)


def handle_add(options, _):
    config = _load_configuration()
    if options.id in config:
        print("Identity '%s' already exists" % options.id)
        return 1
    config[options.id] = {
        "uri": options.uri,
        "token": options.token,
    }
    _save_configuration(config)
    return 0


def handle_update(options, _):
    config = _load_configuration()

    if options.id not in config:
        print("Unknown identity '%s'" % options.id, file=sys.stderr)
        return 1

    if not options.token and not options.uri:
        print("Please provide at least a token or a uri")
        return 1

    if options.token:
        config[options.id]["token"] = options.token

    if options.uri:
        config[options.id]["uri"] = options.uri

    _save_configuration(config)
    return 0


def handle_delete(options, _):
    config = _load_configuration()
    try:
        del config[options.id]
    except KeyError:
        print("Unknown identity '%s'" % options.id, file=sys.stderr)
        return 1
    _save_configuration(config)
    return 0


def handle_list(_, __):
    config = _load_configuration()
    print("Identities:")
    for identity in sorted(config.keys()):
        print("* %s" % identity)
    return 0


def handle_show(options, _):
    config = _load_configuration()
    try:
        yaml.safe_dump(config[options.id], sys.stdout)
        return 0
    except KeyError:
        print("Unknown identity '%s'" % options.id, file=sys.stderr)
        return 1
