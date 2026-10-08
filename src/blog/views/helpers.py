import json

from django.http import JsonResponse


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


def parse_json(request) -> dict | None:
    if request.content_type != "application/json":
        return None
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError, UnicodeDecodeError:
        return None
