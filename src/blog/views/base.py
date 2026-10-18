from django.views import View

from blog.views.helpers import method_not_allowed


class ApiView(View):
    def http_method_not_allowed(self, request, *args, **kwargs):
        resp = method_not_allowed()
        resp["Allow"] = ", ".join(
            m.upper() for m in self.http_method_names if hasattr(self, m)
        )
        return resp
