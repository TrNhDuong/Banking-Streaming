from ..env import env
from ._common import common


def config():
    c = common()
    c.update({
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": env("DB_HOST", required=True),
        "database.port": env("DB_PORT", "5432"),
        "database.user": env("DB_USER", required=True),
        "database.password": env("DB_PASSWORD", required=True),
        "database.dbname": env("DB_NAME", required=True),
        "database.sslmode": env("DB_SSLMODE", "disable"),
        "plugin.name": "pgoutput",
        "publication.name": env("POSTGRES_PUBLICATION_NAME", "banking_publication"),
        "publication.autocreate.mode": "disabled",
        "slot.name": env("POSTGRES_SLOT_NAME", "banking_debezium_slot"),
        "slot.drop.on.stop": "false",          # keep replication slot across restarts
        "heartbeat.interval.ms": "10000",
        "tombstones.on.delete": "true",         # emit null tombstone on DELETE for log compaction
        # Error handling — tolerate bad events and route to DLQ instead of stopping the connector
        "errors.tolerance": "all",
        "errors.deadletterqueue.topic.name": env("TOPIC_PREFIX", "banking") + ".dlq",
        "errors.deadletterqueue.context.headers.enable": "true",
    })
    return c
