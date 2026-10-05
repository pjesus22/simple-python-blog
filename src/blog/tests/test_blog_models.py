import pytest
from django.db import IntegrityError

from blog.models import Category, Post


class TestCategoryModels:
    def test_str_returns_name(self):
        assert str(Category(name="Stub Category")) == "Stub Category"

    def test_verbose_name_plural_is_categories(self):
        assert Category._meta.verbose_name_plural == "categories"

    def test_slug_generated_from_name_on_save(self, db):
        category = Category.objects.create(name="Stub Category")
        assert category.slug == "stub-category"

    def test_duplicate_name_raises_integrity_error(self, db):
        Category.objects.create(name="Stub Category")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Stub Category")


class TestPostModels:
    def test_str_returns_name(self):
        assert str(Post(title="Stub Post")) == "[draft] Stub Post"

    def test_slug_generated_from_name_on_save(self, db):
        post = Post.objects.create(title="Stub Post")
        assert post.slug == "stub-post"

    def test_duplicate_name_raises_integrity_error(self, db):
        Post.objects.create(title="Stub Post")
        with pytest.raises(IntegrityError):
            Post.objects.create(title="Stub Post")

    def test_default_status_is_draft(self):
        assert Post().status == "draft"
