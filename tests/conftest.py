import pytest

# Environment variables used across tests — cleared before each test
# to prevent leakage between test cases.
_TEST_ENV_VARS = [
    "CDC_TABLES", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
    "DB_SSLMODE", "DB_TYPE", "TOPIC_PREFIX", "SNAPSHOT_MODE", "CONNECTOR_NAME",
    "CONNECT_REST_URL", "KAFKA_BOOTSTRAP_SERVERS",
    "POSTGRES_ADMIN_USER", "POSTGRES_PUBLICATION_NAME", "POSTGRES_SLOT_NAME",
    "MYSQL_ROOT_PASSWORD", "MSSQL_SA_PASSWORD",
    "GENERATOR_ENABLED", "SEED_ENABLED",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove all pipeline-related env vars before every test."""
    for var in _TEST_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
