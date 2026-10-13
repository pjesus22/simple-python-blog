from django.urls import path

from blog.views import (
    CategoryDetailView,
    CategoryListView,
    LoginView,
    LogoutView,
    PostDetailView,
    PostListView,
)

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("posts", PostListView.as_view(), name="post-list"),
    path("posts/<slug:slug>", PostDetailView.as_view(), name="post-detail"),
    path("categories", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>", CategoryDetailView.as_view(), name="category-detail"
    ),
]
