"""Unit tests for cli/env.py"""
import pytest
from cli.env import env


class TestEnv:
    def test_returns_value_when_set(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "localhost")
        assert env("DB_HOST") == "localhost"

    def test_returns_default_when_not_set(self):
        assert env("DB_HOST", "postgres") == "postgres"

    def test_returns_none_when_not_set_and_no_default(self):
        assert env("DB_HOST") is None

    def test_zero_string_is_not_coerced_to_empty(self, monkeypatch):
        """Regression: old code did `return value or ""` which coerced "0" to "0" (fine)
        but None to "" (wrong). Ensure None stays None."""
        assert env("DB_HOST") is None

    def test_false_string_returned_as_is(self, monkeypatch):
        monkeypatch.setenv("GENERATOR_ENABLED", "false")
        assert env("GENERATOR_ENABLED") == "false"

    def test_required_raises_when_not_set(self):
        with pytest.raises(RuntimeError, match="Missing environment variable: DB_HOST"):
            env("DB_HOST", required=True)

    def test_required_raises_when_empty_string(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "")
        with pytest.raises(RuntimeError, match="Missing environment variable: DB_HOST"):
            env("DB_HOST", required=True)

    def test_required_does_not_raise_when_set(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "postgres")
        assert env("DB_HOST", required=True) == "postgres"

    def test_default_not_used_when_var_is_set(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "myserver")
        assert env("DB_HOST", "postgres") == "myserver"
