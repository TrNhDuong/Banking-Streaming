from ..env import env


def common():
    """Base Debezium connector config shared by all adapters."""
    return {
        "tasks.max": "1",
        "topic.prefix": env("TOPIC_PREFIX", "banking"),
        "table.include.list": env("CDC_TABLES", required=True),
        "snapshot.mode": env("SNAPSHOT_MODE", "initial"),
        "decimal.handling.mode": "string",
    }
