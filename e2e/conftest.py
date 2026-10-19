import json
from http.cookiejar import CookieJar
from typing import cast
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from django.urls import reverse


class ApiClient:
    def __init__(self, base_url: str) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError(f"unsupported scheme: {base_url}")
        self.base_url = base_url.rstrip("/")
        self._opener = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))

    @staticmethod
    def _decode(raw: bytes):
        return json.loads(raw) if raw else None

    def request(self, method: str, path: str, body: dict | None = None):
        data = None if body is None else json.dumps(body).encode()
        headers = {"Content-Type": "application/json"} if data is not None else {}
        request = Request(  # noqa: S310
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )
        try:
            with self._opener.open(request) as response:
                return response.status, self._decode(response.read())
        except HTTPError as exc:
            return exc.code, self._decode(exc.read())

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("DELETE", path, **kwargs)


@pytest.fixture
def admin_credentials():
    return {"username": "admin", "password": "test"}


@pytest.fixture
def admin_user(transactional_db, admin_credentials):
    manager = cast(UserManager, get_user_model().objects)
    return manager.create_user(**admin_credentials)


@pytest.fixture
def api(live_server):
    return ApiClient(live_server.url)


@pytest.fixture
def authenticated_api(api, admin_user, admin_credentials):
    status, _ = api.post(reverse("login"), body=admin_credentials)
    assert status == 200
    return api
