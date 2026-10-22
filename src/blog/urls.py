from django.urls import path

from blog.views import (
    CategoryDetailView,
    CategoryListView,
    LoginView,
    LogoutView,
    PostDetailView,
    PostListView,
    PostPublishView,
    PostRestoreView,
    PostUnpublishView,
)

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("posts", PostListView.as_view(), name="post-list"),
    path("posts/<slug:slug>", PostDetailView.as_view(), name="post-detail"),
    path("posts/<slug:slug>/publish", PostPublishView.as_view(), name="post-publish"),
    path("posts/<slug:slug>/restore", PostRestoreView.as_view(), name="post-restore"),
    path(
        "posts/<slug:slug>/unpublish",
        PostUnpublishView.as_view(),
        name="post-unpublish",
    ),
    path("categories", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>", CategoryDetailView.as_view(), name="category-detail"
    ),
]
