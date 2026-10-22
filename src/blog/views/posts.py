from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from blog.forms import PostForm
from blog.models import Post
from blog.serializers import serialize_post
from blog.views.auth import login_required_json
from blog.views.base import ApiView
from blog.views.helpers import (
    collection,
    invalid_request,
    invalid_transition,
    paginate,
    parse_json,
    resource,
    validation_error,
)


def lifecycle_response(post, source, target):
    if post.status not in source:
        return invalid_transition()
    post.transition_to(target)
    return resource(serialize_post(post))


@method_decorator(csrf_exempt, name="dispatch")
class PostListView(ApiView):
    def get(self, request):
        qs = Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
            "category"
        )
        category = request.GET.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        items, meta = paginate(qs, request)
        return collection([serialize_post(p) for p in items], meta)

    @login_required_json
    def post(self, request):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        form = PostForm(data)
        if not form.is_valid():
            return validation_error(form.errors)
        post = Post.objects.create(
            title=form.cleaned_data["title"],
            summary=form.cleaned_data["summary"],
            content=form.cleaned_data["content"],
            category=form.cleaned_data["category"],
        )
        return resource(serialize_post(post), status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PostDetailView(ApiView):
    def get(self, request, slug):
        post = get_object_or_404(
            Post.objects.select_related("category"),
            slug=slug,
            status=Post.Status.PUBLISHED,
        )
        return resource(serialize_post(post))

    @login_required_json
    def put(self, request, slug):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        post = get_object_or_404(Post.objects, slug=slug)
        form = PostForm(data=data, instance=post)
        if not form.is_valid():
            return validation_error(form.errors)
        for field, value in form.cleaned_data.items():
            setattr(post, field, value)
        post.save()
        return resource(serialize_post(post))

    @login_required_json
    def patch(self, request, slug):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        post = get_object_or_404(Post.objects, slug=slug)
        form = PostForm(data=data, instance=post)
        for name in list(form.fields):
            if name not in data:
                form.fields.pop(name)
        if not form.is_valid():
            return validation_error(form.errors)
        for field, value in form.cleaned_data.items():
            setattr(post, field, value)
        post.save()
        return resource(serialize_post(post))

    @login_required_json
    def delete(self, request, slug):
        post = get_object_or_404(Post.objects, slug=slug)
        return lifecycle_response(
            post, (Post.Status.DRAFT, Post.Status.PUBLISHED), Post.Status.DELETED
        )


class PostLifecycleView(ApiView):
    source: tuple[str, ...]
    target: str

    @login_required_json
    def post(self, request, slug):
        post = get_object_or_404(Post.objects, slug=slug)
        return lifecycle_response(post, self.source, self.target)


class PostPublishView(PostLifecycleView):
    source = (Post.Status.DRAFT,)
    target = Post.Status.PUBLISHED


class PostUnpublishView(PostLifecycleView):
    source = (Post.Status.PUBLISHED,)
    target = Post.Status.DRAFT


class PostRestoreView(PostLifecycleView):
    source = (Post.Status.DELETED,)
    target = Post.Status.DRAFT
