from django.urls import reverse

from blog.models import Category, Post


class PostCrudTests:
    def test_post_crud_flow(self, authenticated_api):
        api = authenticated_api

        status, category = api.post(
            reverse("category-list"),
            body={"name": "Post Category", "description": "Created over HTTP."},
        )
        assert status == 201

        status, body = api.post(
            reverse("post-list"),
            body={
                "title": "E2E Post",
                "summary": "Created over HTTP.",
                "content": "Body created over HTTP.",
                "category": category["id"],
            },
        )
        assert status == 201
        post_slug = body["slug"]
        assert body["status"] == "draft"
        assert body["category"] == category["slug"]

        status, body = api.put(
            reverse("post-detail", kwargs={"slug": post_slug}),
            body={
                "title": "E2E Post Updated.",
                "summary": "Updated over HTTP.",
                "content": "Updated body over HTTP.",
                "category": category["id"],
            },
        )
        assert status == 200
        assert body["title"] == "E2E Post Updated."
        assert body["summary"] == "Updated over HTTP."

        status, body = api.patch(
            reverse("post-detail", kwargs={"slug": post_slug}),
            body={"summary": "Patched over HTTP."},
        )
        assert status == 200
        assert body["title"] == "E2E Post Updated."
        assert body["summary"] == "Patched over HTTP."

    class PublicVisibilityTests:
        def test_public_visibility_rules(self, api, transactional_db):
            category = Category.objects.create(
                name="Public Category", description="Visible over HTTP."
            )
            other_category = Category.objects.create(
                name="Other Category", description="Visible over HTTP."
            )
            published = Post.objects.create(
                title="Published Post",
                summary="Published.",
                content="Published over HTTP.",
                category=category,
                status=Post.Status.PUBLISHED,
            )
            draft = Post.objects.create(
                title="Draft Post",
                summary="Draft.",
                content="Draft over HTTP.",
                category=category,
            )
            deleted = Post.objects.create(
                title="Deleted Post",
                summary="Deleted.",
                content="Deleted over HTTP.",
                category=category,
                status=Post.Status.DELETED,
            )
            other = Post.objects.create(
                title="Other Published Post",
                summary="Published elsewhere.",
                content="Published elsewhere over HTTP.",
                category=other_category,
                status=Post.Status.PUBLISHED,
            )

            status, body = api.get(reverse("post-list"))
            slugs = [item["slug"] for item in body["items"]]
            assert status == 200
            assert published.slug in slugs
            assert other.slug in slugs
            assert draft.slug not in slugs
            assert deleted.slug not in slugs
            assert body["pagination"] == {
                "page": 1,
                "page_size": 20,
                "total": 2,
                "total_pages": 1,
            }

            status, body = api.get(
                reverse("post-detail", kwargs={"slug": published.slug}),
            )
            assert status == 200
            assert body["slug"] == published.slug

            for post in (draft, deleted):
                status, body = api.get(
                    reverse("post-detail", kwargs={"slug": post.slug}),
                )
                assert status == 404
                assert body["error"]["code"] == "not_found"

            status, body = api.get(f"{reverse('post-list')}?category={category.slug}")
            assert status == 200
            assert [item["slug"] for item in body["items"]] == [published.slug]


class PublicPaginationTests:
    def test_public_list_pagination(self, api, transactional_db):
        for index in range(21):
            Post.objects.create(
                title=f"Pagination Post {index}",
                summary="Pagination.",
                content="Pagination over HTTP.",
                status=Post.Status.PUBLISHED,
            )

        status, body = api.get(reverse("post-list"))
        assert status == 200
        assert body["pagination"] == {
            "page": 1,
            "page_size": 20,
            "total": 21,
            "total_pages": 2,
        }
        assert len(body["items"]) == 20

        status, body = api.get(f"{reverse('post-list')}?page=2")
        assert status == 200
        assert body["pagination"]["page"] == 2
        assert len(body["items"]) == 1
