from django.urls import reverse

from blog.models import Post


class PostPublishViewTests:
    def test_publish_draft_returns_published_post(self, client, user_factory, draft):
        client.force_login(user_factory())
        resp = client.post(reverse("post-publish", kwargs={"slug": draft.slug}))
        body = resp.json()

        assert resp.status_code == 200
        assert body["status"] == Post.Status.PUBLISHED
        assert body["published_at"] is not None
        assert body["deleted_at"] is None

    def test_publish_published_returns_409(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.post(reverse("post-publish", kwargs={"slug": published.slug}))

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "invalid_transition"

    def test_publish_deleted_returns_409(self, client, user_factory, deleted):
        client.force_login(user_factory())
        resp = client.post(reverse("post-publish", kwargs={"slug": deleted.slug}))
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "invalid_transition"

    def test_publish_unknown_slug_returns_404(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(reverse("post-publish", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_publish_unauthenticated_returns_401(self, client, draft):
        resp = client.post(reverse("post-publish", kwargs={"slug": draft.slug}))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"

    class PostUnpublishViewTests:
        def test_unpublish_published_returns_draft_and_retains_published_at(
            self, client, user_factory, published
        ):
            original = published.published_at.isoformat()
            client.force_login(user_factory())
            resp = client.post(
                reverse("post-unpublish", kwargs={"slug": published.slug})
            )
            body = resp.json()

            assert resp.status_code == 200
            assert body["status"] == Post.Status.DRAFT
            assert body["published_at"] == original

        def test_republish_retains_first_published_at(
            self, client, user_factory, published
        ):
            client.force_login(user_factory())
            original = published.published_at.isoformat()
            client.post(reverse("post-unpublish", kwargs={"slug": published.slug}))
            resp = client.post(reverse("post-publish", kwargs={"slug": published.slug}))
            assert resp.status_code == 200
            assert resp.json()["published_at"] == original

        def test_unpublish_deleted_returns_409(self, client, user_factory, deleted):
            client.force_login(user_factory())
            resp = client.post(reverse("post-unpublish", kwargs={"slug": deleted.slug}))
            assert resp.status_code == 409
            assert resp.json()["error"]["code"] == "invalid_transition"

        def test_unpublish_unknown_slug_returns_404(self, client, user_factory):
            client.force_login(user_factory())
            resp = client.post(reverse("post-unpublish", kwargs={"slug": "nope"}))
            assert resp.status_code == 404
            assert resp.json()["error"]["code"] == "not_found"

        def test_unpublish_unauthenticated_returns_401(self, client, published):
            resp = client.post(
                reverse("post-unpublish", kwargs={"slug": published.slug})
            )
            assert resp.status_code == 401
            assert resp.json()["error"]["code"] == "unauthenticated"


class PostDeleteViewTests:
    def test_delete_draft_soft_deletes(self, client, user_factory, draft):
        client.force_login(user_factory())
        resp = client.delete(reverse("post-detail", kwargs={"slug": draft.slug}))
        body = resp.json()

        assert resp.status_code == 200
        assert body["status"] == Post.Status.DELETED
        assert body["deleted_at"] is not None
        assert Post.objects.filter(pk=draft.pk).exists()

    def test_delete_published_soft_deletes(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.delete(reverse("post-detail", kwargs={"slug": published.slug}))
        body = resp.json()

        assert resp.status_code == 200
        assert body["status"] == Post.Status.DELETED
        assert body["deleted_at"] is not None
        assert Post.objects.filter(pk=published.pk).exists()

    def test_delete_deleted_returns_409(self, client, user_factory, deleted):
        client.force_login(user_factory())
        resp = client.delete(reverse("post-detail", kwargs={"slug": deleted.slug}))
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "invalid_transition"

    def test_delete_unknown_slug_returns_404(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.delete(reverse("post-detail", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_delete_unauthenticated_returns_401(self, client, draft):
        resp = client.delete(reverse("post-detail", kwargs={"slug": draft.slug}))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"


class PostRestoreViewTests:
    def test_restore_deleted_returns_draft_and_clears_deleted_at(
        self, client, user_factory, deleted
    ):
        client.force_login(user_factory())
        resp = client.post(reverse("post-restore", kwargs={"slug": deleted.slug}))
        body = resp.json()

        assert resp.status_code == 200
        assert body["status"] == Post.Status.DRAFT
        assert body["deleted_at"] is None

    def test_restore_draft_returns_409(self, client, user_factory, draft):
        client.force_login(user_factory())
        resp = client.post(reverse("post-restore", kwargs={"slug": draft.slug}))
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "invalid_transition"

    def test_restore_published_returns_409(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.post(reverse("post-restore", kwargs={"slug": published.slug}))
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "invalid_transition"

    def test_restore_unknown_slug_returns_404(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(reverse("post-restore", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_restore_unauthenticated_returns_401(self, client, deleted):
        resp = client.post(reverse("post-restore", kwargs={"slug": deleted.slug}))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"
