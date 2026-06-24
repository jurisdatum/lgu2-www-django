"""Translate upstream API exceptions raised by lgu2.api.server into HTTP
responses. The api helpers raise rather than returning sentinels; views stay
clean of try/except boilerplate.

Rendering — including the format-aware branch for /data.{json,xml,akn,feed}
routes and the safe-render fallback — is delegated to lgu2.views.errors so the
middleware and the URLconf error handlers (handler404/handler500) stay
consistent. This module only classifies the upstream exception into a
status/template/message."""

from ..api.server import UpstreamError, UpstreamNotFound, UpstreamTimeout
from ..views.errors import render_error


def _status_and_template(exception):
    if isinstance(exception, UpstreamNotFound):
        return 404, "new_theme/404.html", "Not Found"
    if isinstance(exception, UpstreamTimeout):
        return 504, "new_theme/502.html", "Upstream Timeout"
    return 502, "new_theme/502.html", "Bad Gateway"


class UpstreamErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, UpstreamError):
            return None

        status, template, message = _status_and_template(exception)
        return render_error(request, status, template, message)
