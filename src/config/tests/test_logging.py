import json
import logging
import sys

from config.logging import JsonFormatter


def _record(level=logging.INFO, msg="hello", exc_info=None):
    return logging.LogRecord(
        name="app",
        level=level,
        pathname="src/app.py",
        lineno=42,
        msg=msg,
        args=(),
        exc_info=exc_info,
    )


def test_format_returns_json_with_expected_fields():
    data = json.loads(JsonFormatter().format(_record()))

    assert data["level"] == "INFO"
    assert data["message"] == "hello"
    assert data["logger"] == "app"
    assert {"timestamp", "module", "line"} <= data.keys()


def test_format_includes_exception_when_exc_info_present():
    try:
        raise ValueError("boom")
    except ValueError:
        record = _record(level=logging.ERROR, exc_info=sys.exc_info())
    data = json.loads(JsonFormatter().format(record))

    assert "exception" in data


def test_format_omits_exception_when_no_exc_info():
    data = json.loads(JsonFormatter().format(_record()))
    assert "exception" not in data
