# createsonline/middleware.py
"""
CREATESONLINE Middleware System

Base classes and standard middleware implementations.
"""
from typing import Any, Optional, Callable, Awaitable

class BaseMiddleware:
    """Base class for all middleware"""
    
    async def before_request(self, request: Any) -> Optional[Any]:
        """
        Called before the request is handled by the route.
        Return a response object to intercept the request, or None to continue.
        """
        return None
        
    async def after_request(self, request: Any, response: Any) -> Any:
        """
        Called after the request is handled.
        Must return the response object (modified or original).
        """
        return response

class CORSMiddleware(BaseMiddleware):
    """Cross-Origin Resource Sharing (CORS) Middleware"""
    
    def __init__(self, allow_origins: list = None, allow_methods: list = None, allow_headers: list = None):
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        
    async def before_request(self, request):
        if request.method == "OPTIONS":
            # Handle preflight request
            from .server import InternalResponse
            headers = self._get_cors_headers()
            return InternalResponse(content="", status_code=204, headers=headers)
        return None
        
    async def after_request(self, request, response):
        # Add CORS headers to response
        cors_headers = self._get_cors_headers()
        
        # Handle dict response
        if isinstance(response, dict):
            # Can't easily add headers to dict response without wrapping it
            # Ideally, app.py should handle this, but for now we can't modify dict easily
            pass 
        # Handle InternalResponse
        elif hasattr(response, 'headers'):
            for k, v in cors_headers.items():
                response.headers[k] = v
                
        return response

    def _get_cors_headers(self):
        return {
            "Access-Control-Allow-Origin": ", ".join(self.allow_origins),
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
        }
