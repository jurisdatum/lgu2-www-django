from typing import Optional

from django.http import HttpResponse, JsonResponse

from ..api.browse import browse_by_type, browse_by_type_and_year


def data(request, type: str, format: str, year: Optional[str] = None):
    page = request.GET.get("page", "1")
    if format == "feed":
        pass  # ToDo
    if format == "json":
        if year is None:
            data = browse_by_type(type, page)
        else:
            data = browse_by_type_and_year(type, year, page)
        return JsonResponse(data)
    return HttpResponse(status=406)
