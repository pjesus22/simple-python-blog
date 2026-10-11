import itertools
from typing import cast

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager

from blog.models import Category, Post


@pytest.fixture
def user_factory(db):
    counter = itertools.count()

    def _make(username=None, password="test"):  # noqa: S107
        username = username or f"user-{next(counter)}"
        manager = cast(UserManager, get_user_model().objects)
        return manager.create_user(username=username, password=password)

    return _make


@pytest.fixture
def category_factory(db):
    counter = itertools.count()

    def _make(name=None):
        return Category.objects.create(
            name=name or f"Test Category {next(counter)}",
            description="Standard text for automated suites.",
        )

    return _make


@pytest.fixture
def post_factory(db, category_factory):
    counter = itertools.count()

    def _make(title=None, status=Post.Status.DRAFT):
        post = Post.objects.create(
            title=title or f"Test Post {next(counter)}",
            summary="Standard text for automated suites.",
            content=(
                "This record represents standardized, asyntactic telemetry garbage engineered exclusively for automated continuous integration test suites. It carries zero semantic value, zero domain utility, and exists solely to satisfy non-null database constraints and assertion checks during test execution."
            ),
            category=category_factory(),
        )
        if status != Post.Status.DRAFT:
            post.status = status
            post.save()
        return post

    return _make


@pytest.fixture
def draft(post_factory):
    return post_factory(title="Draft Post")


@pytest.fixture
def published(post_factory):
    return post_factory(title="Published Post", status=Post.Status.PUBLISHED)


@pytest.fixture
def deleted(post_factory):
    return post_factory(title="Deleted Post", status=Post.Status.DELETED)
