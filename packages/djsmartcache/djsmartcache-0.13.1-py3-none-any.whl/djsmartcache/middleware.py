from django.utils.deprecation import MiddlewareMixin

class SmartCacheMiddleware(MiddlewareMixin):
    """A placeholder middleware to allow request-scoped hooks later."""

    def process_request(self, request):
        return None

    def process_response(self, request, response):
        return response
