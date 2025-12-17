# createsonline/routing.py
"""
CREATESONLINE Unique Routing System

A completely different approach to routing.
Uses a declarative, intelligence-based routing system.
"""

import asyncio
import logging
from typing import Dict, Any, List, Callable
from datetime import datetime

# Setup logging
logger = logging.getLogger("createsonline.routing")


class CreatesonlineRoute:
    """
    Individual route definition with AI-enhanced capabilities.
    This uses a declarative approach.
    """
    
    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: List[str] = ["GET"],
        name: str = None,
        description: str = None,
        tags: List[str] = None,
        ai_enhanced: bool = False
    ):
        self.path = path
        self.handler = handler
        self.methods = [m.upper() for m in methods]
        self.name = name or f"{path.replace('/', '_').strip('_')}"
        self.description = description
        self.tags = tags or []
        self.ai_enhanced = ai_enhanced
        self.stats = {
            'requests': 0,
            'errors': 0,
            'avg_response_time': 0,
            'last_called': None
        }
    
    def matches_path(self, path: str) -> Dict[str, str]:
        """Check if route matches path and extract parameters"""
        # Handle wildcard paths like /static/*, /css/*, /js/*
        if self.path.endswith('/*') or self.path.endswith('/{path:path}'):
            route_prefix = self.path.replace('/*', '').replace('/{path:path}', '')
            if path.startswith(route_prefix):
                remaining = path[len(route_prefix):].lstrip('/')
                return {'wildcard': remaining, 'path': remaining}
        
        # Handle path parameters {param}
        if '{' in self.path:
            path_parts = self.path.split('/')
            url_parts = path.split('/')
            
            if len(path_parts) == len(url_parts):
                params = {}
                for i, part in enumerate(path_parts):
                    if part.startswith('{') and part.endswith('}'):
                        param_name = part[1:-1].split(':')[0]  # Handle {name:type}
                        params[param_name] = url_parts[i]
                    elif part != url_parts[i]:
                        return None
                return params
        
        # Simple exact match
        if self.path == path:
            return {}
        return None
    
    async def execute(self, request: Dict[str, Any]) -> Any:
        """Execute the route handler with timing and error tracking"""
        start_time = datetime.utcnow()
        
        try:
            self.stats['requests'] += 1
            
            # Execute handler (sync or async)
            if asyncio.iscoroutinefunction(self.handler):
                result = await self.handler(request)
            else:
                result = self.handler(request)
            
            # Update timing stats
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['requests'] - 1) + response_time) 
                / self.stats['requests']
            )
            self.stats['last_called'] = end_time.isoformat()
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            raise e


