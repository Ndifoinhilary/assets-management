"""
Custom middleware implementing
"""
import logging
import json
import time
import uuid
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests without interfering with authentication
    """

    def process_request(self, request):
        # Skip logging for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None

        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())[:8]

        # Log request details (but don't log sensitive headers)
        logger.info(f"[{request.request_id}] {request.method} {request.path}")

        # Only log body for non-sensitive endpoints
        if request.body and not any(sensitive in request.path for sensitive in ['/auth/', '/login/', '/signup/']):
            try:
                body = json.loads(request.body.decode('utf-8'))
                # Remove sensitive fields
                safe_body = {k: v for k, v in body.items() if k not in ['password', 'token', 'otp_code', 'verification_code', 'confirm_password']}
                if safe_body:
                    logger.info(f"[{request.request_id}] Body: {safe_body}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.info(f"[{request.request_id}] Body: Non-JSON data")

    def process_response(self, request, response):
        if hasattr(request, 'start_time') and hasattr(request, 'request_id'):
            duration = time.time() - request.start_time
            logger.info(f"[{request.request_id}] Response: {response.status_code} - Duration: {duration:.3f}s")

        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Global error handling middleware that doesn't interfere with DRF authentication
    """

    def process_exception(self, request, exception):
        # Let DRF handle its own authentication exceptions
        if 'rest_framework' in str(type(exception).__module__):
            return None

        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)

        # Only handle non-DRF exceptions
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'message': 'Please try again later or contact support',
            'status_code': 500
        }, status=500)