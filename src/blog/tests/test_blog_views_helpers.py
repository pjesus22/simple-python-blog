import json
from types import SimpleNamespace

import pytest

from blog.views.helpers import (
    collection,
    error_response,
    invalid_credentials,
    invalid_request,
    invalid_transition,
    missing_credentials,
    not_found,
    parse_json,
    resource,
    unauthenticated,
    validation_error,
)


def _req(content_type, body=b"{}"):
    return SimpleNamespace(content_type=content_type, body=body)


def _error(resp):
    return json.loads(resp.content)["error"]


class ResponseHelpersTests:
    def test_invalid_request_helper_returns_400(self):
        resp = invalid_request()
        assert resp.status_code == 400
        assert _error(resp) == {
            "code": "invalid_request",
            "message": "The request is invalid.",
        }

    def test_missing_credentials_helper_returns_400(self):
        resp = missing_credentials()
        assert resp.status_code == 400
        assert _error(resp) == {
            "code": "missing_credentials",
            "message": "Username and password are required.",
        }

    def test_invalid_credentials_helper_returns_400(self):
        resp = invalid_credentials()
        assert resp.status_code == 401
        assert _error(resp) == {
            "code": "invalid_credentials",
            "message": "Invalid username or password.",
        }

    def test_unauthenticated_helper_returns_401(self):
        resp = unauthenticated()
        assert resp.status_code == 401
        assert _error(resp) == {
            "code": "unauthenticated",
            "message": "Authentication required.",
        }

    def test_response_with_fields_includes_fields_keys(self):
        resp = error_response("code", "msg", 400, {"username": "required"})
        assert _error(resp)["fields"] == {"username": "required"}

    def test_response_without_fields_omits_fields_keys(self):
        resp = error_response("code", "msg", 400)
        assert "fields" not in _error(resp)

    def test_validation_error_helper_returns_400(self):
        resp = validation_error({"title": ["This field is required."]})
        assert resp.status_code == 400
        assert _error(resp) == {
            "code": "validation_error",
            "message": "One or more fields are invalid.",
            "fields": {"title": ["This field is required."]},
        }

    def test_not_found_helper_returns_404(self):
        resp = not_found()
        assert resp.status_code == 404
        assert _error(resp) == {"code": "not_found", "message": "Resource not found."}

    def test_invalid_transition_helper_returns_409(self):
        resp = invalid_transition()
        assert resp.status_code == 409
        assert _error(resp) == {
            "code": "invalid_transition",
            "message": "The requested transition is not allowed.",
        }

    def test_resource_default_status_returns_200(self):
        resp = resource({"id": 1})
        assert resp.status_code == 200
        assert json.loads(resp.content) == {"id": 1}

    def test_resource_custom_status_returns_given_status(self):
        resp = resource({"id": 1}, status=201)
        assert resp.status_code == 201

    def test_collection_helper_returns_200_with_items(self):
        resp = collection([{"id": 1}], {"page": 1, "total": 1})
        assert resp.status_code == 200
        assert json.loads(resp.content) == {
            "items": [{"id": 1}],
            "pagination": {"page": 1, "total": 1},
        }


class ParseJsonTests:
    def test_parse_json_non_json_content_type_returns_none(self):
        req = _req("text/plain", b'{"a":1}')
        assert parse_json(req) is None

    def test_parse_json_valid_body_returns_dict(self):
        req = _req("application/json", b'{"a":1}')
        assert parse_json(req) == {"a": 1}

    def test_parse_json_empty_body_returns_empty_dict(self):
        req = _req("application/json", b"")
        assert parse_json(req) == {}

    def test_parse_json_malformed_body_returns_none(self):
        req = _req("application/json", b"{nope")
        assert parse_json(req) is None

    def test_parse_json_non_utf8_body_returns_none(self):
        req = _req("application/json", b"\xff")
        assert parse_json(req) is None

    @pytest.mark.parametrize("body", [b"[]", b"5", b"null", b'"x"'])
    def test_parse_json_non_object_body_returns_none(self, body):
        assert parse_json(_req("application/json", body)) is None
