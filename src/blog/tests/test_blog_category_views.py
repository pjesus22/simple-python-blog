import pytest
from django.urls import reverse

from blog.models import Post
from blog.models.categories import Category


class CategoryListViewTests:
    def test_list_empty_database_returns_empty_items(self, client, db):
        resp = client.get(reverse("category-list"))
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["pagination"]["total"] == 0

    def test_list_more_than_page_size_returns_paginated_results(
        self, client, category_factory
    ):
        for _ in range(21):
            category_factory()
        body = client.get(reverse("category-list")).json()
        assert body["pagination"] == {
            "page": 1,
            "page_size": 20,
            "total": 21,
            "total_pages": 2,
        }
        assert len(body["items"]) == 20

    def test_list_page_beyond_last_returns_last_page(self, client, category_factory):
        for _ in range(21):
            category_factory()
        body = client.get(reverse("category-list"), {"page": 99}).json()
        assert body["pagination"] == {
            "page": 2,
            "page_size": 20,
            "total": 21,
            "total_pages": 2,
        }
        assert len(body["items"]) == 1


class CategoryRetrieveViewTests:
    def test_retrieve_existing_category_returns_200(self, client, category_factory):
        category = category_factory(name="New Category")
        resp = client.get(reverse("category-detail", kwargs={"slug": category.slug}))
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Category"

    def test_retrieve_unknown_slug_returns_404(self, client, db):
        resp = client.get(reverse("category-detail", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"


class CategoryCreateViewTests:
    def test_create_valid_payload_returns_201(self, client, db, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("category-list"),
            data={
                "name": "New Category",
                "description": "Standard text for automated suites.",
            },
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.json()["slug"] == "new-category"

    def test_create_without_description_returns_201(self, client, db, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("category-list"),
            data={"name": "New Category"},
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.json()["description"] == ""

    def test_create_duplicate_name_returns_400(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category_factory(name="Same Category")
        resp = client.post(
            reverse("category-list"),
            data={"name": "Same Category"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"

    @pytest.mark.parametrize(
        "data", [{"description": "x"}, {"name": ""}, {"name": "x" * 65}]
    )
    def test_create_invalid_name_returns_400(self, client, db, data, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("category-list"), data=data, content_type="application/json"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"
        assert "name" in resp.json()["error"]["fields"]

    def test_create_non_json_returns_400(self, client, db, user_factory):
        client.force_login(user_factory())
        resp = client.post(
            reverse("category-list"),
            data="name=New Category",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_create_unauthenticated_returns_401(self, client, db):
        resp = client.post(
            reverse("category-list"),
            data={"name": "New Category"},
            content_type="application/json",
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"
        assert not Category.objects.exists()


class CategoryUpdateViewTests:
    def test_patch_name_keeps_slug_returns_200(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": category.slug}),
            data={"name": "Updated Category"},
            content_type="application/json",
        )
        category.refresh_from_db()
        assert resp.status_code == 200
        assert category.name == "Updated Category"
        assert category.slug == "test-category-0"

    def test_patch_description_only_keeps_name_returns_200(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": category.slug}),
            data={"description": "New text"},
            content_type="application/json",
        )
        category.refresh_from_db()
        assert resp.status_code == 200
        assert category.name == "Test Category 0"
        assert category.description == "New text"

    def test_patch_immutable_slug_ignored_returns_200(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": category.slug}),
            data={"slug": "hacked"},
            content_type="application/json",
        )
        category.refresh_from_db()
        assert resp.status_code == 200
        assert category.slug == "test-category-0"

    def test_patch_blank_name_returns_400(self, client, category_factory, user_factory):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": category.slug}),
            data={"name": ""},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "name" in resp.json()["error"]["fields"]

    def test_patch_duplicate_name_returns_400(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category_factory(name="Original Category")
        other = category_factory(name="Other Category")
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": other.slug}),
            data={"name": "Original Category"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "validation_error"

    def test_patch_unknown_slug_returns_404(self, client, db, user_factory):
        client.force_login(user_factory())
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": "nope"}),
            data={"name": "x"},
            content_type="application/json",
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_patch_non_json_content_type_returns_400(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.patch(
            reverse("category-detail", kwargs={"slug": category.slug}),
            data="name=Updates",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_request"

    def test_patch_unauthenticated_returns_401(self, client, category_factory, db):
        category = category_factory()
        resp = client.patch(
            reverse("post-detail", kwargs={"slug": category.slug}),
            data={"name": "Hacked"},
            content_type="application/json",
        )
        category.refresh_from_db()
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"
        assert category.name == "Test Category 0"


class CategoryDeleteViewTests:
    def test_delete_existing_category_returns_204_and_removes_row(
        self, client, category_factory, user_factory
    ):
        client.force_login(user_factory())
        category = category_factory()
        resp = client.delete(reverse("category-detail", kwargs={"slug": category.slug}))
        assert resp.status_code == 204
        assert not Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_with_posts_returns_204_and_nulls_post_category(
        self, client, post_factory, user_factory
    ):
        client.force_login(user_factory())
        post = post_factory(status=Post.Status.PUBLISHED)
        category = post.category
        resp = client.delete(reverse("category-detail", kwargs={"slug": category.slug}))
        post.refresh_from_db()
        assert resp.status_code == 204
        assert post.category is None

    def test_delete_unknown_slug_returns_404(self, client, db, user_factory):
        client.force_login(user_factory())
        resp = client.delete(reverse("category-detail", kwargs={"slug": "nope"}))
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_delete_unauthenticated_returns_401(self, client, category_factory, db):
        category = category_factory()
        resp = client.delete(reverse("category-detail", kwargs={"slug": category.slug}))
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "unauthenticated"
        assert Category.objects.filter(pk=category.pk).exists()
