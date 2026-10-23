from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.utils import timezone

from blog.models import Post


def purge(*args):
    out = StringIO()
    call_command("purge_deleted_posts", *args, stdout=out)
    return out.getvalue()


def set_deleted_days_ago(post, days):
    Post.objects.filter(pk=post.pk).update(
        deleted_at=timezone.now() - timedelta(days=days)
    )


class PurgeDeletedPostsTests:
    def test_purges_deleted_posts_outside_retention(self, deleted):
        set_deleted_days_ago(deleted, 31)

        purge()

        assert not Post.objects.filter(pk=deleted.pk).exists()

    def test_keeps_deleted_post_inside_retention(self, deleted):
        set_deleted_days_ago(deleted, 29)

        purge()

        assert Post.objects.filter(pk=deleted.pk).exists()

    def test_never_purges_draft_or_published(self, draft, published):
        set_deleted_days_ago(draft, 31)
        set_deleted_days_ago(published, 31)

        purge()

        assert Post.objects.filter(pk__in=[draft.pk, published.pk]).count() == 2

    def test_dry_run_reports_and_deletes_nothing(self, deleted):
        set_deleted_days_ago(deleted, 31)

        output = purge("--dry-run")

        assert Post.objects.filter(pk=deleted.pk).exists()
        assert deleted.slug in output

    @override_settings(POST_RETENTION_DAYS=7)
    def test_retention_period_comes_from_setting(self, deleted):
        set_deleted_days_ago(deleted, 8)

        purge()

        assert not Post.objects.filter(pk=deleted.pk).exists()

    @override_settings(POST_RETENTION_DAYS=-1)
    def test_negative_retention_refuses_to_purge(self, deleted):
        set_deleted_days_ago(deleted, 31)

        with pytest.raises(CommandError):
            purge()

        assert Post.objects.filter(pk=deleted.pk).exists()
