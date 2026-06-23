"""Error-response rendering, shared by the URLconf handlers (handler404 /
handler500, wired in lgu2/urls.py) and by UpstreamErrorMiddleware.

render_error is the single source of truth for *how* an error becomes a
response. It is format-aware: a route that captured a `format` kwarg
(/data.{json,xml,akn,feed}) gets a machine-readable body, so API and feed
consumers never receive an HTML error page; everything else gets the branded
new_theme page. The HTML render is wrapped so a broken error template can't
cascade into a second failure at the moment the friendly page is needed.

The handlers (Django-raised 404/500) and the middleware (upstream API failures)
each decide the status/template/message, then delegate the rendering here so the
two paths stay consistent."""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Non-JSON data formats -> (content-type, empty body). JSON is handled
# separately because it gets an error envelope rather than an empty body.
_FORMAT_CONTENT_TYPES = {
    "xml": "application/xml",
    "akn": "application/akn+xml",
    "feed": "application/atom+xml",
}


def render_error(request, status, template, message):
    """Build an error response in the format the matched route expects."""
    fmt = None
    if request.resolver_match is not None:
        fmt = request.resolver_match.kwargs.get("format")

    if fmt == "json":
        return JsonResponse({"error": message, "status": status}, status=status)
    if fmt in _FORMAT_CONTENT_TYPES:
        return HttpResponse(b"", content_type=_FORMAT_CONTENT_TYPES[fmt], status=status)

    # html, no kwarg, or any other route -> branded page. Wrap render so a broken
    # error template (renamed {% url %}, broken include, context-processor crash)
    # does not cascade into a Django 500 at exactly the moment it is needed.
    try:
        return render(request, template, status=status)
    except Exception:
        return HttpResponse(
            b"Service temporarily unavailable.",
            content_type="text/plain",
            status=status,
        )


def page_not_found(request, exception):
    return render_error(request, 404, "new_theme/404.html", "Not Found")


def server_error(request):
    # Reuses the generic "service unavailable" page; no 500-specific template.
    return render_error(request, 500, "new_theme/502.html", "Internal Server Error")
