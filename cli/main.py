import argparse
import os
import time

from .env import load_environment, env
from .compose import up_core, up_generator, down, reset, status as local_status
from .wait import wait_for_connect
from .cdc import setup_local, verify_local, render
from .connect_api import apply as connector_apply, status as connector_status, delete as connector_delete


def local_up(a):
    os.environ["DB_TYPE"] = "postgres"
    os.environ["DB_HOST"] = "postgres"
    os.environ["DB_PORT"] = "5432"
    up_core(a.env_file)
    wait_for_connect(env("CONNECT_REST_URL", "http://localhost:8083"))
    time.sleep(3)  # brief buffer — Connect is ready but may still be registering internal topics
    setup_local()
    connector_apply()
    if env("GENERATOR_ENABLED", "true").lower() == "true":
        up_generator(a.env_file)
    print("[ok] local PostgreSQL CDC stack is up")


def parser():
    p = argparse.ArgumentParser(prog="platform.py")
    p.add_argument("--env-file", default=".env.local")
    sub = p.add_subparsers(dest="group", required=True)

    # local <action>
    l = sub.add_parser("local")
    ls = l.add_subparsers(dest="action", required=True)
    ls.add_parser("up").set_defaults(func=local_up)
    ls.add_parser("status").set_defaults(func=lambda a: local_status(a.env_file))
    ls.add_parser("down").set_defaults(func=lambda a: down(a.env_file))
    ls.add_parser("reset").set_defaults(func=lambda a: (reset(a.env_file), time.sleep(5), local_up(a)))

    # cdc <action>
    c = sub.add_parser("cdc")
    cs = c.add_subparsers(dest="action", required=True)
    cs.add_parser("setup").set_defaults(func=lambda a: setup_local())
    cs.add_parser("verify").set_defaults(func=lambda a: verify_local())
    cs.add_parser("render").set_defaults(func=lambda a: print(render()))

    # connector <action>
    k = sub.add_parser("connector")
    ks = k.add_subparsers(dest="action", required=True)
    ks.add_parser("apply").set_defaults(func=lambda a: connector_apply())
    ks.add_parser("status").set_defaults(func=lambda a: connector_status())
    ks.add_parser("delete").set_defaults(func=lambda a: connector_delete())

    return p


def main():
    p = parser()
    a = p.parse_args()
    load_environment(a.env_file)
    a.func(a)
