
from django.http import HttpResponse

def robots_txt(_request):
    content = "User-agent: *\nDisallow: /\n"
    resp = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return resp
