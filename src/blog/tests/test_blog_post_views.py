import pytest
from django.urls import reverse

from blog.models import Post


class PostListViewTests:
    def test_list_mixed_statuses_returns_only_published(
        self, client, draft, published, deleted
    ):
        resp = client.get(reverse("post-list"))
        expected_slugs = [item["slug"] for item in resp.json()["items"]]

        assert resp.status_code == 200
        assert published.slug in expected_slugs
        assert draft.slug not in expected_slugs
        assert deleted.slug not in expected_slugs

    def test_list_empty_database_returns_empty_items(self, client, db):
        resp = client.get(reverse("post-list"))
        expected = {
            "items": [],
            "pagination": {"page": 1, "page_size": 20, "total": 0, "total_pages": 1},
        }
        assert resp.json() == expected

    def test_list_filter_by_category_returns_matching_posts(self, client, post_factory):
        first = post_factory("First Post", Post.Status.PUBLISHED)
        post_factory("Second Post", Post.Status.PUBLISHED)
        resp = client.get(reverse("post-list"), {"category": first.category.slug})
        assert [item["slug"] for item in resp.json()["items"]] == [first.slug]

    def test_list_more_than_page_size_returns_paginated_results(
        self, client, post_factory
    ):
        for _ in range(21):
            post_factory(status=Post.Status.PUBLISHED)
        body = client.get(reverse("post-list")).json()
        assert body["pagination"] == {
            "page": 1,
            "page_size": 20,
            "total": 21,
            "total_pages": 2,
        }
        assert len(body["items"]) == 20


class PostRetrieveViewTests:
    def test_retrieve_published_post_returns_200(self, client, published):
        resp = client.get(reverse("post-detail", kwargs={"slug": published.slug}))
        body = resp.json()

        assert resp.status_code == 200
        assert body["slug"] == published.slug
        assert body["title"] == published.title
        assert body["status"] == published.status

    def test_retrieve_unknown_slug_returns_404(self, client, db):
        resp = client.get(reverse("post-detail", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_retrieve_draft_post_returns_404(self, client, draft):
        resp = client.get(reverse("post-detail", kwargs={"slug": draft.slug}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_retrieve_deleted_post_returns_404(self, client, deleted):
        resp = client.get(reverse("post-detail", kwargs={"slug": deleted.slug}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"


class PostCreateViewTests:
    MOCK_DATA = {
        "title": "New Post",
        "summary": "Lorem ipsum.",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    }

    def test_create_unauthenticated_returns_401(self, client):
        resp = client.post(
            reverse("post-list"), data=self.MOCK_DATA, content_type="application/json"
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"

    def test_create_valid_payload_returns_201(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("post-list"), data=self.MOCK_DATA, content_type="application/json"
        )
        body = resp.json()

        assert resp.status_code == 201
        assert body["title"] == "New Post"
        assert body["slug"] == "new-post"
        assert body["status"] == "draft"
        assert body["category"] is None

    def test_create_with_category_returns_category_slug(
        self, client, user_factory, category_factory
    ):
        client.force_login(user_factory())
        category = category_factory("Science")
        resp = client.post(
            reverse("post-list"),
            data={**self.MOCK_DATA, "category": category.pk},
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.json()["category"] == "science"

    @pytest.mark.parametrize("field", ["title", "summary", "content"])
    def test_create_missing_required_field_returns_400(
        self, client, user_factory, field
    ):
        client.force_login(user_factory())
        data = self.MOCK_DATA.copy()
        del data[field]
        resp = client.post(
            reverse("post-list"),
            data=data,
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"
        assert field in resp.json()["error"]["fields"]

    def test_create_duplicate_title_returns_400(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.post(
            reverse("post-list"),
            data={**self.MOCK_DATA, "title": published.title},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"
        assert "title" in resp.json()["error"]["fields"]

    def test_create_unknown_category_returns_400(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("post-list"),
            data={**self.MOCK_DATA, "category": 99999},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "category" in resp.json()["error"]["fields"]

    def test_create_non_json_content_type_returns_400(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("post-list"),
            data="title=New Post",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"


class PostUpdateViewTests:
    def test_update_unauthenticated_returns_401(self, client, published):
        resp = client.put(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": "x"},
            content_type="application/json",
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"

    def test_update_full_payload_returns_200(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.put(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": "Updated", "summary": "Sum", "content": "Body"},
            content_type="application/json",
        )
        body = resp.json()
        assert resp.status_code == 200
        assert body["title"] == "Updated"
        assert body["summary"] == "Sum"
        assert body["content"] == "Body"

    def test_update_unknown_slug_returns_404(self, client, user_factory):
        client.force_login(user_factory())
        resp = client.put(
            reverse("post-detail", kwargs={"slug": "nope"}),
            data={"title": "x"},
            content_type="application/json",
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_update_blank_title_returns_400(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.put(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": ""},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"

    def test_update_immutable_fields_returns_200(self, client, user_factory, published):
        client.force_login(user_factory())
        resp = client.put(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={
                "title": published.title,
                "summary": published.summary,
                "content": published.content,
                "slug": "hacked-slug",
                "status": "deleted",
                "published_at": "2020-01-01T00:00:00Z",
            },
            content_type="application/json",
        )
        body = resp.json()

        assert resp.status_code == 200
        assert body["slug"] == published.slug
        assert body["status"] == "published"

    def test_update_non_json_content_type_returns_400(
        self, client, user_factory, published
    ):
        client.force_login(user_factory())
        resp = client.put(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data="title=Updated",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_partial_update_title_only_returns_200(
        self, client, user_factory, published
    ):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": "Updated"},
            content_type="application/json",
        )
        body = resp.json()
        assert resp.status_code == 200
        assert body["title"] == "Updated"
        assert body["summary"] == published.summary
        assert body["content"] == published.content

    def test_partial_update_blank_title_returns_400(
        self, client, user_factory, published
    ):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": ""},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"

    def test_partial_update_immutable_fields_returns_200(
        self, client, user_factory, published
    ):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={
                "slug": "hacked-slug",
                "status": "deleted",
                "published_at": "2020-01-01T00:00:00Z",
            },
            content_type="application/json",
        )
        body = resp.json()
        assert resp.status_code == 200
        assert body["slug"] == published.slug
        assert body["status"] == "published"

    def test_partial_update_duplicate_title_returns_400(
        self, client, user_factory, published, draft
    ):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": draft.title},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "title" in resp.json()["error"]["fields"]

    def test_partial_update_non_json_content_type_returns_400(
        self, client, user_factory, published
    ):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data="title=Updated",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_partial_update_unauthenticated_returns_401(self, client, published):
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": published.slug}),
            data={"title": "x"},
            content_type="application/json",
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"