class CreatesonlineRouter:
    """
    CREATESONLINE's unique routing system.
    
    This uses a unique approach to routing.
    this uses an intelligent registry system with built-in analytics.
    """
    
    def __init__(self):
        self.routes: List[CreatesonlineRoute] = []
        self.middleware: List[Callable] = []
        self.global_stats = {
            'total_requests': 0,
            'total_errors': 0,
            'start_time': datetime.utcnow()
        }
        self.static_file_handler = None  # Will be set later
    
    def register(
        self,
        path: str,
        handler: Callable,
        methods: List[str] = ["GET"],
        **kwargs
    ) -> CreatesonlineRoute:
        """Register a new route with the router"""
        route = CreatesonlineRoute(path, handler, methods, **kwargs)
        self.routes.append(route)
        return route
    
    def GET(self, path: str, **kwargs):
        """Shorthand for GET route registration"""
        def decorator(handler):
            return self.register(path, handler, ["GET"], **kwargs)
        return decorator
    
    def POST(self, path: str, **kwargs):
        """Shorthand for POST route registration"""
        def decorator(handler):
            return self.register(path, handler, ["POST"], **kwargs)
        return decorator
    
    def PUT(self, path: str, **kwargs):
        """Shorthand for PUT route registration"""
        def decorator(handler):
            return self.register(path, handler, ["PUT"], **kwargs)
        return decorator
    
    def DELETE(self, path: str, **kwargs):
        """Shorthand for DELETE route registration"""
        def decorator(handler):
            return self.register(path, handler, ["DELETE"], **kwargs)
        return decorator
    
    def PATCH(self, path: str, **kwargs):
        """Shorthand for PATCH route registration"""
        def decorator(handler):
            return self.register(path, handler, ["PATCH"], **kwargs)
        return decorator
    
    def OPTIONS(self, path: str, **kwargs):
        """Shorthand for OPTIONS route registration"""
        def decorator(handler):
            return self.register(path, handler, ["OPTIONS"], **kwargs)
        return decorator
    
    def HEAD(self, path: str, **kwargs):
        """Shorthand for HEAD route registration"""
        def decorator(handler):
            return self.register(path, handler, ["HEAD"], **kwargs)
        return decorator
    
    def AI(self, path: str, methods: List[str] = ["GET"], **kwargs):
        """Register an AI-enhanced route"""
        def decorator(handler):
            kwargs['ai_enhanced'] = True
            kwargs['tags'] = kwargs.get('tags', []) + ['ai']
            return self.register(path, handler, methods, **kwargs)
        return decorator
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to the router"""
        self.middleware.append(middleware)
    
    def _is_static_file(self, path: str) -> bool:
        """Check if path looks like a static file"""
        static_extensions = {
            '.html', '.htm', '.css', '.js', '.json', '.xml',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
            '.woff', '.woff2', '.ttf', '.eot',
            '.pdf', '.txt', '.md',
            '.mp4', '.webm', '.mp3', '.wav'
        }
        
        # Check if path has a static extension
        for ext in static_extensions:
            if path.endswith(ext):
                return True
        
        # Check if path starts with common static prefixes
        static_prefixes = ['/static/', '/css/', '/js/', '/images/', '/img/', '/assets/', '/media/', '/files/']
        for prefix in static_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    async def _serve_static_file(self, path: str) -> Any:
        """Serve a static file dynamically"""
        try:
            # Initialize static handler if not already done
            if self.static_file_handler is None:
                from createsonline.static_files import static_handler
                self.static_file_handler = static_handler
            
            # Serve the file
            content, status_code, headers = self.static_file_handler.serve_file(path)
            
            return content, status_code, headers
            
        except Exception as e:
            logger.error(f"Error serving static file {path}: {e}")
            return {"error": f"Failed to serve file: {str(e)}"}, 500
    
    async def route(self, request: Dict[str, Any]) -> Any:
        """
        Main routing logic
        Uses intelligent matching and built-in analytics.
        """
        path = request.get('path', '/')
        method = request.get('method', 'GET').upper()
        
        # Update global stats
        self.global_stats['total_requests'] += 1
        
        # Auto-detect and serve static files (HTML, CSS, JS, images, etc.)
        if self._is_static_file(path):
            return await self._serve_static_file(path)
        
        # Find matching route
        matching_route = None
        path_params = {}
        for route in self.routes:
            params = route.matches_path(path)
            if params is not None and method in route.methods:
                matching_route = route
                path_params = params
                break
        
        if not matching_route:
            self.global_stats['total_errors'] += 1
            return {
                'error': 'Route not found',
                'path': path,
                'method': method,
                'available_routes': [
                    {
                        'path': r.path,
                        'methods': r.methods,
                        'name': r.name
                    } for r in self.routes
                ]
            }, 404
        
        # Apply middleware
        for middleware in self.middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    modified_request = await middleware(request)
                else:
                    modified_request = middleware(request)
                
                # Support early exit from middleware
                if modified_request is None:
                    # Middleware wants to short-circuit
                    return {"error": "Request blocked by middleware"}, 403
                    
                request = modified_request
            except Exception as e:
                logger.exception(f"Middleware error: {e}")
                return {"error": "Middleware processing failed"}, 500
        
        # Add path parameters to request
        if path_params:
            request['path_params'] = path_params
        
        # Execute route
        try:
            result = await matching_route.execute(request)
            
            # Apply security headers if they were set by middleware
            if 'security_headers' in request:
                if isinstance(result, tuple) and len(result) >= 2:
                    # Result is (data, status_code, headers)
                    data, status_code = result[0], result[1]
                    existing_headers = result[2] if len(result) > 2 else {}
                    # Merge security headers with existing headers
                    merged_headers = {**request['security_headers'], **existing_headers}
                    return data, status_code, merged_headers
                else:
                    # Result is just data, add security headers
                    return result, 200, request['security_headers']
            
            # Return result as-is if it's a tuple, or default to 200 status
            if isinstance(result, tuple):
                return result
            return result, 200
        except Exception as e:
            self.global_stats['total_errors'] += 1
            return {
                'error': str(e),
                'route': matching_route.name,
                'path': path
            }, 500
    
    def get_route_stats(self) -> Dict[str, Any]:
        """Get detailed routing statistics"""
        route_stats = []
        for route in self.routes:
            route_stats.append({
                'path': route.path,
                'name': route.name,
                'methods': route.methods,
                'stats': route.stats,
                'ai_enhanced': route.ai_enhanced,
                'tags': route.tags
            })
        
        uptime = (datetime.utcnow() - self.global_stats['start_time']).total_seconds()
        
        return {
            'global_stats': {
                **self.global_stats,
                'uptime_seconds': uptime,
                'error_rate': (
                    self.global_stats['total_errors'] / 
                    max(self.global_stats['total_requests'], 1)
                ) * 100
            },
            'route_stats': route_stats,
            'total_routes': len(self.routes),
            'ai_routes': len([r for r in self.routes if r.ai_enhanced])
        }
    
    def generate_api_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI-like specification"""
        paths = {}
        
        for route in self.routes:
            if route.path not in paths:
                paths[route.path] = {}
            
            for method in route.methods:
                # Basic response definition
                response_def = {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'}
                        }
                    }
                }
                
                # Include common security headers that may be added by middleware
                # Note: These are added by security middleware, not per-route
                response_def['headers'] = {
                    'X-Content-Type-Options': {
                        'description': 'MIME type sniffing prevention (added by security middleware)',
                        'schema': {'type': 'string', 'example': 'nosniff'}
                    },
                    'X-Frame-Options': {
                        'description': 'Clickjacking protection (added by security middleware)',
                        'schema': {'type': 'string', 'example': 'DENY'}
                    },
                    'X-XSS-Protection': {
                        'description': 'XSS protection (added by security middleware)',
                        'schema': {'type': 'string', 'example': '1; mode=block'}
                    }
                }
                
                paths[route.path][method.lower()] = {
                    'summary': route.name.replace('_', ' ').title(),
                    'description': route.description or f"{method} {route.path}",
                    'tags': route.tags,
                    'x-ai-enhanced': route.ai_enhanced,
                    'responses': {
                        '200': response_def
                    }
                }
        
        from . import __version__
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'CREATESONLINE API',
                'version': __version__,
                'description': 'AI-Native Web Framework API with Intelligent Routing',
                'x-framework': 'CREATESONLINE',
                'x-routing-system': 'Intelligence-Based'
            },
            'paths': paths,
            'x-route-stats': self.get_route_stats()
        }


