"""
CLI entry point — parser definition only.
Command handler functions live in cli/commands.py.
"""
import argparse

from .env import load_environment
from .logger import setup_cli_logging
from .commands import (
    cmd_local_up, cmd_local_status, cmd_local_down, cmd_local_reset,
    cmd_cdc_setup, cmd_cdc_verify, cmd_cdc_render,
    cmd_connector_apply, cmd_connector_status, cmd_connector_delete,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="manage.py")
    p.add_argument("--env-file", default=".env.local", help="Path to environment variables file")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    p.add_argument("--log-file", default=None, help="Optional file path to persist logs")
    sub = p.add_subparsers(dest="group", required=True)

    # local <action>
    l = sub.add_parser("local", help="Manage local Docker Compose infrastructure")
    ls = l.add_subparsers(dest="action", required=True)
    ls.add_parser("up", help="Start all local services (Postgres, Kafka, Connect, CDC, Generator)").set_defaults(func=cmd_local_up)
    ls.add_parser("status", help="Show status of local containers").set_defaults(func=cmd_local_status)
    ls.add_parser("down", help="Stop local containers").set_defaults(func=cmd_local_down)
    ls.add_parser("reset", help="Reset local containers and volumes").set_defaults(func=cmd_local_reset)

    # cdc <action>
    c = sub.add_parser("cdc", help="Manage database CDC replication & publications")
    cs = c.add_subparsers(dest="action", required=True)
    cs.add_parser("setup", help="Execute CDC setup SQL on the target database").set_defaults(func=cmd_cdc_setup)
    cs.add_parser("verify", help="Verify WAL level, publication, and replication slot status").set_defaults(func=cmd_cdc_verify)
    cs.add_parser("render", help="Render CDC SQL script without executing").set_defaults(func=cmd_cdc_render)

    # connector <action>
    k = sub.add_parser("connector", help="Manage Debezium connector via Kafka Connect REST API")
    ks = k.add_subparsers(dest="action", required=True)
    ks.add_parser("apply", help="Deploy or update the Debezium connector").set_defaults(func=cmd_connector_apply)
    ks.add_parser("status", help="Get current status of the connector").set_defaults(func=cmd_connector_status)
    ks.add_parser("delete", help="Delete the connector").set_defaults(func=cmd_connector_delete)

    return p


def main() -> None:
    p = parser()
    a = p.parse_args()
    setup_cli_logging(verbose=a.verbose, log_file=a.log_file)
    load_environment(a.env_file)
    a.func(a)
