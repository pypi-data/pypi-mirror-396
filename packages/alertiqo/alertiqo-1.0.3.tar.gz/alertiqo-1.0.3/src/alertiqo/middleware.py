"""Middleware for web frameworks."""

from typing import Callable
from .client import Alertiqo


def alertiqo_middleware(alertiqo: Alertiqo):
    """
    WSGI middleware for Flask/Django.
    
    Usage with Flask:
        app.wsgi_app = alertiqo_middleware(alertiqo)(app.wsgi_app)
    
    Usage with Django (in settings.py):
        MIDDLEWARE = [
            'alertiqo.middleware.AlertiqoDjangoMiddleware',
            ...
        ]
    """
    def middleware(app):
        def wrapper(environ, start_response):
            try:
                return app(environ, start_response)
            except Exception as e:
                alertiqo.add_breadcrumb(
                    message=f"{environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')}",
                    category="http",
                    level="info",
                    data={
                        "method": environ.get("REQUEST_METHOD"),
                        "path": environ.get("PATH_INFO"),
                        "query": environ.get("QUERY_STRING"),
                    }
                )
                alertiqo.capture_exception(e, {
                    "tags": {
                        "route": environ.get("PATH_INFO", ""),
                        "method": environ.get("REQUEST_METHOD", ""),
                    }
                })
                raise
        return wrapper
    return middleware


class AlertiqoDjangoMiddleware:
    """Django middleware for Alertiqo error tracking."""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.alertiqo = None

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Process exceptions and send to Alertiqo."""
        if self.alertiqo:
            self.alertiqo.add_breadcrumb(
                message=f"{request.method} {request.path}",
                category="http",
                level="info",
                data={
                    "method": request.method,
                    "path": request.path,
                    "query": request.GET.dict(),
                }
            )
            self.alertiqo.capture_exception(exception, {
                "tags": {
                    "route": request.path,
                    "method": request.method,
                }
            })
        return None
