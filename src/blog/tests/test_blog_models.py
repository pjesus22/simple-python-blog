import pytest
from django.db import IntegrityError

from blog.models import Category, Post


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
