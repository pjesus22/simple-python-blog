from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from blog.forms import PostForm
from blog.models import Post
from blog.serializers import serialize_post
from blog.views.auth import login_required_json
from blog.views.helpers import (
    Json404Mixin,
    collection,
    invalid_request,
    paginate,
    parse_json,
    resource,
    validation_error,
)


@method_decorator(csrf_exempt, name="dispatch")
class PostListView(View):
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
class PostDetailView(Json404Mixin, View):
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
