from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from blog.views.base import ApiView
from blog.views.helpers import (
    invalid_credentials,
    invalid_request,
    missing_credentials,
    parse_json,
    unauthenticated,
)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(ApiView):
    def post(self, request):
        data = parse_json(request)
        if data is None:
            return invalid_request()
        username, password = data.get("username"), data.get("password")
        if not username or not password:
            return missing_credentials()
        user = authenticate(request, username=username, password=password)
        if user is None:
            return invalid_credentials()
        login(request, user)
        return JsonResponse({"id": user.pk, "username": user.get_username()})


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(ApiView):
    def post(self, request):
        if not request.user.is_authenticated:
            return unauthenticated()
        logout(request)
        return HttpResponse(status=204)


def login_required_json(view):
    @wraps(view)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return unauthenticated()
        return view(self, request, *args, **kwargs)

    return wrapper
