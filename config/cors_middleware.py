"""Custom CORS middleware to ensure headers are always added."""
from django.http import HttpResponse


class SimpleCorsMiddleware:
    """Add CORS headers to all responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle OPTIONS preflight requests immediately
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Accept, Authorization, Content-Type, X-CSRFToken"
            response["Access-Control-Max-Age"] = "86400"
            return response
        
        # Process normal requests
        response = self.get_response(request)
        
        # Add CORS headers to all responses
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Authorization, Content-Type, X-CSRFToken"
        response["Access-Control-Max-Age"] = "86400"
        
        return response
