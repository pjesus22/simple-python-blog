from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from blog.models import Post


class PostLifecycleTests:
    def test_full_lifecycle_flow(self, authenticated_api, transactional_db):
        api = authenticated_api

        status, category = api.post(
            reverse("category-list"),
            body={
                "name": "Lifecycle Category",
                "description": "Created over HTTP.",
            },
        )
        assert status == 201

        status, body = api.post(
            reverse("post-list"),
            body={
                "title": "Lifecycle Post",
                "summary": "Lifecycle over HTTP.",
                "content": "Lifecycle body over HTTP.",
                "category": category["id"],
            },
        )
        assert status == 201
        assert body["status"] == Post.Status.DRAFT
        slug = body["slug"]

        status, body = api.post(reverse("post-publish", kwargs={"slug": slug}))
        assert status == 200
        assert body["status"] == Post.Status.PUBLISHED
        assert body["published_at"] is not None
        published_at = body["published_at"]

        status, body = api.post(reverse("post-unpublish", kwargs={"slug": slug}))
        assert status == 200
        assert body["status"] == Post.Status.DRAFT
        assert body["published_at"] == published_at

        status, body = api.delete(reverse("post-detail", kwargs={"slug": slug}))
        assert status == 200
        assert body["status"] == Post.Status.DELETED
        assert body["deleted_at"] is not None

        status, body = api.post(reverse("post-restore", kwargs={"slug": slug}))
        assert status == 200
        assert body["status"] == Post.Status.DRAFT
        assert body["deleted_at"] is None

        status, body = api.delete(reverse("post-detail", kwargs={"slug": slug}))
        assert status == 200
        assert body["status"] == Post.Status.DELETED

        Post.objects.filter(slug=slug).update(
            deleted_at=timezone.now() - timedelta(days=31)
        )

        out = StringIO()
        call_command("purge_deleted_posts", "--dry-run", stdout=out)
        assert slug in out.getvalue()
        assert Post.objects.filter(slug=slug).exists()

        call_command("purge_deleted_posts", stdout=out)
        assert not Post.objects.filter(slug=slug).exists()

        status, _ = api.get(reverse("post-detail", kwargs={"slug": slug}))
        assert status == 404


class PostLifecycleAccessTests:
    def test_anonymous_cannot_run_lifecycle_operations_or_list_deleted(
        self, authenticated_api, admin_credentials
    ):
        api = authenticated_api

        status, body = api.post(
            reverse("post-list"),
            body={
                "title": "Anonymous Lifecycle Post",
                "summary": "Access over HTTP.",
                "content": "Access body over HTTP.",
            },
        )
        assert status == 201
        slug = body["slug"]

        status, _ = api.post(reverse("logout"))
        assert status == 204

        for status, body in (
            api.post(reverse("post-publish", kwargs={"slug": slug})),
            api.post(reverse("post-unpublish", kwargs={"slug": slug})),
            api.delete(reverse("post-detail", kwargs={"slug": slug})),
            api.post(reverse("post-restore", kwargs={"slug": slug})),
        ):
            assert status == 401
            assert body["error"]["code"] == "unauthenticated"

        status, _ = api.post(reverse("login"), body=admin_credentials)
        assert status == 200

        status, _ = api.post(reverse("post-publish", kwargs={"slug": slug}))
        assert status == 200

        status, _ = api.delete(reverse("post-detail", kwargs={"slug": slug}))
        assert status == 200

        status, _ = api.post(reverse("logout"))
        assert status == 204

        status, body = api.get(reverse("post-list"))
        assert status == 200
        assert slug not in [item["slug"] for item in body["items"]]

        status, body = api.get(reverse("post-detail", kwargs={"slug": slug}))
        assert status == 404
        assert body["error"]["code"] == "not_found"

        status, body = api.get(f"{reverse('post-list')}?status={Post.Status.DELETED}")
        assert status == 403
        assert body["error"]["code"] == "forbidden"
