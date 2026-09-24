"""Unit tests for cli/cdc/postgres.py — SQL generation and docker exec calls."""
import pytest
from unittest.mock import MagicMock, call
from cli.cdc.postgres import sql, setup, verify


@pytest.fixture(autouse=True)
def postgres_env(monkeypatch):
    monkeypatch.setenv("CDC_TABLES", "public.customers,public.transactions")
    monkeypatch.setenv("DB_USER", "debezium")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_PUBLICATION_NAME", "banking_pub")
    monkeypatch.setenv("DB_NAME", "banking")
    monkeypatch.setenv("POSTGRES_ADMIN_USER", "bank_admin")


class TestSql:
    def test_contains_publication_name(self):
        assert "banking_pub" in sql()

    def test_creates_or_alters_debezium_role(self):
        result = sql()
        assert "CREATE ROLE" in result or "ALTER ROLE" in result
        assert "debezium" in result

    def test_grants_replication(self):
        assert "REPLICATION" in sql()

    def test_creates_publication_for_tables(self):
        result = sql()
        assert "CREATE PUBLICATION" in result
        assert '"public"."customers"' in result
        assert '"public"."transactions"' in result

    def test_publication_uses_correct_name(self):
        assert 'CREATE PUBLICATION "banking_pub"' in sql()

    def test_grants_connect_on_db(self):
        assert 'GRANT CONNECT ON DATABASE "banking"' in sql()

    def test_grants_select_on_tables(self):
        assert "GRANT SELECT ON ALL TABLES" in sql()

    def test_drops_existing_publication_first(self):
        result = sql()
        drop_pos = result.index("DROP PUBLICATION")
        create_pos = result.index("CREATE PUBLICATION")
        assert drop_pos < create_pos, "DROP must come before CREATE"

    def test_uses_env_db_name(self, monkeypatch):
        monkeypatch.setenv("DB_NAME", "mydb")
        assert "mydb" in sql()

    def test_uses_env_db_user(self, monkeypatch):
        monkeypatch.setenv("DB_USER", "custom_user")
        assert "custom_user" in sql()


class TestSetup:
    def test_calls_docker_exec_psql(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        setup()
        args = mock_run.call_args[0][0]
        assert "docker" in args
        assert "exec" in args
        assert "banking-postgres" in args
        assert "psql" in args

    def test_passes_generated_sql_as_input(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        setup()
        _, kwargs = mock_run.call_args
        assert kwargs["input_text"] == sql()

    def test_uses_admin_user(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        setup()
        args = mock_run.call_args[0][0]
        assert "bank_admin" in args

    def test_uses_on_error_stop(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        setup()
        args = mock_run.call_args[0][0]
        assert "ON_ERROR_STOP=1" in args


class TestVerify:
    def test_calls_docker_exec_psql(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        verify()
        args = mock_run.call_args[0][0]
        assert "docker" in args
        assert "exec" in args
        assert "banking-postgres" in args

    def test_checks_wal_level(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        verify()
        _, kwargs = mock_run.call_args
        assert "wal_level" in kwargs["input_text"]

    def test_checks_publications(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        verify()
        _, kwargs = mock_run.call_args
        assert "pg_publication" in kwargs["input_text"]

    def test_checks_replication_slots(self, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("cli.cdc.postgres.run", mock_run)
        verify()
        _, kwargs = mock_run.call_args
        assert "pg_replication_slots" in kwargs["input_text"]
