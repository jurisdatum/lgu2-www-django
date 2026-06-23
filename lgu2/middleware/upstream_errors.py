"""Translate upstream API exceptions raised by lgu2.api.server into HTTP
responses. The api helpers raise rather than returning sentinels; views stay
clean of try/except boilerplate.

Format-aware: routes ending in /data.{json,xml,akn,feed} (the `format` kwarg
captured by lgu2/urls.py) get a response in the matching content-type instead
of an HTML error page, so API and feed consumers don't receive HTML where they
expect machine-readable bodies."""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from ..api.server import UpstreamError, UpstreamNotFound, UpstreamTimeout

# Format kwarg → (content-type, empty body). JSON is handled separately because
# it gets an error envelope rather than an empty body.
_FORMAT_CONTENT_TYPES = {
    "xml": "application/xml",
    "akn": "application/akn+xml",
    "feed": "application/atom+xml",
}


def _status_and_template(exception):
    if isinstance(exception, UpstreamNotFound):
        return 404, "new_theme/404.html", "Not Found"
    if isinstance(exception, UpstreamTimeout):
        return 504, "new_theme/502.html", "Upstream Timeout"
    return 502, "new_theme/502.html", "Bad Gateway"


def _safe_render(request, template, status):
    # Wrap render so a broken error template (renamed {% url %}, broken include,
    # context-processor crash) does not cascade into a Django 500 at exactly the
    # moment the friendly page is needed.
    try:
        return render(request, template, status=status)
    except Exception:
        return HttpResponse(
            b"Service temporarily unavailable.",
            content_type="text/plain",
            status=status,
        )


class UpstreamErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, UpstreamError):
            return None

        status, template, message = _status_and_template(exception)

        fmt = None
        if request.resolver_match is not None:
            fmt = request.resolver_match.kwargs.get("format")

        if fmt == "json":
            return JsonResponse({"error": message, "status": status}, status=status)
        if fmt in _FORMAT_CONTENT_TYPES:
            return HttpResponse(
                b"", content_type=_FORMAT_CONTENT_TYPES[fmt], status=status
            )

        # html, no kwarg, or any other route → branded page.
        return _safe_render(request, template, status)
