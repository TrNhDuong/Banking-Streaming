"""
Connectors subpackage — PostgreSQL / Debezium only.

Public interface (unchanged from before):
    from .connectors import build
"""
from . import postgres


def build() -> dict:
    """Return the Debezium connector config dict for PostgreSQL."""
    return postgres.config()
