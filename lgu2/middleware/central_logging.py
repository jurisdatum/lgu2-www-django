import time
import json
import os
import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


def _env_true(name: str) -> bool:
    return os.getenv(name, "").lower() == 'true'

ENABLE_LOG = _env_true("CENTRAL_LOGGING")

class CentralRequestLoggingMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response)        
        self.logger = logging.getLogger("central_request_logger")

    def process_request(self, request):
        if not ENABLE_LOG:
            return None
        
        # stash start time on request object
        request._central_log_start = time.perf_counter()
        return None
    
    def process_response(self, request, response):
        if not ENABLE_LOG:
            return response
        
        start = getattr(request, "_central_log_start", None)
        if start is None:
            duration_ms = None
        else:
            duration_ms = int((time.perf_counter() - start) * 1000)

        payload = {
            "event_time": timezone.now().isoformat(),
            "path": request.path,
            "method": request.method,
            "status_code": getattr(response, "status_code", None),
            "duration_ms": duration_ms,
        }

        self.logger.info(json.dumps(payload, ensure_ascii=False))
        return response