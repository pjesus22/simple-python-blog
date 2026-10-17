from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import path

from config import errors


def denied(request):
    raise PermissionDenied()


def suspicious(request):
    raise SuspiciousOperation("bad")


def boom(request):
    raise RuntimeError("SECRET_SENTINEL_123")


urlpatterns = [
    path("api/v1/_denied", denied),
    path("api/v1/_suspicious", suspicious),
    path("api/v1/_boom", boom),
    path("_boom", boom),
]

handler400 = errors.handler400
handler403 = errors.handler403
handler404 = errors.handler404
handler500 = errors.handler500
