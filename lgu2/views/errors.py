"""Custom error handlers, wired as handler404/handler500 in lgu2/urls.py.

These cover errors Django itself raises — an unmatched URL (resolver 404) or an
unhandled exception in a view (500) — as opposed to upstream API failures, which
UpstreamErrorMiddleware translates separately. Both paths render the same
new_theme templates so every error surfaces in one consistent style.

The render is wrapped so a broken error template can't cascade into a second
failure at the moment the friendly page is needed (the same guard the upstream
middleware applies)."""

from django.http import HttpResponse
from django.shortcuts import render


def _safe_render(request, template, status):
    try:
        return render(request, template, status=status)
    except Exception:
        return HttpResponse(
            b"Service temporarily unavailable.",
            content_type="text/plain",
            status=status,
        )


def page_not_found(request, exception):
    return _safe_render(request, "new_theme/404.html", 404)


def server_error(request):
    # Reuses the generic "service unavailable" page; no upstream-specific wording.
    return _safe_render(request, "new_theme/502.html", 500)
