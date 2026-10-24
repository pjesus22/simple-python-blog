import pytest
from django.urls import reverse


def _login(client, **body):
    return client.post(reverse("login"), data=body, content_type="application/json")


class LoginViewTests:
    def test_login_non_json_content_type_returns_400(self, client):
        resp = client.post(reverse("login"))
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_login_missing_username_returns_400(self, client):
        resp = _login(client, password="secret")  # noqa: S106
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "missing_credentials"

    def test_login_missing_password_returns_400(self, client):
        resp = _login(client, username="jhonny")
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "missing_credentials"

    def test_login_wrong_password_returns_401(self, client, user_factory):
        user_factory()
        resp = _login(client, username="jhonny", password="wrong")  # noqa: S106
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "invalid_credentials"

    def test_login_valid_credentials_returns_200(self, client, user_factory):
        user = user_factory("jhonny", "test")
        resp = _login(client, username="jhonny", password="test")  # noqa: S106
        assert resp.status_code == 200
        assert resp.json() == {"id": user.pk, "username": "jhonny"}
        assert client.session["_auth_user_id"] == str(user.pk)

    @pytest.mark.parametrize("payload", ["{nope", ["[]"]])
    def test_login_invalid_json_returns_400(self, client, payload):
        resp = client.post(
            reverse("login"),
            data=payload,
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"


class LogoutViewTests:
    def test_logout_anonymous_returns_401(self, client):
        resp = client.post(reverse("logout"))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"

    def test_logout_authenticated_returns_204(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(reverse("logout"))
        assert resp.status_code == 204
        assert resp.content == b""
        assert "_auth_user_id" not in client.session
