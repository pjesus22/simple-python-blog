from django.urls import reverse


class AuthFlowTests:
    def test_login_and_logout_flow(self, api, admin_user, admin_credentials):
        status, body = api.post(reverse("login"), body=admin_credentials)
        assert status == 200
        assert set(body) == {"id", "username"}
        assert body["username"] == admin_credentials["username"]

        status, body = api.post(reverse("logout"))
        assert status == 204
        assert body is None

        status, body = api.post(
            reverse("post-list"),
            body={
                "title": "After Logout",
                "summary": "Rejected over HTTP.",
                "content": "Rejected over HTTP.",
            },
        )
        assert status == 401
        assert body["error"]["code"] == "unauthenticated"

    def test_anonymous_writes_are_rejected(self, api):
        status, body = api.post(
            reverse("post-list"),
            body={
                "title": "Anonymous Post",
                "summary": "Rejected over HTTP.",
                "content": "Rejected over HTTP.",
            },
        )
        assert status == 401
        assert body["error"]["code"] == "unauthenticated"

        status, body = api.post(reverse("category-list"), body={"name": "Anon"})
        assert status == 401
        assert body["error"]["code"] == "unauthenticated"

        status, body = api.patch(
            reverse("post-detail", kwargs={"slug": "nope"}),
            body={"summary": "Rejected over HTTP."},
        )
        assert status == 401
        assert body["error"]["code"] == "unauthenticated"

        status, body = api.delete(reverse("category-detail", kwargs={"slug": "nope"}))
        assert status == 401
        assert body["error"]["code"] == "unauthenticated"
