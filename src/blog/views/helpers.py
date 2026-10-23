import json

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse


def error_response(
    code: str, message: str, status: int, fields: dict | None = None
) -> JsonResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return JsonResponse(body, status=status)


def invalid_request() -> JsonResponse:
    return error_response("invalid_request", "The request is invalid.", 400)


def missing_credentials() -> JsonResponse:
    return error_response(
        "missing_credentials", "Username and password are required.", 400
    )


def invalid_credentials() -> JsonResponse:
    return error_response("invalid_credentials", "Invalid username or password.", 401)


def unauthenticated() -> JsonResponse:
    return error_response("unauthenticated", "Authentication required.", 401)


def validation_error(fields: dict) -> JsonResponse:
    return error_response(
        "validation_error", "One or more fields are invalid.", 400, fields
    )


def not_found() -> JsonResponse:
    return error_response("not_found", "Resource not found.", 404)


def invalid_transition() -> JsonResponse:
    return error_response(
        "invalid_transition", "The requested transition is not allowed.", 409
    )


def method_not_allowed() -> JsonResponse:
    return error_response("method_not_allowed", "Method not allowed.", 405)


def forbidden() -> JsonResponse:
    return error_response(
        "forbidden", "You do not have permission to perform this action.", 403
    )


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


def paginate(queryset, request, per_page=None):
    if per_page is None:
        per_page = settings.API_PAGE_SIZE
    if per_page < 1:
        raise ValueError("Page size must be at least 1.")
    paginator = Paginator(queryset, per_page)
    page = paginator.get_page(request.GET.get("page"))
    meta = {
        "page": page.number,
        "page_size": per_page,
        "total": paginator.count,
        "total_pages": paginator.num_pages,
    }
    return list(page), meta
