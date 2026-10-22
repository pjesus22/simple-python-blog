import pytest
from django.db import IntegrityError

from blog.models import Category, InvalidTransition, Post


class CategoryModelsTests:
    def test_str_named_category_returns_name(self):
        assert str(Category(name="Stub Category")) == "Stub Category"

    def test_verbose_name_plural_default_returns_categories(self):
        assert Category._meta.verbose_name_plural == "categories"

    def test_save_new_category_generates_slug_from_name(self, db):
        category = Category.objects.create(name="Stub Category")
        assert category.slug == "stub-category"

    def test_save_duplicate_category_name_raises_integrity_error(self, db):
        Category.objects.create(name="Stub Category")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Stub Category")


class PostModelsTests:
    def test_str_draft_post_returns_prefixed_title(self):
        assert str(Post(title="Stub Post")) == "[draft] Stub Post"

    def test_save_new_post_generates_slug_from_title(self, db):
        post = Post.objects.create(title="Stub Post")
        assert post.slug == "stub-post"

    def test_save_duplicate_post_title_raises_integrity_error(self, db):
        Post.objects.create(title="Stub Post")
        with pytest.raises(IntegrityError):
            Post.objects.create(title="Stub Post")

    def test_init_post_default_status_is_draft(self):
        assert Post().status == "draft"


class PostLifecycleTests:
    def test_deleted_at_defaults_to_none(self, db):
        post = Post.objects.create(title="No Deletion")
        assert post.deleted_at is None

    def test_publish_draft_sets_status_and_published_at(self, draft):
        draft.transition_to(Post.Status.PUBLISHED)
        draft.refresh_from_db()
        assert draft.status == Post.Status.PUBLISHED
        assert draft.published_at is not None

    def test_unpublish_published_sets_draft_and_retains_published_at(self, published):
        original = published.published_at
        published.transition_to(Post.Status.DRAFT)
        published.refresh_from_db()
        assert published.status == Post.Status.DRAFT
        assert published.published_at == original

    def test_republish_retains_first_published_at(self, published):
        original = published.published_at
        published.transition_to(Post.Status.DRAFT)
        published.transition_to(Post.Status.PUBLISHED)
        published.refresh_from_db()
        assert published.published_at == original

    def test_soft_delete_draft_sets_deleted_at(self, draft):
        draft.transition_to(Post.Status.DELETED)
        draft.refresh_from_db()
        assert draft.status == Post.Status.DELETED
        assert draft.deleted_at is not None

    def test_soft_delete_published_sets_deleted_at(self, published):
        published.transition_to(Post.Status.DELETED)
        published.refresh_from_db()
        assert published.status == Post.Status.DELETED
        assert published.deleted_at is not None

    def test_restore_deleted_sets_draft_and_clears_deleted_at(self, deleted):
        deleted.transition_to(Post.Status.DRAFT)
        deleted.refresh_from_db()
        assert deleted.status == Post.Status.DRAFT
        assert deleted.deleted_at is None

    def test_publish_deleted_is_rejected(self, deleted):
        original = deleted.deleted_at
        with pytest.raises(InvalidTransition):
            deleted.transition_to(Post.Status.PUBLISHED)
        deleted.refresh_from_db()
        assert deleted.status == Post.Status.DELETED
        assert deleted.deleted_at == original

    def test_repeat_transition_is_rejected(self, published):
        with pytest.raises(InvalidTransition):
            published.transition_to(Post.Status.PUBLISHED)
