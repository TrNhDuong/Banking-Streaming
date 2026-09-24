"""
CLI entry point — parser definition only.
Command handler functions live in cli/commands.py.
"""
import argparse

from .env import load_environment
from .commands import (
    cmd_local_up, cmd_local_status, cmd_local_down, cmd_local_reset,
    cmd_cdc_setup, cmd_cdc_verify, cmd_cdc_render,
    cmd_connector_apply, cmd_connector_status, cmd_connector_delete,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="manage.py")
    p.add_argument("--env-file", default=".env.local")
    sub = p.add_subparsers(dest="group", required=True)

    # local <action>
    l = sub.add_parser("local")
    ls = l.add_subparsers(dest="action", required=True)
    ls.add_parser("up").set_defaults(func=cmd_local_up)
    ls.add_parser("status").set_defaults(func=cmd_local_status)
    ls.add_parser("down").set_defaults(func=cmd_local_down)
    ls.add_parser("reset").set_defaults(func=cmd_local_reset)

    # cdc <action>
    c = sub.add_parser("cdc")
    cs = c.add_subparsers(dest="action", required=True)
    cs.add_parser("setup").set_defaults(func=cmd_cdc_setup)
    cs.add_parser("verify").set_defaults(func=cmd_cdc_verify)
    cs.add_parser("render").set_defaults(func=cmd_cdc_render)

    # connector <action>
    k = sub.add_parser("connector")
    ks = k.add_subparsers(dest="action", required=True)
    ks.add_parser("apply").set_defaults(func=cmd_connector_apply)
    ks.add_parser("status").set_defaults(func=cmd_connector_status)
    ks.add_parser("delete").set_defaults(func=cmd_connector_delete)

    return p


def main() -> None:
    p = parser()
    a = p.parse_args()
    load_environment(a.env_file)
    a.func(a)