class IntelligentMiddleware:
    """
    Middleware system that's different from typical frameworks.
    Uses AI-like decision making for request processing.
    """
    
    @staticmethod
    def request_logger(request: Dict[str, Any]) -> Dict[str, Any]:
        """Log requests with intelligent filtering"""
        # Skip logging for health checks and static files
        path = request.get('path', '')
        if path in ['/health', '/favicon.ico'] or path.startswith('/static/'):
            return request
        
        logger.info(f"{request.get('method', 'GET')} {path}")
        return request
    
    @staticmethod
    def security_headers(request: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers intelligently"""
        request['security_headers'] = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            'X-Framework': 'CREATESONLINE-AI'
        }
        return request
    
    @staticmethod
    async def ai_request_analyzer(request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requests using AI-like logic"""
        path = request.get('path', '')
        
        # Detect API endpoints
        if path.startswith('/api/') or path.endswith('.json'):
            request['content_type'] = 'application/json'
        
        # Detect admin requests
        if path.startswith('/admin/'):
            request['requires_auth'] = True
        
        # Add intelligent suggestions
        if path == '/documentation' or path == '/docs':
            request['suggested_redirect'] = '/docs'
        
        return request


# Global router instance
router = CreatesonlineRouter()

# Add default middleware
router.add_middleware(IntelligentMiddleware.request_logger)
router.add_middleware(IntelligentMiddleware.security_headers)


# Helper functions for easy routing
def path(route: str, view, methods: List[str] = None, name: str = None):
    """
    Django-style path() helper for defining routes
    
    Usage:
        from createsonline.routing import path
        from myapp import views
        
        urlpatterns = [
            path('/', views.home),
            path('/api/users', views.UserListView.as_view()),
            path('/api/users/{id}', views.UserDetailView.as_view(), name='user-detail'),
        ]
    """
    methods = methods or ['GET']
    
    # Handle class-based views
    if hasattr(view, 'as_view'):
        view = view.as_view()
    
    return CreatesonlineRoute(
        path=route,
        handler=view,
        methods=methods,
        name=name
    )


def include(module_path: str):
    """
    Include routes from another module
    
    Usage:
        from createsonline.routing import path, include
        
        urlpatterns = [
            path('/api/', include('myapp.api.routes')),
            path('/admin/', include('myapp.admin.routes')),
        ]
    """
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, 'urlpatterns', [])


def register_routes(app, urlpatterns: List[CreatesonlineRoute]):
    """
    Register a list of URL patterns with the app
    
    Usage:
        from createsonline import create_app
        from createsonline.routing import register_routes
        from . import routes
        
        app = create_app()
        register_routes(app, routes.urlpatterns)
    """
    for route in urlpatterns:
        if isinstance(route, list):
            # Handle included routes
            register_routes(app, route)
        elif isinstance(route, CreatesonlineRoute):
            # Register the route
            for method in route.methods:
                if hasattr(app, method.lower()):
                    decorator = getattr(app, method.lower())
                    decorator(route.path)(route.handler)


# Export main components
__all__ = [
    'CreatesonlineRoute',
    'CreatesonlineRouter',
    'IntelligentMiddleware',
    'router',
    'path',
    'include',
    'register_routes'
]
