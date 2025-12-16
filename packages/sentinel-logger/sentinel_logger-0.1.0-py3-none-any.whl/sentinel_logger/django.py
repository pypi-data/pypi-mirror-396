"""Django middleware wrapper for SentinelLogger"""
from django.conf import settings
from .middleware import SentinelLogger as WSGISentinel

class SentinelMiddleware:
    """
    Django middleware. Add to settings.py MIDDLEWARE list:
    
    MIDDLEWARE = [
        'sentinel_logger.django.SentinelMiddleware',
        ...
    ]
    SENTINEL_API_KEY = "your-key"
    SENTINEL_URL = "https://..."  # optional
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        api_key = getattr(settings, "SENTINEL_API_KEY", None)
        url = getattr(settings, "SENTINEL_URL", None)
        
        if not api_key:
            raise ValueError("SENTINEL_API_KEY required in settings")
        
        # Wrap the Django WSGI handler
        from django.core.handlers.wsgi import WSGIHandler
        handler = WSGIHandler()
        kwargs = {"api_key": api_key}
        if url:
            kwargs["url"] = url
        self.sentinel = WSGISentinel(handler, **kwargs)
    
    def __call__(self, request):
        return self.get_response(request)
    