import json
from types import SimpleNamespace

import pytest
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.test import Client, override_settings

from config import errors, urls


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/api/", True),
        ("/api/v1/posts", True),
        ("/apiary/", False),
        ("/api", False),
        ("/admin/", False),
    ],
)
def test_is_api_request(path, expected):
    assert errors.is_api_request(SimpleNamespace(path_info=path)) is expected


def test_handlers_are_registered():
    assert urls.handler400 is errors.handler400
    assert urls.handler403 is errors.handler403
    assert urls.handler404 is errors.handler404
    assert urls.handler500 is errors.handler500


def test_handler400_api(rf):
    resp = errors.handler400(rf.get("/api/v1/x"), SuspiciousOperation("bad"))
    assert resp.status_code == 400
    assert resp["Content-Type"] == "application/json"
    assert json.loads(resp.content)["error"]["code"] == "invalid_request"


def test_handler403_api(rf):
    resp = errors.handler403(rf.get("/api/v1/x"), PermissionDenied())
    assert resp.status_code == 403
    assert json.loads(resp.content)["error"]["code"] == "forbidden"


def test_handler404_api(rf):
    resp = errors.handler404(rf.get("/api/v1/x"), Http404())
    assert resp.status_code == 404
    assert json.loads(resp.content)["error"]["code"] == "not_found"


def test_handler500_api(rf):
    resp = errors.handler500(rf.get("/api/v1/x"))
    assert resp.status_code == 500
    assert json.loads(resp.content) == {
        "error": {"code": "internal_error", "message": "An unexpected error occurred."}
    }


def test_handler400_non_api_delegates(rf):
    resp = errors.handler400(rf.get("/nope"), SuspiciousOperation("bad"))
    assert resp.status_code == 400
    assert resp["Content-Type"].startswith("text/html")


def test_handler403_non_api_delegates(rf):
    resp = errors.handler403(rf.get("/nope"), PermissionDenied())
    assert resp.status_code == 403
    assert resp["Content-Type"].startswith("text/html")


def test_handler404_non_api_delegates(rf):
    resp = errors.handler404(rf.get("/nope"), Http404())
    assert resp.status_code == 404
    assert resp["Content-Type"].startswith("text/html")


def test_handler500_non_api_delegates(rf):
    resp = errors.handler500(rf.get("/nope"))
    assert resp.status_code == 500
    assert resp["Content-Type"].startswith("text/html")


@override_settings(DEBUG=False)
def test_api_unmatched_url_returns_json_404(client):
    resp = client.get("/api/v1/does-not-exist")
    assert resp.status_code == 404
    assert resp["Content-Type"] == "application/json"
    assert resp.json()["error"]["code"] == "not_found"


@override_settings(DEBUG=False)
def test_non_api_404_remains_html(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert resp["Content-Type"].startswith("text/html")


@override_settings(DEBUG=False)
def test_detail_view_http404_returns_json_404(client, db):
    resp = client.get("/api/v1/posts/does-not-exist")
    assert resp.status_code == 404
    assert resp["Content-Type"] == "application/json"
    assert resp.json()["error"]["code"] == "not_found"


@override_settings(DEBUG=False)
def test_successful_api_response_unchanged(client, db):
    resp = client.get("/api/v1/posts")
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/json"
    assert "items" in resp.json()


@override_settings(ROOT_URLCONF="config.tests.error_urls", DEBUG=False)
def test_suspicious_operation_returns_json_400(client):
    resp = client.get("/api/v1/_suspicious")
    assert resp.status_code == 400
    assert resp["Content-Type"] == "application/json"
    assert resp.json()["error"]["code"] == "invalid_request"


@override_settings(ROOT_URLCONF="config.tests.error_urls", DEBUG=False)
def test_permission_denied_returns_json_403(client):
    resp = client.get("/api/v1/_denied")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "forbidden"


@override_settings(
    ROOT_URLCONF="config.tests.error_urls",
    DEBUG=False,
    DEBUG_PROPAGATE_EXCEPTIONS=False,
)
def test_unexpected_exception_returns_json_500():
    client = Client(raise_request_exception=False)
    resp = client.get("/api/v1/_boom")
    assert resp.status_code == 500
    assert resp["Content-Type"] == "application/json"
    assert resp.json() == {
        "error": {"code": "internal_error", "message": "An unexpected error occurred."}
    }
    assert "SECRET_SENTINEL_123" not in resp.content.decode()


@override_settings(
    ROOT_URLCONF="config.tests.error_urls",
    DEBUG=False,
    DEBUG_PROPAGATE_EXCEPTIONS=False,
)
def test_non_api_unexpected_exception_remains_html():
    client = Client(raise_request_exception=False)
    resp = client.get("/_boom")
    assert resp.status_code == 500
    assert resp["Content-Type"].startswith("text/html")


@override_settings(DEBUG=False, DATA_UPLOAD_MAX_MEMORY_SIZE=10)
def test_oversized_request_returns_json_400(client):
    resp = client.post(
        "/api/v1/auth/login", data="x" * 100, content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "error": {"code": "invalid_request", "message": "The request is invalid."}
    }


@override_settings(DEBUG=False)
def test_api_method_not_allowed_returns_json_405(client):
    resp = client.delete("/api/v1/posts/anything")
    assert resp.status_code == 405
    assert resp["Content-Type"] == "application/json"
    assert resp.json()["error"]["code"] == "method_not_allowed"
    assert "DELETE" not in resp["Allow"]
    assert "GET" in resp["Allow"]
