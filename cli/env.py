import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment(path: str) -> None:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Environment file not found: {path}")
    load_dotenv(p, override=True)


def env(name: str, default: str | None = None, required: bool = False) -> str | None:
    """Return the value of an environment variable.

    Returns `default` if the variable is not set.
    Raises RuntimeError if `required=True` and the value is falsy.
    """
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value
