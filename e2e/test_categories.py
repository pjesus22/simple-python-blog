from django.urls import reverse


class CategoryCrudTests:
    def test_category_crud_flow(self, authenticated_api, admin_user):
        api = authenticated_api

        status, body = api.post(
            reverse("category-list"),
            body={"name": "E2E Category", "description": "Created over HTTP."},
        )
        assert status == 201

        category_slug = body["slug"]
        status, body = api.get(
            reverse("category-detail", kwargs={"slug": category_slug})
        )
        assert status == 200
        assert body["name"] == "E2E Category"

        status, body = api.get(reverse("category-list"))
        assert status == 200
        assert category_slug in [item["slug"] for item in body["items"]]

        status, body = api.patch(
            reverse("category-detail", kwargs={"slug": category_slug}),
            body={"description": "Updated over HTTP."},
        )
        assert status == 200
        assert body["description"] == "Updated over HTTP."

        status, body = api.delete(
            reverse("category-detail", kwargs={"slug": category_slug})
        )
        assert status == 204
        assert body is None

        status, body = api.get(
            reverse("category-detail", kwargs={"slug": category_slug})
        )
        assert status == 404
        assert body["error"]["code"] == "not_found"
