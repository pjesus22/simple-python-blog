from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from blog.forms import CategoryForm
from blog.models import Category
from blog.serializers import serialize_category
from blog.views.auth import login_required_json
from blog.views.base import ApiView
from blog.views.helpers import (
    collection,
    invalid_request,
    paginate,
    parse_json,
    resource,
    validation_error,
)


@method_decorator(csrf_exempt, name="dispatch")
class CategoryListView(ApiView):
    def get(self, request):
        items, meta = paginate(Category.objects.all(), request)
        return collection([serialize_category(c) for c in items], meta)

    @login_required_json
    def post(self, request):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        form = CategoryForm(data)
        if not form.is_valid():
            return validation_error(form.errors)
        category = Category.objects.create(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
        )
        return resource(serialize_category(category), status=201)


@method_decorator(csrf_exempt, name="dispatch")
class CategoryDetailView(ApiView):
    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        return resource(serialize_category(category))

    @login_required_json
    def patch(self, request, slug):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        category = get_object_or_404(Category, slug=slug)
        form = CategoryForm(data=data, instance=category)
        for name in list(form.fields):
            if name not in data:
                form.fields.pop(name)
        if not form.is_valid():
            return validation_error(form.errors)
        for field, value in form.cleaned_data.items():
            setattr(category, field, value)
        category.save()
        return resource(serialize_category(category))

    @login_required_json
    def delete(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return HttpResponse(status=204)
