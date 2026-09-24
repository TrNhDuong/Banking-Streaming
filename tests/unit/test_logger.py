"""Unit tests for cli/logger.py — CLI logging infrastructure."""
import logging
import os
import tempfile
import pytest

from cli.logger import setup_cli_logging, get_logger, CliFormatter


class TestCliFormatter:
    def test_formats_info_record(self):
        formatter = CliFormatter()
        record = logging.LogRecord(
            name="cli.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Hello %s",
            args=("world",),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "[INFO]" in output
        assert "Hello world" in output

    def test_formats_warn_record(self):
        formatter = CliFormatter()
        record = logging.LogRecord(
            name="cli.test",
            level=logging.WARNING,
            pathname=__file__,
            lineno=10,
            msg="Warning message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "[WARN]" in output
        assert "Warning message" in output

    def test_formats_error_record(self):
        formatter = CliFormatter()
        record = logging.LogRecord(
            name="cli.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "[ERROR]" in output
        assert "Error occurred" in output

    def test_formats_debug_record(self):
        formatter = CliFormatter()
        record = logging.LogRecord(
            name="cli.test",
            level=logging.DEBUG,
            pathname=__file__,
            lineno=10,
            msg="Debug trace",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "[DEBUG]" in output
        assert "Debug trace" in output


class TestSetupCliLogging:
    def test_default_level_is_info(self, monkeypatch):
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        logger = setup_cli_logging(verbose=False)
        assert logger.level == logging.INFO

    def test_verbose_sets_debug_level(self, monkeypatch):
        logger = setup_cli_logging(verbose=True)
        assert logger.level == logging.DEBUG

    def test_env_var_overrides_level(self, monkeypatch):
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        logger = setup_cli_logging(verbose=False)
        assert logger.level == logging.WARNING

    def test_file_logging(self, tmp_path):
        log_file = tmp_path / "test_cli.log"
        logger = setup_cli_logging(verbose=True, log_file=str(log_file))
        logger.info("Test message to file")
        # Flush handlers
        for handler in logger.handlers:
            handler.flush()
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test message to file" in content


class TestGetLogger:
    def test_returns_namespaced_logger(self):
        log = get_logger("commands")
        assert log.name == "cli.commands"

    def test_preserves_cli_prefix(self):
        log = get_logger("cli.compose")
        assert log.name == "cli.compose"

    def test_base_cli_logger(self):
        log = get_logger("cli")
        assert log.name == "cli"
