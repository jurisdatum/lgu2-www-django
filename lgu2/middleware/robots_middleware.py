from django.http import HttpResponse

class RobotsTxtMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Serve robots.txt
        if request.path == '/robots.txt':
            content = "User-agent: *\nDisallow:"
            return HttpResponse(content, content_type="text/plain")
        return self.get_response(request)
