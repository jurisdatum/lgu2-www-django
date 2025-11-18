import json
import logging
import time

from django.utils import timezone


logger = logging.getLogger("central_request_logger")

class CentralRequestLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception as e:
            self._emit(request, getattr(e, "status_code", 500), start)
            raise
        else:
            self._emit(request, getattr(response, "status_code", None), start)
            return response

    def _emit(self, request, status_code, start):
        duration_ms = int((time.perf_counter() - start) * 1000)
        payload = {
            "event_time": timezone.now().isoformat(),
            "path": request.path,
            "method": request.method,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }
        logger.debug(json.dumps(payload, ensure_ascii=False))
