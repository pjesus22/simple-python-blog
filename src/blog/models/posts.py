from django.db import models
from django.utils import timezone

from core import BaseModel


class InvalidTransition(Exception):
    def __init__(self, current: str, target: str):
        super().__init__(f"Cannot transition from {current} to {target}.")
        self.current = current
        self.target = target


class Post(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft"
        PUBLISHED = "published"
        DELETED = "deleted"

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        Status.DRAFT: {Status.PUBLISHED, Status.DELETED},
        Status.PUBLISHED: {Status.DRAFT, Status.DELETED},
        Status.DELETED: {Status.DRAFT},
    }

    category = models.ForeignKey(
        to="Category",
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, unique=True)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(
        choices=Status.choices, default=Status.DRAFT, editable=False
    )
    published_at = models.DateTimeField(null=True, blank=True, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    slug_source = "title"

    def __str__(self):
        return f"[{self.status}] {self.title}"

    def transition_to(self, target: str) -> None:
        if target not in self.ALLOWED_TRANSITIONS.get(self.status, set()):
            raise InvalidTransition(self.status, target)
        if target == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        if target == self.Status.DELETED:
            self.deleted_at = timezone.now()
        elif self.status == self.Status.DELETED:
            self.deleted_at = None
        self.status = target
        self.save()
