from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    slug_source: str | None = None

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-id"]

    def save(self, *args, **kwargs):
        if self.slug_source and not self.slug:
            self.slug = slugify(getattr(self, self.slug_source))
        super().save(*args, **kwargs)
