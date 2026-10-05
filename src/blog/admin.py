from django.contrib import admin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "published_at", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug", "status", "published_at", "created_at", "updated_at")
    fieldsets = [
        ("Content", {"fields": ["title", "summary", "content", "category"]}),
        (
            "Metadata",
            {"fields": ["slug", "status", "published_at", "created_at", "updated_at"]},
        ),
    ]
