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


def test_format_info_record_returns_json_fields():
    data = json.loads(JsonFormatter().format(_record()))

    assert data["level"] == "INFO"
    assert data["message"] == "hello"
    assert data["logger"] == "app"
    assert {"timestamp", "module", "line"} <= data.keys()


def test_format_exc_info_present_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = _record(level=logging.ERROR, exc_info=sys.exc_info())
    data = json.loads(JsonFormatter().format(record))

    assert "exception" in data


def test_format_no_exc_info_omits_exception():
    data = json.loads(JsonFormatter().format(_record()))
    assert "exception" not in data
