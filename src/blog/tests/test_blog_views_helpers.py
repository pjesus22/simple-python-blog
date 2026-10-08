import json
from types import SimpleNamespace

from blog.views.helpers import (
    _response,
    invalid_credentials,
    invalid_request,
    missing_credentials,
    parse_json,
    unauthenticated,
)


def _req(content_type, body=b"{}"):
    return SimpleNamespace(content_type=content_type, body=body)


def _error(resp):
    return json.loads(resp.content)["error"]


class TestResponseHelpers:
    def test_invalid_request(self):
        resp = invalid_request()
        assert resp.status_code == 400
        assert _error(resp) == {
            "code": "invalid_request",
            "message": "The request is invalid.",
        }

    def test_missing_credentials(self):
        resp = missing_credentials()
        assert resp.status_code == 400
        assert _error(resp) == {
            "code": "missing_credentials",
            "message": "Username and password are required.",
        }

    def test_invalid_credentials(self):
        resp = invalid_credentials()
        assert resp.status_code == 401
        assert _error(resp) == {
            "code": "invalid_credentials",
            "message": "Invalid username or password.",
        }

    def test_unauthenticated(self):
        resp = unauthenticated()
        assert resp.status_code == 401
        assert _error(resp) == {
            "code": "unauthenticated",
            "message": "Authentication required.",
        }

    def test_fields_included_when_present(self):
        resp = _response("code", "msg", 400, {"username": "required"})
        assert _error(resp)["fields"] == {"username": "required"}

    def test_fields_ommited_when_absent(self):
        resp = _response("code", "msg", 400)
        assert "fields" not in _error(resp)


class TestParseJson:
    def test_non_json_content_type_returns_none(self):
        req = _req("text/plain", b'{"a":1}')
        assert parse_json(req) is None

    def test_valid_json_returns_dict(self):
        req = _req("application/json", b'{"a":1}')
        assert parse_json(req) == {"a": 1}

    def test_empty_body_returns_empty_dict(self):
        req = _req("application/json", b"")
        assert parse_json(req) == {}

    def test_malformed_json_returns_none(self):
        req = _req("application/json", b"{nope")
        assert parse_json(req) is None

    def test_non_utf8_returns_none(self):
        req = _req("application/json", b"\xff")
        assert parse_json(req) is None
