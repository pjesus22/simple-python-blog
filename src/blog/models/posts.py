from django.db import models

from core import BaseModel


class Post(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft"
        PUBLISHED = "published"
        DELETED = "deleted"

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

    slug_source = "title"

    def __str__(self):
        return f"[{self.status}] {self.title}"
