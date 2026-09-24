"""
Command handler functions for the platform CLI.

Each function maps to one CLI subcommand and receives the parsed
argparse Namespace. Keeping handlers here keeps main.py focused on
parser definition and entry point only.
"""
import os
import time

from .env import env
from .compose import up_core, up_generator, down, reset, status as local_status, wait_for_connect
from .cdc import setup_local, verify_local, render
from .connect_api import apply as connector_apply, status as connector_status, delete as connector_delete


def cmd_local_up(a) -> None:
    os.environ["DB_TYPE"] = "postgres"
    os.environ["DB_HOST"] = "postgres"
    os.environ["DB_PORT"] = "5432"
    up_core(a.env_file)
    wait_for_connect(env("CONNECT_REST_URL") or "http://localhost:8083")
    time.sleep(3)  # brief buffer — Connect is ready but may still be registering internal topics
    setup_local()
    connector_apply()
    if (env("GENERATOR_ENABLED") or "true").lower() == "true":
        up_generator(a.env_file)
    print("[ok] local PostgreSQL CDC stack is up")


def cmd_local_status(a) -> None:
    local_status(a.env_file)


def cmd_local_down(a) -> None:
    down(a.env_file)


def cmd_local_reset(a) -> None:
    reset(a.env_file)
    time.sleep(5)   # wait for volumes to be fully removed before bringing stack back up
    cmd_local_up(a)


def cmd_cdc_setup(a) -> None:
    setup_local()


def cmd_cdc_verify(a) -> None:
    verify_local()


def cmd_cdc_render(a) -> None:
    print(render())


def cmd_connector_apply(a) -> None:
    connector_apply()


def cmd_connector_status(a) -> None:
    connector_status()


def cmd_connector_delete(a) -> None:
    connector_delete()
