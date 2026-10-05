from django.db import models

from core import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255)

    slug_source = "name"

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return str(self.name)
