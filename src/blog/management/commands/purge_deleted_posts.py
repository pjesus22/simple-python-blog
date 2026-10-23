from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from blog.models import Post


class Command(BaseCommand):
    help = "Permanently delete posts soft-deleted at or before the retention cutoff."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report posts that would be purged without deleting them.",
        )

    def handle(self, *args, **options):
        if settings.POST_RETENTION_DAYS < 0:
            raise CommandError(
                f"Invalid POST_RETENTION_DAYS: {settings.POST_RETENTION_DAYS}"
            )
        cutoff = timezone.now() - timedelta(days=settings.POST_RETENTION_DAYS)
        post = Post.objects.filter(status=Post.Status.DELETED, deleted_at__lte=cutoff)
        if options["dry_run"]:
            slugs = list(post.values_list("slug", flat=True))
            for slug in slugs:
                self.stdout.write(f"Would purge: {slug}")
            self.stdout.write(f"{len(slugs)} post(s) would be purged.")
            return
        count, _ = post.delete()
        self.stdout.write(f"Purged {count} post(s).")
