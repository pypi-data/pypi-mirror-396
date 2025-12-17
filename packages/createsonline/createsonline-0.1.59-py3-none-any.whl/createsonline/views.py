# createsonline/views.py
"""
CREATESONLINE Views Module

Base view functions and utilities.
Users can import and extend these, or create their own views.
"""

import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json
from . import __version__

logger = logging.getLogger("createsonline.views")


class BaseView:
    """Base class for class-based views"""
    
    async def dispatch(self, request: Dict[str, Any]):
        """Dispatch request to appropriate method handler"""
        method = request.get('method', 'GET').lower()
        handler = getattr(self, method, self.http_method_not_allowed)
        
        if callable(handler):
            return await handler(request)
        return await self.http_method_not_allowed(request)
    
    async def http_method_not_allowed(self, request: Dict[str, Any]):
        """Return 405 Method Not Allowed"""
        return {
            "error": "Method not allowed",
            "allowed_methods": self.allowed_methods()
        }, 405
    
    def allowed_methods(self):
        """Return list of allowed HTTP methods"""
        methods = []
        for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
            if hasattr(self, method) and callable(getattr(self, method)):
                methods.append(method.upper())
        return methods


class TemplateView(BaseView):
    """View that renders a template"""
    
    template_name: str = None
    
    def __init__(self, template_name: str = None):
        if template_name:
            self.template_name = template_name
    
    async def get_context_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Override this to provide template context"""
        return {}
    
    async def get(self, request: Dict[str, Any]):
        """Handle GET request - render template"""
        if not self.template_name:
            return {"error": "template_name not set"}, 500
        
        context = await self.get_context_data(request)
        # This will be handled by the template system
        return {"template": self.template_name, "context": context}


class JSONView(BaseView):
    """View that returns JSON data"""
    
    async def get_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Override this to provide JSON data"""
        return {}
    
    async def get(self, request: Dict[str, Any]):
        """Handle GET request - return JSON"""
        data = await self.get_data(request)
        return data


class ListView(JSONView):
    """View that returns a list of items"""
    
    async def get_queryset(self, request: Dict[str, Any]) -> list:
        """Override this to provide the list of items"""
        return []
    
    async def get_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Return paginated list data"""
        items = await self.get_queryset(request)
        
        # Simple pagination
        page = int(request.get('query_params', {}).get('page', 1))
        page_size = int(request.get('query_params', {}).get('page_size', 20))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "items": items[start:end],
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "has_next": end < len(items),
            "has_previous": page > 1
        }


class DetailView(JSONView):
    """View that returns a single item"""
    
    async def get_object(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Override this to provide the item"""
        return None
    
    async def get_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Return single item data"""
        obj = await self.get_object(request)
        if obj is None:
            return {"error": "Not found"}, 404
        return obj


# Function-based view decorators
def json_response(func: Callable):
    """Decorator to ensure function returns JSON response"""
    async def wrapper(request: Dict[str, Any]):
        result = await func(request) if callable(func) else func(request)
        if not isinstance(result, dict):
            result = {"data": result}
        return result
    return wrapper


def require_method(*methods: str):
    """Decorator to restrict view to specific HTTP methods"""
    def decorator(func: Callable):
        async def wrapper(request: Dict[str, Any]):
            if request.get('method', 'GET').upper() not in [m.upper() for m in methods]:
                return {"error": f"Method not allowed. Allowed: {', '.join(methods)}"}, 405
            return await func(request) if callable(func) else func(request)
        wrapper.allowed_methods = [m.upper() for m in methods]
        return wrapper
    return decorator


# Common view functions
async def index_view(request: Dict[str, Any]):
    """Default index view - renders index.html"""
    return {"template": "index.html", "context": {}}


async def health_check_view(request: Dict[str, Any]):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "framework": "CREATESONLINE",
        "version": __version__
    }


async def not_found_view(request: Dict[str, Any]):
    """404 Not Found view"""
    return {
        "error": "Not Found",
        "path": request.get('path', ''),
        "message": "The requested resource was not found"
    }, 404


# Export commonly used views
__all__ = [
    'BaseView',
    'TemplateView',
    'JSONView',
    'ListView',
    'DetailView',
    'json_response',
    'require_method',
    'index_view',
    'health_check_view',
    'not_found_view'
]
