"""
CDC subpackage — PostgreSQL only.

Public interface (unchanged from before):
    from .cdc import setup_local, verify_local, render
"""
from . import postgres


def render() -> str:
    """Return the CDC setup SQL without executing it."""
    return postgres.sql()


def setup_local() -> None:
    """Run CDC setup SQL against the local Docker container."""
    postgres.setup()


def verify_local() -> None:
    """Query CDC status from the local Docker container."""
    postgres.verify()
