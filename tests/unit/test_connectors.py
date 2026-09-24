"""Unit tests for cli/connectors/ — Debezium connector config builders."""
import pytest
from cli.connectors.postgres import config
from cli.connectors._common import common


@pytest.fixture(autouse=True)
def connector_env(monkeypatch):
    monkeypatch.setenv("CDC_TABLES", "public.customers,public.transactions")
    monkeypatch.setenv("TOPIC_PREFIX", "banking")
    monkeypatch.setenv("SNAPSHOT_MODE", "initial")
    monkeypatch.setenv("DB_HOST", "postgres")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "debezium")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_NAME", "banking")
    monkeypatch.setenv("DB_SSLMODE", "disable")
    monkeypatch.setenv("POSTGRES_PUBLICATION_NAME", "banking_pub")
    monkeypatch.setenv("POSTGRES_SLOT_NAME", "banking_slot")


class TestCommon:
    def test_decimal_handling_is_string(self):
        assert common()["decimal.handling.mode"] == "string"

    def test_tasks_max_is_one(self):
        assert common()["tasks.max"] == "1"

    def test_uses_topic_prefix_from_env(self):
        assert common()["topic.prefix"] == "banking"

    def test_uses_snapshot_mode_from_env(self):
        assert common()["snapshot.mode"] == "initial"

    def test_table_include_list_from_env(self):
        assert common()["table.include.list"] == "public.customers,public.transactions"


class TestPostgresConfig:
    def test_correct_connector_class(self):
        assert config()["connector.class"] == "io.debezium.connector.postgresql.PostgresConnector"

    def test_plugin_name_is_pgoutput(self):
        assert config()["plugin.name"] == "pgoutput"

    def test_publication_autocreate_disabled(self):
        assert config()["publication.autocreate.mode"] == "disabled"

    def test_slot_drop_on_stop_is_false(self):
        assert config()["slot.drop.on.stop"] == "false"

    def test_tombstones_on_delete_is_true(self):
        assert config()["tombstones.on.delete"] == "true"

    def test_errors_tolerance_is_all(self):
        assert config()["errors.tolerance"] == "all"

    def test_dlq_topic_uses_prefix(self):
        assert config()["errors.deadletterqueue.topic.name"] == "banking.dlq"

    def test_dlq_context_headers_enabled(self):
        assert config()["errors.deadletterqueue.context.headers.enable"] == "true"

    def test_heartbeat_interval_set(self):
        assert "heartbeat.interval.ms" in config()

    def test_uses_db_host_from_env(self):
        assert config()["database.hostname"] == "postgres"

    def test_uses_publication_name_from_env(self):
        assert config()["publication.name"] == "banking_pub"

    def test_uses_slot_name_from_env(self):
        assert config()["slot.name"] == "banking_slot"

    def test_config_is_dict(self):
        assert isinstance(config(), dict)

    def test_all_required_keys_present(self):
        c = config()
        required = [
            "connector.class", "database.hostname", "database.port",
            "database.user", "database.password", "database.dbname",
            "plugin.name", "publication.name", "slot.name",
        ]
        for key in required:
            assert key in c, f"Missing required key: {key}"
