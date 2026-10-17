from django.views import defaults

from blog.views.helpers import error_response, invalid_request, not_found


def is_api_request(request) -> bool:
    return request.path_info.startswith(r"/api/")


def handler400(request, exception):
    if is_api_request(request):
        return invalid_request()
    return defaults.bad_request(request, exception)


def handler403(request, exception):
    if is_api_request(request):
        return error_response(
            "forbidden", "You do not have permission to perform this action.", 403
        )
    return defaults.permission_denied(request, exception)


def handler404(request, exception):
    if is_api_request(request):
        return not_found()
    return defaults.page_not_found(request, exception)


def handler500(request):
    if is_api_request(request):
        return error_response("internal_error", "An unexpected error occurred.", 500)
    return defaults.server_error(request)
