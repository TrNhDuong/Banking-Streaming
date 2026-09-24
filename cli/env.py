import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment(path):
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Environment file not found: {path}")
    load_dotenv(p, override=True)


def env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value or ""
