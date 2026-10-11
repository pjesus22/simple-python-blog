import json

from django.core.paginator import Paginator
from django.http import Http404, JsonResponse


def _response(
    code: str, message: str, status: int, fields: dict | None = None
) -> JsonResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return JsonResponse(body, status=status)


def invalid_request() -> JsonResponse:
    return _response("invalid_request", "The request is invalid.", 400)


def missing_credentials() -> JsonResponse:
    return _response("missing_credentials", "Username and password are required.", 400)


def invalid_credentials() -> JsonResponse:
    return _response("invalid_credentials", "Invalid username or password.", 401)


def unauthenticated() -> JsonResponse:
    return _response("unauthenticated", "Authentication required.", 401)


def validation_error(fields: dict) -> JsonResponse:
    return _response("validation_error", "One or more fields are invalid.", 400, fields)


def not_found() -> JsonResponse:
    return _response("not_found", "Resource not found.", 404)


def parse_json(request) -> dict | None:
    if request.content_type != "application/json":
        return None
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError, UnicodeDecodeError:
        return None
    return data if isinstance(data, dict) else None


def resource(data: dict, status: int = 200) -> JsonResponse:
    return JsonResponse(data, status=status)


def collection(items: list, pagination: dict) -> JsonResponse:
    return JsonResponse({"items": items, "pagination": pagination}, status=200)


def paginate(queryset, request, per_page=20):
    paginator = Paginator(queryset, per_page)
    page = paginator.get_page(request.GET.get("page"))
    meta = {
        "page": page.number,
        "page_size": per_page,
        "total": paginator.count,
        "total_pages": paginator.num_pages,
    }
    return list(page), meta


class Json404Mixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return not_found()
