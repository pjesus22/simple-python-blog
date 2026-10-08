import json
from typing import cast

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from django.urls import reverse


@pytest.fixture
def user(db):
    manager = cast(UserManager, get_user_model().objects)
    return manager.create_user(username="jhonny", password="test")  # noqa: S106


def _login(client, **body):
    return client.post(
        reverse("login"), data=json.dumps(body), content_type="application/json"
    )


class TestLoginView:
    def test_non_json_content_type_returns_invalid_request(self, client):
        resp = client.post(reverse("login"))
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_missing_username_returns_missing_credentials(self, client):
        resp = _login(client, password="secret")  # noqa: S106
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "missing_credentials"

    def test_missing_password_returns_missing_credentials(self, client):
        resp = _login(client, username="jhonny")
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "missing_credentials"

    def test_wrong_password_returns_invalid_credentials(self, client, user):
        resp = _login(client, username="jhonny", password="wrong")  # noqa: S106
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "invalid_credentials"

    def test_successful_login_returns_user_id(self, client, user):
        resp = _login(client, username="jhonny", password="test")  # noqa: S106
        assert resp.status_code == 200
        assert resp.json() == {"id": user.pk, "username": "jhonny"}
        assert client.session["_auth_user_id"] == str(user.pk)


class TestLogoutView:
    def test_unauthenticated_returns_unauthenticated(self, client):
        resp = client.post(reverse("logout"))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"

    def test_authenticated_logout_return_204(self, client, user):
        client.force_login(user)
        resp = client.post(reverse("logout"))
        assert resp.status_code == 204
        assert resp.content == b""
        assert "_auth_user_id" not in client.session
