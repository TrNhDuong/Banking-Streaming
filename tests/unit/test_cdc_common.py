"""Unit tests for cli/cdc/_common.py — tables() parser."""
import pytest
from cli.cdc._common import tables


class TestTables:
    def test_schema_dot_table_format(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "public.customers,public.accounts")
        assert tables() == [("public", "customers"), ("public", "accounts")]

    def test_bare_table_name_defaults_to_public_schema(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "customers,accounts")
        assert tables() == [("public", "customers"), ("public", "accounts")]

    def test_mixed_format(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "public.customers,transactions")
        assert tables() == [("public", "customers"), ("public", "transactions")]

    def test_strips_whitespace_around_entries(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", " public.customers , public.accounts ")
        assert tables() == [("public", "customers"), ("public", "accounts")]

    def test_skips_empty_entries_from_trailing_comma(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "public.customers,,public.accounts,")
        assert tables() == [("public", "customers"), ("public", "accounts")]

    def test_single_table(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "public.transactions")
        assert tables() == [("public", "transactions")]

    def test_raises_when_cdc_tables_not_set(self):
        with pytest.raises(RuntimeError, match="CDC_TABLES"):
            tables()

    def test_custom_schema(self, monkeypatch):
        monkeypatch.setenv("CDC_TABLES", "banking.transactions")
        assert tables() == [("banking", "transactions")]
