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
from .logger import get_logger

logger = get_logger("commands")


def cmd_local_up(a) -> None:
    logger.info("=" * 60)
    logger.info("Launching Local Banking CDC Platform")
    logger.info("=" * 60)
    os.environ["DB_TYPE"] = "postgres"
    os.environ["DB_HOST"] = "postgres"
    os.environ["DB_PORT"] = "5432"

    logger.info("[1/5] Starting core containers (Kafka, Connect, Postgres)...")
    up_core(a.env_file)

    connect_url = env("CONNECT_REST_URL") or "http://localhost:8083"
    logger.info("[2/5] Waiting for Kafka Connect REST API at %s...", connect_url)
    wait_for_connect(connect_url)

    logger.info("Waiting 3s for internal Kafka Connect topics to settle...")
    time.sleep(3)

    logger.info("[3/5] Setting up CDC replication role & publications in Postgres...")
    setup_local()

    logger.info("[4/5] Applying Debezium connector configuration...")
    connector_apply()

    if (env("GENERATOR_ENABLED") or "true").lower() == "true":
        logger.info("[5/5] Starting synthetic transaction generator...")
        up_generator(a.env_file)
    else:
        logger.info("[5/5] Transaction generator skipped (GENERATOR_ENABLED=false)")

    logger.info("[SUCCESS] Local PostgreSQL CDC stack is fully up and streaming!")


def cmd_local_status(a) -> None:
    logger.info("Checking status of local services...")
    local_status(a.env_file)


def cmd_local_down(a) -> None:
    logger.info("Tearing down local platform containers...")
    down(a.env_file)
    logger.info("Local platform stopped.")


def cmd_local_reset(a) -> None:
    logger.warning("Resetting local stack: wiping containers, networks, and persistent data volumes...")
    reset(a.env_file)
    logger.info("Waiting 5s for volume cleanup...")
    time.sleep(5)
    cmd_local_up(a)


def cmd_cdc_setup(a) -> None:
    logger.info("Executing CDC setup on database...")
    setup_local()
    logger.info("CDC setup completed successfully.")


def cmd_cdc_verify(a) -> None:
    logger.info("Verifying database CDC prerequisites...")
    verify_local()


def cmd_cdc_render(a) -> None:
    logger.info("Rendering CDC prerequisite SQL script:")
    print(render())


def cmd_connector_apply(a) -> None:
    logger.info("Submitting connector configuration to Kafka Connect...")
    connector_apply()


def cmd_connector_status(a) -> None:
    logger.info("Retrieving connector status from Kafka Connect...")
    connector_status()


def cmd_connector_delete(a) -> None:
    logger.warning("Deleting connector from Kafka Connect...")
    connector_delete()
