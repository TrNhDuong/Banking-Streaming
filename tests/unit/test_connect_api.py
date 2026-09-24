"""Unit tests for cli/connect_api.py — Kafka Connect REST client."""
import json
import pytest
from io import BytesIO
from unittest.mock import MagicMock
from urllib.error import HTTPError

from cli.connect_api import call, apply, status, delete


def _make_urlopen_response(status_code: int, body=None):
    """Build a mock context-manager response for request.urlopen."""
    raw = json.dumps(body).encode() if body is not None else b""
    mock = MagicMock()
    mock.status = status_code
    mock.read.return_value = raw
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


@pytest.fixture(autouse=True)
def connect_env(monkeypatch):
    monkeypatch.setenv("CONNECT_REST_URL", "http://localhost:8083")
    monkeypatch.setenv("CONNECTOR_NAME", "banking-cdc")
    monkeypatch.setenv("CDC_TABLES", "public.transactions")
    monkeypatch.setenv("TOPIC_PREFIX", "banking")
    monkeypatch.setenv("DB_HOST", "postgres")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "debezium")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_NAME", "banking")
    monkeypatch.setenv("DB_SSLMODE", "disable")
    monkeypatch.setenv("POSTGRES_PUBLICATION_NAME", "banking_pub")
    monkeypatch.setenv("POSTGRES_SLOT_NAME", "banking_slot")
    monkeypatch.setenv("SNAPSHOT_MODE", "initial")


class TestCall:
    def test_returns_status_and_parsed_json(self, monkeypatch):
        mock_urlopen = MagicMock(return_value=_make_urlopen_response(200, {"name": "test"}))
        monkeypatch.setattr("cli.connect_api.request.urlopen", mock_urlopen)
        code, body = call("GET", "http://localhost:8083/connectors/test")
        assert code == 200
        assert body == {"name": "test"}

    def test_returns_none_body_for_empty_response(self, monkeypatch):
        mock_urlopen = MagicMock(return_value=_make_urlopen_response(204, None))
        monkeypatch.setattr("cli.connect_api.request.urlopen", mock_urlopen)
        code, body = call("DELETE", "http://localhost:8083/connectors/test")
        assert code == 204
        assert body is None

    def test_handles_http_error_404(self, monkeypatch):
        error = HTTPError(
            url="http://localhost:8083/connectors/missing",
            code=404, msg="Not Found", hdrs={},
            fp=BytesIO(b'{"error_code":404,"message":"not found"}'),
        )
        monkeypatch.setattr("cli.connect_api.request.urlopen", MagicMock(side_effect=error))
        code, body = call("GET", "http://localhost:8083/connectors/missing")
        assert code == 404

    def test_handles_http_error_500(self, monkeypatch):
        error = HTTPError(
            url="http://x", code=500, msg="Server Error", hdrs={},
            fp=BytesIO(b'{"error": "internal"}'),
        )
        monkeypatch.setattr("cli.connect_api.request.urlopen", MagicMock(side_effect=error))
        code, body = call("GET", "http://x")
        assert code == 500


class TestApply:
    def test_apply_succeeds_on_200(self, monkeypatch, capsys):
        mock_call = MagicMock(return_value=(200, {"name": "banking-cdc"}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        apply()  # should not raise
        assert mock_call.called

    def test_apply_succeeds_on_201(self, monkeypatch):
        mock_call = MagicMock(return_value=(201, {"name": "banking-cdc"}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        apply()  # should not raise

    def test_apply_raises_system_exit_on_error(self, monkeypatch):
        mock_call = MagicMock(return_value=(500, {"error": "server error"}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        with pytest.raises(SystemExit, match="500"):
            apply()

    def test_apply_calls_put_method(self, monkeypatch):
        mock_call = MagicMock(return_value=(200, {}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        apply()
        method = mock_call.call_args[0][0]
        assert method == "PUT"

    def test_apply_url_contains_connector_name(self, monkeypatch):
        mock_call = MagicMock(return_value=(200, {}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        apply()
        url = mock_call.call_args[0][1]
        assert "banking-cdc" in url
        assert "/config" in url


class TestStatus:
    def test_status_succeeds_on_200(self, monkeypatch):
        mock_call = MagicMock(return_value=(200, {"connector": {"state": "RUNNING"}}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        status()  # should not raise

    def test_status_raises_on_non_200(self, monkeypatch):
        mock_call = MagicMock(return_value=(404, None))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        with pytest.raises(SystemExit, match="404"):
            status()

    def test_status_calls_get_method(self, monkeypatch):
        mock_call = MagicMock(return_value=(200, {}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        status()
        assert mock_call.call_args[0][0] == "GET"


class TestDelete:
    def test_delete_succeeds_on_204(self, monkeypatch):
        mock_call = MagicMock(return_value=(204, None))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        delete()  # should not raise

    def test_delete_succeeds_on_404_already_gone(self, monkeypatch):
        """Deleting a connector that doesn't exist should not raise."""
        mock_call = MagicMock(return_value=(404, None))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        delete()  # should not raise

    def test_delete_raises_on_unexpected_error(self, monkeypatch):
        mock_call = MagicMock(return_value=(500, {"error": "server error"}))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        with pytest.raises(SystemExit, match="500"):
            delete()

    def test_delete_calls_delete_method(self, monkeypatch):
        mock_call = MagicMock(return_value=(204, None))
        monkeypatch.setattr("cli.connect_api.call", mock_call)
        delete()
        assert mock_call.call_args[0][0] == "DELETE"
