# createsonline/config/app.py
"""
CREATESONLINE Application Factory

The main application factory for the CREATESONLINE framework.
Built for AI-native web development.

Supports Python 3.9 through 3.13 with zero external dependencies.
"""
from typing import Dict, Any, Optional, List, Callable
import sys
import json
from datetime import datetime
from urllib.parse import parse_qs

# Python version check (3.9-3.13 support)
if sys.version_info < (3, 9) or sys.version_info >= (3, 14):
    raise RuntimeError(f"CREATESONLINE supports Python 3.9-3.13. Current: {sys.version}")

# Import from extracted modules
from .errors import HTTPException, ErrorPageGenerator
from .request import CreatesonlineInternalRequest
from .docs import APIDocumentationGenerator


class CreatesonlineApp:
    """
    CREATESONLINE Framework Application
    
    The main application class for building AI-native web applications.
    Pure internal implementation with zero external dependencies.
    
    Features:
    - Pure AI-native routing and middleware
    - Built-in admin interface
    - User management system
    - Intelligent request/response handling
    - Automatic API documentation
    - Vector search capabilities
    - LLM integration ready
    - Complete internal implementation
    """
    
    def __init__(
        self,
        title: str = "CREATESONLINE Application",
        description: str = "Built with CREATESONLINE - The AI-Native Framework",
        version: str = "1.0.0",
        ai_config: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        cors_origins: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize CREATESONLINE application
        
        Args:
            title: Application title
            description: Application description  
            version: Application version
            ai_config: AI configuration dictionary
            debug: Enable debug mode
            cors_origins: Allowed CORS origins
            **kwargs: Additional configuration options
        """
        # Core application metadata
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.ai_config = ai_config or {}
        
        # Internal application state
        self._routes: List[Dict[str, Any]] = []
        self._middleware: List[Dict[str, Any]] = []
        self._startup_handlers: List[Callable] = []
        self._shutdown_handlers: List[Callable] = []
        
        # AI features registry
        self._ai_features: List[str] = []
        
        # Internal routing system
        self._internal_routes = {}
        
        # Initialize pure internal application
        self._setup_internal_app(cors_origins)
        
        # Setup framework routes (works with both implementations)
        self._setup_framework_routes()
        self._setup_error_handlers()
    
    @property
    def routes(self):
        """Backward compatibility property for _internal_routes"""
        return self._internal_routes
    
    def _setup_internal_app(self, cors_origins: Optional[List[str]] = None):
        """Setup internal ASGI application"""
        
        # Store CORS configuration for internal implementation
        self._cors_origins = cors_origins or (["*"] if self.debug else [])
        self._enable_gzip = True
    
    def _setup_framework_routes(self):
        """Setup built-in CREATESONLINE routes"""
        
        # Framework root endpoint
        @self.get("/")
        async def root_endpoint(request):
            return await self._root_endpoint(request)
        
        # Health check
        @self.get("/health")
        async def health_endpoint(request):
            return await self._health_endpoint(request)
        
        # Framework info
        @self.get("/framework/info")
        async def framework_info_endpoint(request):
            return await self._framework_info_endpoint(request)

        # API docs
        @self.get("/docs")
        async def docs_endpoint(request):
            generator = APIDocumentationGenerator(self)
            return generator.generate_beautiful_api_docs()

        # Alias for /doc
        @self.get("/doc")
        async def doc_redirect(request):
            try:
                from createsonline.server import InternalResponse
                return InternalResponse(b"", status_code=302, headers={"Location": "/docs"})
            except Exception:
                return {"redirect": "/docs"}, 302
    
    def _setup_error_handlers(self):
        """Setup CREATESONLINE error handling - pure internal implementation"""
        # Error handling is now done in the internal ASGI handler
        pass
    
    async def _root_endpoint(self, request) -> Dict[str, Any]:
        """CREATESONLINE framework root endpoint"""
        return {
            "framework": "CREATESONLINE",
            "application": self.title,
            "version": self.version,
            "tagline": "Build Intelligence Into Everything",
            "status": "operational",
            "mode": "internal",
            "timestamp": datetime.utcnow().isoformat(),
            "admin_interface": "/admin",
            "api_documentation": "/docs",
            "health_check": "/health",
            "ai_enabled": len(self._ai_features) > 0,
            "ai_features": self._ai_features,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "supported_python": "3.9-3.13"
        }
    
    async def _health_endpoint(self, request) -> Dict[str, Any]:
        """CREATESONLINE health check endpoint"""
        return {
            "status": "healthy",
            "framework": "CREATESONLINE",
            "version": self.version,
            "mode": "internal",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_enabled": len(self._ai_features) > 0,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "system_checks": {
                "database": "ready",
                "ai_services": "operational",
                "memory": "optimal",
                "internal_asgi": True
            }
        }
    
    async def _framework_info_endpoint(self, request) -> Dict[str, Any]:
        """CREATESONLINE framework information endpoint"""
        return {
            "framework": {
                "name": "CREATESONLINE",
                "version": self.version,
                "description": self.description,
                "tagline": "Build Intelligence Into Everything",
                "architecture": "AI-Native",
                "foundation": "Internal ASGI",
                "python_support": "3.9-3.13"
            },
            "application": {
                "title": self.title,
                "version": self.version,
                "debug": self.debug
            },
            "ai_configuration": self.ai_config,
            "enabled_features": self._ai_features,
            "dependencies": {
                "pure_internal": True,
                "external_ai": self._check_external_ai(),
                "mode": "core"
            },
            "capabilities": [
                "AI-Enhanced Fields",
                "Built-in Admin Interface", 
                "User Management System",
                "Natural Language Queries",
                "Vector Similarity Search",
                "LLM Integration",
                "Smart Routing",
                "Intelligent Middleware",
                "Pure Python Core"
            ],
            "endpoints": {
                "admin": "/admin",
                "health": "/health",
                "api_spec": "/docs"
            }
        }
    
    def _generate_api_paths(self) -> Dict[str, Any]:
        """Generate OpenAPI paths from routes"""
        paths = {}
        for route_key in self._internal_routes.keys():
            method, path = route_key.split(':', 1)
            if path not in paths:
                paths[path] = {}
            paths[path][method.lower()] = {
                "summary": f"{method} {path}",
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        return paths
    
    def _check_external_ai(self) -> bool:
        """Check if external AI services are available"""
        try:
            import openai
            return True
        except ImportError:
            return False
    
    # ========================================
    # CREATESONLINE ROUTING API
    # ========================================
    
    def get(self, path: str, **kwargs) -> Callable:
        """CREATESONLINE GET route decorator"""
        return self._add_route("GET", path, **kwargs)
    
    def post(self, path: str, **kwargs) -> Callable:
        """CREATESONLINE POST route decorator"""
        return self._add_route("POST", path, **kwargs)
    
    def put(self, path: str, **kwargs) -> Callable:
        """CREATESONLINE PUT route decorator"""
        return self._add_route("PUT", path, **kwargs)
    
    def delete(self, path: str, **kwargs) -> Callable:
        """CREATESONLINE DELETE route decorator"""
        return self._add_route("DELETE", path, **kwargs)
    
    def route(
        self, 
        path: str, 
        methods: Optional[List[str]] = None, 
        **kwargs
    ) -> Callable:
        """CREATESONLINE multi-method route decorator"""
        if methods is None:
            methods = ["GET"]
        
        def decorator(func: Callable) -> Callable:
            for method in methods:
                self._add_route_internal(method.upper(), path, func, **kwargs)
            return func
        return decorator
    
    def _add_route(self, method: str, path: str, **kwargs) -> Callable:
        """Add route to router"""
        def decorator(func: Callable) -> Callable:
            self._add_route_internal(method, path, func, **kwargs)
            return func
        return decorator
    
    def _add_route_internal(self, method: str, path: str, func: Callable, **kwargs):
        """Internal route registration"""
        route_key = f"{method}:{path}"
        
        # Store in internal router only
        self._internal_routes[route_key] = func
    
    
    # ========================================
    # CREATESONLINE MIDDLEWARE & EVENTS
    # ========================================
    
    def middleware(self, middleware_type: str = "http") -> Callable:
        """Add custom middleware to CREATESONLINE application"""
        def decorator(func: Callable) -> Callable:
            self._middleware.append({
                "type": middleware_type,
                "func": func
            })
            return func
        return decorator
    
    def on_startup(self, func: Callable) -> Callable:
        """Register CREATESONLINE startup event handler"""
        self._startup_handlers.append(func)
        return func
    
    def on_shutdown(self, func: Callable) -> Callable:
        """Register CREATESONLINE shutdown event handler"""
        self._shutdown_handlers.append(func)
        return func
    
    def get_routes(self) -> List[str]:
        """Get list of all registered routes"""
        routes = set()
        for route_key in self._internal_routes.keys():
            # Extract path from "METHOD:path" format
            if ':' in route_key:
                path = route_key.split(':', 1)[1]
                routes.add(path)
        return sorted(list(routes))
    
    # ========================================
    # CREATESONLINE AI FEATURES
    # ========================================
    
    def enable_ai_features(self, features: List[str]) -> 'CreatesonlineApp':
        """Enable AI features in CREATESONLINE application"""
        for feature in features:
            if feature not in self._ai_features:
                self._ai_features.append(feature)
                
                # Setup feature-specific routes
                self._setup_ai_feature_routes(feature)
        
        return self
    
    def _setup_ai_feature_routes(self, feature: str):
        """Setup AI feature-specific routes"""
        if feature == "smart_query":
            @self.get("/ai/query/{model:str}")
            async def smart_query_endpoint(request):
                return await self._smart_query_handler(request)
        
        elif feature == "content_generation":
            @self.post("/ai/generate")
            async def content_generation_endpoint(request):
                return await self._content_generation_handler(request)
        
        elif feature == "vector_search":
            @self.get("/ai/search")
            async def vector_search_endpoint(request):
                return await self._vector_search_handler(request)
        
        elif feature == "model_serving":
            @self.post("/ai/predict")
            async def model_prediction_endpoint(request):
                return await self._model_prediction_handler(request)
        
        elif feature == "admin_ai":
            @self.get("/admin/ai")
            async def admin_ai_dashboard(request):
                return await self._admin_ai_handler(request)
    
    async def _smart_query_handler(self, request):
        """Handle smart query requests"""
        model = request.path_params.get('model', 'unknown')
        return {
            "framework": "CREATESONLINE",
            "feature": "smart_query",
            "mode": "internal",
            "model": model,
            "result": f"Smart query processed with CREATESONLINE AI using model: {model}"
        }
    
    async def _content_generation_handler(self, request):
        """Handle content generation requests"""
        return {
            "framework": "CREATESONLINE",
            "feature": "content_generation",
            "mode": "internal",
            "generated_content": "CREATESONLINE AI generated content"
        }
    
    async def _vector_search_handler(self, request):
        """Handle vector search requests"""
        return {
            "framework": "CREATESONLINE",
            "feature": "vector_search",
            "mode": "internal",
            "results": []
        }
    
    async def _model_prediction_handler(self, request):
        """Handle model prediction requests"""
        return {
            "framework": "CREATESONLINE",
            "feature": "model_serving",
            "mode": "internal",
            "prediction": 0.87
        }
    
    async def _admin_ai_handler(self, request):
        """Handle admin AI dashboard requests"""
        return {
            "framework": "CREATESONLINE",
            "feature": "admin_ai",
            "mode": "internal",
            "ai_dashboard": "AI-enhanced admin interface"
        }
    
    # ========================================
    # ASGI INTERFACE
    # ========================================
    
    async def __call__(self, scope, receive, send):
        """
        CREATESONLINE ASGI callable interface
        
        Pure internal ASGI implementation
        """
        # Execute startup handlers if this is the first request
        if not getattr(self, '_startup_executed', False):
            for handler in self._startup_handlers:
                await handler()
            self._startup_executed = True
            
        # Use internal ASGI implementation
        await self._internal_asgi_handler(scope, receive, send)
    
    async def _internal_asgi_handler(self, scope, receive, send):
        """Internal ASGI handler for zero-dependency mode"""
        
        if scope['type'] == 'http':
            await self._handle_internal_http(scope, receive, send)
        elif scope['type'] == 'websocket':
            await self._handle_internal_websocket(scope, receive, send)
    
    async def _handle_internal_http(self, scope, receive, send):
        """Handle HTTP requests with internal router"""
        
        # On first request, discover routes from routes.py to override decorators
        if getattr(self, '_needs_route_discovery', False):
            try:
                from createsonline.project_init import auto_discover_routes
                auto_discover_routes(self)
                self._needs_route_discovery = False
            except Exception:
                self._needs_route_discovery = False
        
        path = scope['path']
        method = scope['method']
        
        # Serve static files first (favicon, logo, icons, CSS, JS, images)
        if method == 'GET' and (
            path.startswith('/icons/') or 
            path.startswith('/static/') or
            path in ['/favicon.ico', '/site.webmanifest'] or
            path.endswith(('.png', '.webp', '.jpg', '.jpeg', '.css', '.js', '.svg', '.ico'))
        ):
            await self._serve_static_file(path, scope, receive, send)
            return
        
        route_key = f"{method}:{path}"
        
        # Create internal request object
        request = CreatesonlineInternalRequest(scope, receive)
        
        try:
            # Find matching route - first try exact match
            handler = None
            path_params = {}
            
            if route_key in self._internal_routes:
                handler = self._internal_routes[route_key]
            else:
                # Try pattern matching for path parameters
                handler, path_params = self._match_parametric_route(method, path)
            
            if handler:
                # Add path parameters to the request
                request.path_params.update(path_params)
                response_data = await handler(request)
            else:
                # 404 handler
                accept_header = getattr(request, 'headers', {}).get('accept', '')
                user_agent = getattr(request, 'headers', {}).get('user-agent', '')
                
                # If browser request, return beautiful HTML error page
                if ('text/html' in accept_header or 'Mozilla' in user_agent):
                    error_html = self._generate_error_page(
                        status_code=404,
                        error_message="The requested page could not be found.",
                        path=path,
                        method=method,
                        details="This endpoint is not available or may have been moved."
                    )
                    await send({
                        'type': 'http.response.start',
                        'status': 404,
                        'headers': [
                            [b'content-type', b'text/html; charset=utf-8'],
                            [b'content-length', str(len(error_html.encode())).encode()],
                        ]
                    })
                    await send({
                        'type': 'http.response.body',
                        'body': error_html.encode()
                    })
                    return
                
                # Otherwise return JSON error
                response_data = {
                    "error": "Not Found",
                    "path": path,
                    "method": method,
                    "framework": "CREATESONLINE",
                    "mode": "internal",
                    "available_routes": list(self._internal_routes.keys())
                }
                status = 404
            
            # Send response
            await self._send_internal_response(send, response_data, status=locals().get('status', 200))
                
        except Exception as e:
            # Error handling
            accept_header = getattr(request, 'headers', {}).get('accept', '')
            user_agent = getattr(request, 'headers', {}).get('user-agent', '')
            
            # If browser request, return beautiful HTML error page
            if ('text/html' in accept_header or 'Mozilla' in user_agent):
                error_html = self._generate_error_page(
                    status_code=500,
                    error_message="An internal server error occurred.",
                    path=getattr(request, 'path', ''),
                    method=getattr(request, 'method', 'GET'),
                    details=str(e) if self.debug else "Please try again later or contact support."
                )
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                    'headers': [
                        [b'content-type', b'text/html; charset=utf-8'],
                        [b'content-length', str(len(error_html.encode())).encode()],
                    ]
                })
                await send({
                    'type': 'http.response.body',
                    'body': error_html.encode()
                })
                return
            
            # Otherwise return JSON error
            error_data = {
                "error": "Internal Server Error",
                "message": str(e) if self.debug else "Something went wrong",
                "framework": "CREATESONLINE",
                "mode": "internal"
            }
            await self._send_internal_response(send, error_data, status=500)
    
    async def _serve_static_file(self, path: str, scope, receive, send):
        """Serve static files using Django-style STATICFILES_DIRS"""
        from createsonline.static_files import static_handler
        
        # Use the static handler which respects STATICFILES_DIRS
        content, status, headers = static_handler.serve_file(path)
        
        # Convert headers dict to ASGI format
        asgi_headers = []
        for key, value in headers.items():
            asgi_headers.append([key.lower().encode(), str(value).encode()])
        
        # Send response
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': asgi_headers,
        })
        await send({
            'type': 'http.response.body',
            'body': content,
        })
    
    def _match_parametric_route(self, method: str, path: str):
        """Match path against parametric routes and extract parameters"""
        import re
        
        for route_key, handler in self._internal_routes.items():
            stored_method, route_pattern = route_key.split(':', 1)
            
            if stored_method != method:
                continue
            
            # Check if this route has path parameters
            if '{' not in route_pattern or '}' not in route_pattern:
                continue
            
            # Convert path pattern to regex
            # Handle {param} and {param:path} patterns
            regex_pattern = route_pattern
            path_params = {}
            
            # Find all parameter patterns
            param_matches = re.findall(r'\{([^}]+)\}', route_pattern)
            
            for param_match in param_matches:
                if ':' in param_match:
                    # Handle {param_name:path} or {param_name:type} patterns
                    param_name, param_type = param_match.split(':', 1)
                    if param_type == 'path':
                        # Match any path including slashes
                        regex_pattern = regex_pattern.replace(f'{{{param_match}}}', f'(?P<{param_name}>.+)')
                    else:
                        # Match segments without slashes  
                        regex_pattern = regex_pattern.replace(f'{{{param_match}}}', f'(?P<{param_name}>[^/]+)')
                else:
                    # Handle simple {param} patterns - match segments without slashes
                    param_name = param_match
                    regex_pattern = regex_pattern.replace(f'{{{param_match}}}', f'(?P<{param_name}>[^/]+)')
            
            # Try to match the path
            match = re.match(f'^{regex_pattern}$', path)
            if match:
                path_params = match.groupdict()
                return handler, path_params
        
        return None, {}
    
    async def _handle_internal_websocket(self, scope, receive, send):
        """Handle WebSocket connections (internal implementation)"""
        await send({'type': 'websocket.accept'})
        
        while True:
            message = await receive()
            if message['type'] == 'websocket.disconnect':
                break
            elif message['type'] == 'websocket.receive':
                await send({
                    'type': 'websocket.send',
                    'text': json.dumps({
                        "framework": "CREATESONLINE",
                        "mode": "internal",
                        "message": "WebSocket connected",
                        "received": message.get('text', '')
                    })
                })
    
    async def _send_internal_response(self, send, data, status=200):
        """Send response using internal ASGI implementation"""
        
        response_headers = {}
        
        # Handle different response types
        if hasattr(data, 'content') and hasattr(data, 'status_code'):
            # Handle Response objects (like FileResponse, HTMLResponse, etc.)
            content = data.content
            status = getattr(data, 'status_code', status)
            response_headers = getattr(data, 'headers', {})
            
            if isinstance(content, bytes):
                response_body = content
            elif isinstance(content, str):
                response_body = content.encode('utf-8')
            elif isinstance(content, (dict, list)):
                response_body = json.dumps(content, indent=2 if self.debug else None).encode('utf-8')
            else:
                response_body = str(content).encode('utf-8')
        elif isinstance(data, dict) or isinstance(data, list):
            # JSON response
            response_body = json.dumps(data, indent=2 if self.debug else None).encode('utf-8')
        elif isinstance(data, str):
            # Text/HTML response
            response_body = data.encode('utf-8')
        else:
            # Fallback
            response_body = str(data).encode('utf-8')
        
        # Build headers list
        headers = [
            [b'content-length', str(len(response_body)).encode()],
            [b'x-framework', b'CREATESONLINE'],
            [b'x-version', self.version.encode()],
            [b'x-mode', b'internal'],
        ]
        
        # Add response-specific headers first (from Response object)
        for key, value in response_headers.items():
            if isinstance(key, str):
                key = key.lower().encode()
            if isinstance(value, str):
                value = value.encode()
            headers.append([key, value])
        
        # Add default content-type if not set by Response object
        content_type_set = any(header[0] == b'content-type' for header in headers)
        if not content_type_set:
            if isinstance(data, dict) or isinstance(data, list):
                headers.append([b'content-type', b'application/json'])
            elif isinstance(data, str) and data.strip().startswith('<'):
                headers.append([b'content-type', b'text/html'])
            else:
                headers.append([b'content-type', b'text/plain'])
        
        # Add CORS headers
        if self._cors_origins and "*" in self._cors_origins:
            headers.extend([
                [b'access-control-allow-origin', b'*'],
                [b'access-control-allow-methods', b'GET, POST, PUT, DELETE, OPTIONS'],
                [b'access-control-allow-headers', b'*'],
            ])
        
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': headers,
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })
    
    # ========================================
    # CREATESONLINE UTILITIES
    # ========================================
    
    def get_routes_info(self) -> List[Dict[str, Any]]:
        """Get information about CREATESONLINE routes"""
        routes_info = []
        for route_key in self._internal_routes.keys():
            method, path = route_key.split(':', 1)
            routes_info.append({
                "path": path,
                "method": method,
                "framework": "CREATESONLINE",
                "mode": "internal"
            })
        return routes_info
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get current CREATESONLINE AI configuration"""
        return {
            "framework": "CREATESONLINE",
            "mode": "internal",
            "config": self.ai_config,
            "enabled_features": self._ai_features,
            "feature_count": len(self._ai_features),
            "external_ai_available": self._check_external_ai()
        }
    
    def _generate_beautiful_api_docs(self):
        """Generate beautiful HTML API documentation with dynamic backend data"""
        import json
        from datetime import datetime
        import platform
        import sys
        
        # Get comprehensive API spec data with real backend info
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "description": self.description,
                "version": self.version,
                "x-framework": "CREATESONLINE",
                "x-ai-enabled": len(self._ai_features) > 0,
                "x-mode": "internal",
                "x-timestamp": datetime.utcnow().isoformat(),
                "x-python-version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "x-platform": platform.system(),
                "x-architecture": platform.machine()
            },
            "servers": [
                {
                    "url": "/", 
                    "description": "CREATESONLINE Development Server",
                    "variables": {
                        "protocol": {"default": "http", "enum": ["http", "https"]},
                        "host": {"default": "127.0.0.1:8000"}
                    }
                }
            ],
            "paths": self._generate_enhanced_api_paths(),
            "components": {
                "schemas": self._generate_api_schemas(),
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    },
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer"
                    }
                }
            },
            "x-system-info": {
                "framework": "CREATESONLINE",
                "mode": "AI-Native",
                "features": self._ai_features,
                "total_routes": len(self._internal_routes),
                "ai_routes": len([r for r in self._internal_routes.keys() if 'ai' in r.lower()]),
                "admin_routes": len([r for r in self._internal_routes.keys() if 'admin' in r.lower()]),
                "startup_time": datetime.utcnow().isoformat(),
                "health_status": "operational",
                "debug_mode": self.debug
            }
        }
        
        # Advanced HTML template with dynamic backend data
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} - API Explorer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            /* CREATESONLINE Brand Colors */
            --primary: #000000;
            --secondary: #ffffff;
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            
            /* Gray Scale */
            --gray-50: #fafafa;
            --gray-100: #f5f5f5;
            --gray-200: #e5e5e5;
            --gray-300: #d4d4d4;
            --gray-400: #a3a3a3;
            --gray-500: #737373;
            --gray-600: #525252;
            --gray-700: #404040;
            --gray-800: #262626;
            --gray-900: #171717;
            
            /* Status Colors */
            --success: #10b981;
            --success-bg: #ecfdf5;
            --warning: #f59e0b;
            --warning-bg: #fffbeb;
            --error: #ef4444;
            --error-bg: #fef2f2;
            --info: #3b82f6;
            --info-bg: #eff6ff;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            
            /* Transitions */
            --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        html {{ scroll-behavior: smooth; }}
        
        @keyframes rotate-pulse {{
            0% {{ transform: rotate(0deg) scale(1); }}
            25% {{ transform: rotate(10deg) scale(1.1); }}
            50% {{ transform: rotate(0deg) scale(1); }}
            75% {{ transform: rotate(-10deg) scale(1.1); }}
            100% {{ transform: rotate(0deg) scale(1); }}
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #ffffff 100%);
            color: var(--gray-900);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* Header Section */
        .header {{
            background: linear-gradient(135deg, #000000 0%, #ffffff 100%);
            color: var(--primary);
            padding: 4rem 0 3rem;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.7;
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 900;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #ffffff, #f8fafc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
        }}
        
        .header-description {{
            font-size: 1.25rem;
            color: #ffffff;
            opacity: 0.95;
            margin-bottom: 2rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }}
        
        .header-badges {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }}
        
        .badge {{
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .badge-version {{ background: rgba(16, 185, 129, 0.9); }}
        .badge-ai {{ background: rgba(59, 130, 246, 0.9); }}
        .badge-routes {{ background: rgba(168, 85, 247, 0.9); }}
        
        /* Navigation Hover Effects */
        .nav-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
            background: rgba(255, 255, 255, 0.15) !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
        }}
        
        .nav-active:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
            background: #f8fafc !important;
        }}
        
        .nav-link:active {{
            transform: translateY(0px);
        }}
        
        .system-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }}
        
        .stat-label {{
            font-size: 0.875rem;
            color: #ffffff;
            opacity: 0.9;
            margin-top: 0.5rem;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        /* Main Content */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .api-layout {{
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 2rem;
            margin: 2rem 0;
            min-height: calc(100vh - 400px);
        }}
        
        /* Sidebar */
        .sidebar {{
            background: var(--secondary);
            border-radius: 1rem;
            box-shadow: var(--shadow-lg);
            position: sticky;
            top: 2rem;
            height: fit-content;
            max-height: calc(100vh - 4rem);
            overflow: hidden;
            border: 1px solid var(--gray-200);
        }}
        
        .sidebar-header {{
            background: linear-gradient(135deg, var(--primary), var(--gray-800));
            color: var(--secondary);
            padding: 1.5rem;
            font-weight: 700;
            font-size: 1.125rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .sidebar-content {{
            max-height: calc(100vh - 8rem);
            overflow-y: auto;
        }}
        
        .endpoint-filters {{
            padding: 1rem;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .filter-tabs {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .filter-tab {{
            padding: 0.5rem 1rem;
            border: none;
            background: var(--gray-100);
            color: var(--gray-600);
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: var(--transition);
        }}
        
        .filter-tab.active {{
            background: var(--primary);
            color: var(--secondary);
        }}
        
        .endpoint-list {{
            list-style: none;
            padding: 0;
        }}
        
        .endpoint-group {{
            border-bottom: 1px solid var(--gray-100);
        }}
        
        .endpoint-group-title {{
            padding: 1rem;
            font-weight: 600;
            color: var(--gray-700);
            background: var(--gray-50);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .endpoint-item {{
            border-bottom: 1px solid var(--gray-100);
            cursor: pointer;
            transition: var(--transition);
            position: relative;
        }}
        
        .endpoint-item:hover {{
            background: var(--gray-50);
        }}
        
        .endpoint-item.active {{
            background: var(--primary);
            color: var(--secondary);
        }}
        
        .endpoint-item.active::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--accent);
        }}
        
        .endpoint-link {{
            display: flex;
            align-items: center;
            padding: 1rem;
            text-decoration: none;
            color: inherit;
            gap: 1rem;
        }}
        
        .method-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            border-radius: 0.375rem;
            min-width: 70px;
            text-align: center;
            border: 2px solid;
        }}
        
        .method-get {{ background: var(--success); color: white; border-color: var(--success); }}
        .method-post {{ background: var(--info); color: white; border-color: var(--info); }}
        .method-put {{ background: var(--warning); color: white; border-color: var(--warning); }}
        .method-delete {{ background: var(--error); color: white; border-color: var(--error); }}
        .method-patch {{ background: var(--accent); color: white; border-color: var(--accent); }}
        
        .endpoint-path {{
            font-family: 'JetBrains Mono', monospace;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        /* Main Content Area */
        .main-content {{
            background: var(--secondary);
            border-radius: 1rem;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            border: 1px solid var(--gray-200);
        }}
        
        .content-header {{
            background: linear-gradient(135deg, var(--gray-50), var(--gray-100));
            padding: 2rem;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .endpoint-title {{
            font-size: 2.5rem;
            font-weight: 900;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .endpoint-description {{
            font-size: 1.125rem;
            color: var(--gray-600);
            margin-bottom: 1.5rem;
            padding: 1.5rem;
            background: var(--secondary);
            border-radius: 0.75rem;
            border-left: 4px solid var(--accent);
            box-shadow: var(--shadow-sm);
        }}
        
        .endpoint-tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .tag {{
            padding: 0.25rem 0.75rem;
            background: var(--accent);
            color: var(--secondary);
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        .content-body {{
            padding: 2rem;
        }}
        
        .section {{
            margin-bottom: 3rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--gray-200);
        }}
        
        /* Code Examples */
        .code-examples {{
            background: var(--gray-50);
            border-radius: 1rem;
            overflow: hidden;
            border: 1px solid var(--gray-200);
        }}
        
        .code-tabs {{
            display: flex;
            background: var(--gray-100);
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .code-tab {{
            padding: 1rem 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: var(--gray-600);
            transition: var(--transition);
            border-bottom: 3px solid transparent;
        }}
        
        .code-tab.active {{
            background: var(--secondary);
            color: var(--primary);
            border-bottom-color: var(--accent);
        }}
        
        .code-content {{
            display: none;
            position: relative;
        }}
        
        .code-content.active {{
            display: block;
        }}
        
        .code-block {{
            background: var(--gray-900);
            color: var(--gray-100);
            padding: 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            overflow-x: auto;
            position: relative;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--gray-700);
            color: var(--gray-100);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 600;
            transition: var(--transition);
        }}
        
        .copy-btn:hover {{
            background: var(--gray-600);
        }}
        
        /* Try It Out Section */
        .try-it-section {{
            background: linear-gradient(135deg, var(--info-bg), var(--success-bg));
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid var(--info);
            margin: 2rem 0;
        }}
        
        .try-it-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .try-it-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-900);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .execute-btn {{
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: var(--secondary);
            border: none;
            padding: 1rem 2rem;
            border-radius: 0.75rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
            font-size: 1rem;
            box-shadow: var(--shadow-md);
        }}
        
        .execute-btn:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .execute-btn:active {{
            transform: translateY(0);
        }}
        
        .execute-btn.loading {{
            opacity: 0.7;
            pointer-events: none;
        }}
        
        /* Response Section */
        .response-section {{
            margin-top: 2rem;
            border-radius: 1rem;
            overflow: hidden;
            border: 1px solid var(--gray-200);
            box-shadow: var(--shadow-md);
        }}
        
        .response-header {{
            background: var(--gray-100);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .status-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .status-200 {{ background: var(--success-bg); color: var(--success); border: 1px solid var(--success); }}
        .status-400 {{ background: var(--error-bg); color: var(--error); border: 1px solid var(--error); }}
        .status-500 {{ background: var(--error-bg); color: var(--error); border: 1px solid var(--error); }}
        
        .response-time {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--gray-600);
            font-size: 0.875rem;
        }}
        
        /* Welcome Message */
        .welcome-message {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--gray-600);
        }}
        
        .welcome-message h2 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            color: var(--gray-800);
        }}
        
        .welcome-message p {{
            font-size: 1.125rem;
            margin-bottom: 2rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .quick-start {{
            background: var(--gray-50);
            border-radius: 1rem;
            padding: 2rem;
            margin-top: 2rem;
            border: 1px solid var(--gray-200);
        }}
        
        .quick-start h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--gray-800);
        }}
        
        /* Loading States */
        .loading-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: var(--secondary);
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Responsive Design */
        @media (max-width: 1024px) {{
            .api-layout {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
            
            .sidebar {{
                position: static;
                max-height: none;
            }}
            
            .header h1 {{
                font-size: 3rem;
            }}
            
            .system-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 640px) {{
            .container {{
                padding: 0 1rem;
            }}
            
            .header {{
                padding: 2rem 0;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .header-badges {{
                flex-direction: column;
                align-items: center;
            }}
            
            .system-stats {{
                grid-template-columns: 1fr;
            }}
            
            .endpoint-title {{
                font-size: 1.75rem;
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .try-it-header {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .execute-btn {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-nav" style="position: absolute; top: 1rem; right: 2rem; display: flex; gap: 1.5rem; z-index: 3;">
            <a href="/" class="nav-link" style="color: #ffffff; text-decoration: none; font-weight: 600; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s ease; border: 2px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);">Home</a>
            <a href="/docs" class="nav-link nav-active" style="color: #000000; text-decoration: none; font-weight: 600; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s ease; background: #ffffff; border: 2px solid #ffffff; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);">API Docs</a>
            <a href="/admin" class="nav-link" style="color: #ffffff; text-decoration: none; font-weight: 600; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s ease; border: 2px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);">Admin</a>
            <a href="/health" class="nav-link" style="color: #ffffff; text-decoration: none; font-weight: 600; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s ease; border: 2px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);">Health</a>
        </div>
        <div class="container">
            <div class="header-content">
                <h1><img src="/static/image/favicon.ico" alt="CREATESONLINE" style="width: 48px; height: 48px; margin-right: 1rem; animation: rotate-pulse 3s ease-in-out infinite; vertical-align: middle;" />{self.title}</h1>
                <p class="header-description">{self.description}</p>
                
                <div class="header-badges">
                    <div class="badge badge-version">v{self.version}</div>
                    <div class="badge badge-ai"><img src="/static/image/favicon.ico" alt="CREATESONLINE" style="width: 16px; height: 16px; margin-right: 0.5rem; vertical-align: middle;" />AI-Native</div>
                    <div class="badge badge-routes">{spec['x-system-info']['total_routes']} Routes</div>
                </div>
                
                <div class="system-stats">
                    <div class="stat-card">
                        <div class="stat-value">{spec['x-system-info']['total_routes']}</div>
                        <div class="stat-label">Total Endpoints</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{spec['x-system-info']['ai_routes']}</div>
                        <div class="stat-label">AI-Powered</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(spec['x-system-info']['features'])}</div>
                        <div class="stat-label">AI Features</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{spec['info']['x-python-version']}</div>
                        <div class="stat-label">Python Version</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="api-layout">
            <aside class="sidebar">
                <div class="sidebar-header">
                     API Endpoints
                </div>
                <div class="sidebar-content">
                    <div class="endpoint-filters">
                        <div class="filter-tabs">
                            <button class="filter-tab active" data-filter="all">All</button>
                            <button class="filter-tab" data-filter="ai">AI</button>
                            <button class="filter-tab" data-filter="admin">Admin</button>
                            <button class="filter-tab" data-filter="system">System</button>
                        </div>
                    </div>
                    <ul class="endpoint-list" id="endpointList">
                        <!-- Dynamic endpoints will be loaded here -->
                    </ul>
                </div>
            </aside>

            <main class="main-content">
                <div id="endpointDetails">
                    <div class="welcome-message">
                        <h2>Welcome to {self.title} API</h2>
                        <p>Explore our AI-native API with intelligent endpoints and real-time testing capabilities. Select an endpoint from the sidebar to get started.</p>
                        
                        <div class="quick-start">
                            <h3> Quick Start</h3>
                            <div class="code-block">
curl -X GET "{self._get_base_url()}/" \\
  -H "Accept: application/json" \\
  -H "User-Agent: MyApp/1.0"
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script>
        // API Specification with all dynamic backend data
        const apiSpec = {json.dumps(spec, indent=2)};
        
        class AdvancedAPIExplorer {{
            constructor() {{
                this.currentEndpoint = null;
                this.baseUrl = window.location.origin;
                this.currentFilter = 'all';
                this.currentCodeTab = 'curl';
                this.init();
            }}

            init() {{
                this.renderEndpoints();
                this.setupEventListeners();
                this.setupFilters();
                this.displaySystemInfo();
            }}

            setupEventListeners() {{
                // Filter tabs
                document.querySelectorAll('.filter-tab').forEach(tab => {{
                    tab.addEventListener('click', (e) => {{
                        this.setFilter(e.target.dataset.filter);
                    }});
                }});
            }}

            setupFilters() {{
                // Initialize filter functionality
                this.filterEndpoints(this.currentFilter);
            }}

            setFilter(filter) {{
                this.currentFilter = filter;
                
                // Update active tab
                document.querySelectorAll('.filter-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                document.querySelector(`[data-filter="${{filter}}"]`).classList.add('active');
                
                // Filter endpoints
                this.filterEndpoints(filter);
            }}

            filterEndpoints(filter) {{
                const items = document.querySelectorAll('.endpoint-item');
                items.forEach(item => {{
                    const tags = item.dataset.tags || '';
                    const shouldShow = filter === 'all' || 
                                     tags.toLowerCase().includes(filter.toLowerCase());
                    item.style.display = shouldShow ? 'block' : 'none';
                }});
            }}

            displaySystemInfo() {{
                // console.log(' CREATESONLINE API Explorer Loaded');
                // console.log('System Info:', apiSpec['x-system-info']);
                // console.log('Available Features:', apiSpec['x-system-info']['features']);
            }}

            renderEndpoints() {{
                const endpointList = document.getElementById('endpointList');
                const paths = apiSpec.paths || {{}};
                
                // Group endpoints by tags
                const groupedEndpoints = {{}};
                
                Object.entries(paths).forEach(([path, methods]) => {{
                    Object.entries(methods).forEach(([method, details]) => {{
                        const tags = details.tags || ['API'];
                        const primaryTag = tags[0];
                        
                        if (!groupedEndpoints[primaryTag]) {{
                            groupedEndpoints[primaryTag] = [];
                        }}
                        
                        groupedEndpoints[primaryTag].push({{
                            path, method, details, tags: tags.join(' ')
                        }});
                    }});
                }});

                // Render grouped endpoints
                Object.entries(groupedEndpoints).forEach(([group, endpoints]) => {{
                    // Group header
                    const groupDiv = document.createElement('div');
                    groupDiv.className = 'endpoint-group';
                    
                    const groupTitle = document.createElement('div');
                    groupTitle.className = 'endpoint-group-title';
                    groupTitle.textContent = group;
                    groupDiv.appendChild(groupTitle);
                    
                    // Group endpoints
                    endpoints.forEach({{path, method, details, tags}}) => {{
                        const li = document.createElement('li');
                        li.className = 'endpoint-item';
                        li.dataset.tags = tags;
                        li.innerHTML = `
                            <a href="#" class="endpoint-link" data-path="${{path}}" data-method="${{method}}">
                                <span class="method-badge method-${{method}}">${{method.toUpperCase()}}</span>
                                <span class="endpoint-path">${{path}}</span>
                            </a>
                        `;
                        
                        li.addEventListener('click', (e) => {{
                            e.preventDefault();
                            this.showEndpointDetails(path, method, details);
                            this.setActiveEndpoint(li);
                        }});

                        groupDiv.appendChild(li);
                    }});
                    
                    endpointList.appendChild(groupDiv);
                }});
            }}

            setActiveEndpoint(activeElement) {{
                document.querySelectorAll('.endpoint-item').forEach(item => {{
                    item.classList.remove('active');
                }});
                activeElement.classList.add('active');
            }}

            showEndpointDetails(path, method, details) {{
                this.currentEndpoint = {{ path, method, details }};
                const detailsContainer = document.getElementById('endpointDetails');
                
                const codeSamples = details['x-code-samples'] || [];
                const parameters = details.parameters || [];
                const responses = details.responses || {{}};
                
                detailsContainer.innerHTML = `
                    <div class="content-header">
                        <div class="endpoint-title">
                            <span class="method-badge method-${{method}}">${{method.toUpperCase()}}</span>
                            <span>${{path}}</span>
                        </div>
                        
                        <div class="endpoint-description">
                            ${{details.description || details.summary || 'No description available'}}
                        </div>
                        
                        <div class="endpoint-tags">
                            ${{(details.tags || []).map(tag => `<span class="tag">${{tag}}</span>`).join('')}}
                        </div>
                    </div>
                    
                    <div class="content-body">
                        ${{parameters.length > 0 ? `
                        <div class="section">
                            <h3 class="section-title"> Parameters</h3>
                            <div class="parameters-grid">
                                ${{parameters.map(param => `
                                    <div class="parameter-item">
                                        <div class="parameter-name">${{param.name}}</div>
                                        <div class="parameter-type">${{param.schema?.type || 'string'}}</div>
                                        <div class="parameter-description">${{param.description || 'No description'}}</div>
                                        <div class="parameter-required">${{param.required ? 'Required' : 'Optional'}}</div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                        ` : ''}}

                        <div class="section">
                            <h3 class="section-title"> Code Examples</h3>
                            <div class="code-examples">
                                <div class="code-tabs">
                                    ${{codeSamples.map(sample => `
                                        <button class="code-tab ${{sample.lang === 'curl' ? 'active' : ''}}" 
                                                data-lang="${{sample.lang}}">${{sample.lang.toUpperCase()}}</button>
                                    `).join('')}}
                                </div>
                                ${{codeSamples.map(sample => `
                                    <div class="code-content ${{sample.lang === 'curl' ? 'active' : ''}}" 
                                         data-lang="${{sample.lang}}">
                                        <div class="code-block">
                                            <button class="copy-btn" onclick="this.copyCode(this)"> Copy</button>
                                            <pre>${{sample.source}}</pre>
                                        </div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>

                        <div class="try-it-section">
                            <div class="try-it-header">
                                <h3 class="try-it-title">
                                     Try It Out
                                </h3>
                                <button class="execute-btn" onclick="apiExplorer.executeRequest()">
                                    Execute Request
                                </button>
                            </div>
                            
                            <div id="responseContainer" class="response-section" style="display: none;">
                                <div class="response-header">
                                    <div id="responseStatus"></div>
                                    <div id="responseTime" class="response-time"></div>
                                </div>
                                <div id="responseContent"></div>
                            </div>
                        </div>

                        <div class="section">
                            <h3 class="section-title"> Response Schema</h3>
                            ${{this.renderResponseSchema(responses)}}
                        </div>
                    </div>
                `;
                
                // Setup code tab switching
                this.setupCodeTabs();
            }}

            setupCodeTabs() {{
                document.querySelectorAll('.code-tab').forEach(tab => {{
                    tab.addEventListener('click', (e) => {{
                        const lang = e.target.dataset.lang;
                        
                        // Update active tab
                        document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
                        e.target.classList.add('active');
                        
                        // Show corresponding content
                        document.querySelectorAll('.code-content').forEach(content => {{
                            content.classList.remove('active');
                        }});
                        document.querySelector(`[data-lang="${{lang}}"]`).classList.add('active');
                    }});
                }});
            }}

            copyCode(button) {{
                const code = button.nextElementSibling.textContent;
                navigator.clipboard.writeText(code).then(() => {{
                    button.textContent = ' Copied!';
                    setTimeout(() => {{
                        button.textContent = ' Copy';
                    }}, 2000);
                }});
            }}

            renderResponseSchema(responses) {{
                let html = '';
                Object.entries(responses).forEach(([status, response]) => {{
                    const statusClass = status.startsWith('2') ? 'status-200' : 
                                      status.startsWith('4') ? 'status-400' : 'status-500';
                    html += `
                        <div style="margin-bottom: 1.5rem;">
                            <div class="status-indicator ${{statusClass}}">
                                <span>${{status}}</span>
                                <span>${{response.description}}</span>
                            </div>
                            <div class="code-block" style="margin-top: 1rem;">
                                <button class="copy-btn" onclick="apiExplorer.copyCode(this)"> Copy</button>
                                <pre>${{JSON.stringify(response.content?.['application/json']?.example || {{}}, null, 2)}}</pre>
                            </div>
                        </div>
                    `;
                }});
                return html || '<p>No response schema available</p>';
            }}

            async executeRequest() {{
                if (!this.currentEndpoint) return;

                const {{ path, method }} = this.currentEndpoint;
                const executeBtn = document.querySelector('.execute-btn');
                const responseContainer = document.getElementById('responseContainer');
                const responseStatus = document.getElementById('responseStatus');
                const responseTime = document.getElementById('responseTime');
                const responseContent = document.getElementById('responseContent');

                // Show loading state
                executeBtn.classList.add('loading');
                executeBtn.innerHTML = '<span class="loading-spinner"></span> Executing...';
                responseContainer.style.display = 'block';

                try {{
                    const startTime = performance.now();
                    const response = await fetch(path, {{ 
                        method: method.toUpperCase(),
                        headers: {{
                            'Accept': 'application/json',
                            'User-Agent': 'CREATESONLINE-API-Explorer/1.0'
                        }}
                    }});
                    const endTime = performance.now();
                    const responseTimeMs = Math.round(endTime - startTime);

                    let responseData;
                    const contentType = response.headers.get('content-type') || '';
                    
                    if (contentType.includes('application/json')) {{
                        responseData = await response.json();
                    }} else {{
                        responseData = await response.text();
                    }}

                    const statusClass = response.ok ? 'status-200' : 
                                      response.status >= 400 && response.status < 500 ? 'status-400' : 'status-500';
                    
                    responseStatus.innerHTML = `
                        <div class="status-indicator ${{statusClass}}">
                            <span>${{response.status}} ${{response.statusText}}</span>
                        </div>
                    `;
                    
                    responseTime.textContent = `⏱ ${{responseTimeMs}}ms`;
                    
                    responseContent.innerHTML = `
                        <div class="code-block">
                            <button class="copy-btn" onclick="apiExplorer.copyCode(this)"> Copy</button>
                            <pre>${{typeof responseData === 'object' ? 
                                JSON.stringify(responseData, null, 2) : responseData}}</pre>
                        </div>
                    `;

                }} catch (error) {{
                    responseStatus.innerHTML = `
                        <div class="status-indicator status-400">
                            <span> Network Error</span>
                        </div>
                    `;
                    responseTime.textContent = '';
                    responseContent.innerHTML = `
                        <div class="code-block">
                            <pre>Error: ${{error.message}}</pre>
                        </div>
                    `;
                }} finally {{
                    executeBtn.classList.remove('loading');
                    executeBtn.textContent = 'Execute Request';
                }}
            }}
        }}

        // Initialize the advanced API explorer
        const apiExplorer = new AdvancedAPIExplorer();
        
        // Global functions for inline event handlers
        window.apiExplorer = apiExplorer;
    </script>
</body>
</html>
"""
        
        # Use internal HTML response class
        class HTMLResponse:
            def __init__(self, content, status_code=200, headers=None):
                self.content = content
                self.status_code = status_code
                self.headers = headers or {'content-type': 'text/html'}
        
        return HTMLResponse(html_content)
    
    def _get_base_url(self):
        """Get base URL for API documentation"""
        return "http://127.0.0.1:8000"  # Default for development

    def _generate_enhanced_api_paths(self) -> dict:
        """Generate enhanced OpenAPI paths from routes with detailed info"""
        paths = {}
        for route_key in self._internal_routes.keys():
            method, path = route_key.split(':', 1)
            if path not in paths:
                paths[path] = {}
            
            # Enhanced path information
            paths[path][method.lower()] = {
                "summary": f"{method.upper()} {path}",
                "description": self._get_route_description(path, method),
                "operationId": f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}",
                "tags": self._get_route_tags(path),
                "parameters": self._get_route_parameters(path),
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": self._get_example_response(path, method)
                            }
                        }
                    },
                    "400": {"description": "Bad request"},
                    "404": {"description": "Not found"},
                    "500": {"description": "Internal server error"}
                },
                "x-code-samples": [
                    {
                        "lang": "curl",
                        "source": f"curl -X {method.upper()} '{self._get_base_url()}{path}' -H 'Accept: application/json'"
                    },
                    {
                        "lang": "python",
                        "source": f"import requests\nresponse = requests.{method.lower()}('{self._get_base_url()}{path}')\nprint(response.json())"
                    },
                    {
                        "lang": "javascript",
                        "source": f"fetch('{self._get_base_url()}{path}', {{\n  method: '{method.upper()}',\n  headers: {{\n    'Accept': 'application/json'\n  }}\n}})\n.then(response => response.json())\n.then(data => console.log(data));"
                    }
                ]
            }
        return paths

    def _get_route_description(self, path: str, method: str) -> str:
        """Get description for a route based on its path"""
        descriptions = {
            "/": "Get framework information and status",
            "/health": "Health check endpoint with system metrics",
            "/examples": "Example endpoint showcasing framework capabilities", 
            "/admin": "Admin interface for managing the application",
            "/api/status": "API status and operational information",
            "/docs": "Interactive API documentation and specification",
            "/docs": "Interactive API documentation",
            "/framework/info": "Detailed framework information and configuration"
        }
        
        # Check for AI routes
        if '/ai/' in path:
            return "AI-powered endpoint with intelligent processing capabilities"
        
        # Check for admin routes
        if '/admin/' in path:
            return "Administrative endpoint for system management"
            
        return descriptions.get(path, f"API endpoint: {method.upper()} {path}")

    def _get_route_tags(self, path: str) -> list:
        """Get tags for route categorization"""
        if path.startswith('/ai/'):
            return ["AI", "Machine Learning"]
        elif path.startswith('/admin/'):
            return ["Admin", "Management"]
        elif path in ['/health', '/api/status']:
            return ["System", "Health"]
        elif path in ['/', '/examples', '/framework/info']:
            return ["Framework", "Info"]
        else:
            return ["API"]

    def _get_route_parameters(self, path: str) -> list:
        """Extract parameters from route path"""
        import re
        params = []
        param_matches = re.findall(r'\{([^}]+)\}', path)
        
        for param in param_matches:
            param_info = {
                "name": param,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"Path parameter: {param}"
            }
            
            # Type hints from parameter names
            if 'id' in param.lower():
                param_info["schema"] = {"type": "integer", "minimum": 1}
                param_info["description"] = f"Unique identifier for {param.replace('_id', '').replace('id', 'resource')}"
            elif 'model' in param.lower():
                param_info["schema"] = {"type": "string", "enum": ["gpt-3.5-turbo", "gpt-4", "claude-3"]}
                param_info["description"] = "AI model name"
            
            params.append(param_info)
        
        return params

    def _get_example_response(self, path: str, method: str) -> dict:
        """Generate example responses based on route"""
        examples = {
            "/": {
                "framework": "CREATESONLINE",
                "version": self.version,
                "status": "operational",
                "ai_enabled": len(self._ai_features) > 0,
                "features": self._ai_features[:3] if self._ai_features else []
            },
            "/health": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "uptime": 86400,
                "system": {"memory": "45%", "cpu": "12%", "disk": "67%"}
            },
            "/examples": {
                "message": "CREATESONLINE Example Response",
                "capabilities": ["AI Integration", "Admin Interface", "Smart Routing"],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        if '/ai/' in path:
            return {
                "model": "gpt-3.5-turbo",
                "response": "AI-generated response",
                "confidence": 0.95,
                "processing_time_ms": 250
            }
        
        return examples.get(path, {"message": "Success", "data": {}})

    def _generate_api_schemas(self) -> dict:
        """Generate API schemas for common data types"""
        return {
            "FrameworkInfo": {
                "type": "object",
                "properties": {
                    "framework": {"type": "string", "example": "CREATESONLINE"},
                    "version": {"type": "string", "example": self.version},
                    "status": {"type": "string", "enum": ["operational", "maintenance", "error"]},
                    "ai_enabled": {"type": "boolean"},
                    "features": {"type": "array", "items": {"type": "string"}}
                }
            },
            "HealthStatus": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "uptime": {"type": "integer", "description": "Uptime in seconds"},
                    "system": {
                        "type": "object",
                        "properties": {
                            "memory": {"type": "string"},
                            "cpu": {"type": "string"},
                            "disk": {"type": "string"}
                        }
                    }
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "integer"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }
    
    def _generate_error_page(self, status_code: int, error_message: str, path: str = "", method: str = "GET", details: str = "") -> str:
        """Generate beautiful HTML error pages matching homepage UI"""
        
        error_titles = {
            404: "Page Not Found",
            500: "Internal Server Error",
            403: "Access Forbidden",
            400: "Bad Request"
        }
        
        title = error_titles.get(status_code, f"Error {status_code}")
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CREATESONLINE</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .error-container {{
            max-width: 700px;
            width: 100%;
            background: #1a1a1a;
            padding: 60px 50px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            text-align: center;
        }}
        
        .error-code {{
            font-size: 8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            line-height: 1;
        }}
        
        h1 {{
            font-size: 2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #fff;
        }}
        
        p {{
            color: #888;
            font-size: 1.1em;
            margin-bottom: 40px;
            line-height: 1.6;
        }}
        
        .btn {{
            padding: 14px 28px;
            background: #ffffff;
            color: #000;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-block;
        }}
        
        .btn:hover {{
            background: #f0f0f0;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.15);
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid #2a2a2a;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 600px) {{
            .error-container {{
                padding: 40px 30px;
            }}
            .error-code {{
                font-size: 5em;
            }}
            h1 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">{status_code}</div>
        <h1>{title}</h1>
        <p>{error_message}</p>
        
        <a href="/" class="btn">Go Home</a>
        
        <div class="footer">
            <p>CREATESONLINE v{self.version}</p>
        </div>
    </div>
</body>
</html>"""


class CreatesonlineInternalRequest:
    """Internal request object for zero-dependency mode"""
    
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self.method = scope['method']
        self.url = self._build_url(scope)
        self.path = scope['path']
        self.query_params = self._parse_query_string(scope.get('query_string', b''))
        self.path_params = scope.get('path_params', {})
        self.headers = self._parse_headers(scope.get('headers', []))
    
    def _build_url(self, scope):
        """Build URL object from scope"""
        scheme = scope.get('scheme', 'http')
        server = scope.get('server', ('localhost', 80))
        path = scope.get('path', '/')
        query_string = scope.get('query_string', b'').decode()
        
        url = f"{scheme}://{server[0]}:{server[1]}{path}"
        if query_string:
            url += f"?{query_string}"
        
        return url
    
    def _parse_query_string(self, query_string):
        """Parse query string into dict"""
        if not query_string:
            return {}
        
        return parse_qs(query_string.decode(), keep_blank_values=True)
    
    def _parse_headers(self, headers):
        """Parse headers into dict"""
        header_dict = {}
        for name, value in headers:
            # Handle both bytes and string headers
            if isinstance(name, bytes):
                name = name.decode()
            if isinstance(value, bytes):
                value = value.decode()
            header_dict[name.lower()] = value
        return header_dict
    
    async def json(self):
        """Parse JSON body"""
        body = await self._get_body()
        return json.loads(body.decode())
    
    async def body(self):
        """Get raw body"""
        return await self._get_body()
    
    async def _get_body(self):
        """Get request body"""
        body = b''
        while True:
            message = await self.receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body

    def _generate_error_page(self, status_code: int, error_message: str, path: str = "", method: str = "GET", details: str = "") -> str:
        """Generate beautiful HTML error pages with consistent CREATESONLINE theming"""
        
        # Define error page content based on status code
        error_info = {
            404: {
                "title": "Page Not Found",
                "emoji": "",
                "description": "The page you're looking for doesn't exist or has been moved.",
                "suggestions": [
                    "Check the URL for typos",
                    "Go back to the homepage",
                    "Browse our available API endpoints",
                    "Contact support if you believe this is an error"
                ]
            },
            500: {
                "title": "Internal Server Error",
                "emoji": "",
                "description": "Something went wrong on our end. We're working to fix it.",
                "suggestions": [
                    "Try refreshing the page",
                    "Wait a moment and try again",
                    "Check our status page",
                    "Contact support if the problem persists"
                ]
            },
            403: {
                "title": "Access Forbidden",
                "emoji": "🚫",
                "description": "You don't have permission to access this resource.",
                "suggestions": [
                    "Check if you're logged in",
                    "Verify your permissions",
                    "Contact an administrator",
                    "Return to the homepage"
                ]
            },
            400: {
                "title": "Bad Request",
                "emoji": "",
                "description": "The request was invalid or could not be processed.",
                "suggestions": [
                    "Check your request format",
                    "Review the API documentation",
                    "Verify required parameters",
                    "Try a different approach"
                ]
            }
        }
        
        # Get error info or default for unknown status codes
        info = error_info.get(status_code, {
            "title": f"Error {status_code}",
            "emoji": "",
            "description": error_message or "An unexpected error occurred.",
            "suggestions": [
                "Try refreshing the page",
                "Go back to the previous page",
                "Contact support",
                "Return to the homepage"
            ]
        })
        
        # Generate navigation suggestions based on available routes
        nav_links = []
        if hasattr(self, '_internal_routes'):
            for route_key in self._internal_routes.keys():
                route_method, route_path = route_key.split(':', 1)
                if route_method == 'GET' and not '{' in route_path:  # Only GET routes without parameters
                    if route_path in ['/', '/health', '/admin', '/docs']:
                        route_name = {
                            '/': 'Home',
                            '/health': 'System Health',
                            '/admin': 'Admin Panel',
                            '/docs': 'API Documentation'
                        }.get(route_path, route_path.title())
                        nav_links.append(f'<a href="{route_path}" style="color: #ffffff; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; border-radius: 0.5rem; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); transition: all 0.2s ease; display: inline-block; margin: 0.5rem;">{route_name}</a>')
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{info['title']} - CREATESONLINE</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="icon" type="image/x-icon" href="/static/image/favicon.ico">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        @keyframes rotate-pulse {{
            0% {{ transform: rotate(0deg) scale(1); }}
            25% {{ transform: rotate(10deg) scale(1.1); }}
            50% {{ transform: rotate(0deg) scale(1); }}
            75% {{ transform: rotate(-10deg) scale(1.1); }}
            100% {{ transform: rotate(0deg) scale(1); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .error-container {{
            max-width: 700px;
            width: 100%;
            background: #1a1a1a;
            padding: 60px 50px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            text-align: center;
        }}
        
        .error-icon {{
            font-size: 4rem;
            margin-bottom: 1.5rem;
            display: block;
        }}
        
        .error-code {{
            font-size: 8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            line-height: 1;
        }}
        
        .error-title {{
            font-size: 2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #fff;
        }}
        
        .error-description {{
            color: #888;
            font-size: 1.1em;
            margin-bottom: 40px;
            line-height: 1.6;
        }}
        
        .error-details {{
            background: #0a0a0a;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            text-align: left;
        }}
        
        .error-details h4 {{
            color: #fff;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .error-details p {{
            color: #888;
            font-size: 0.95em;
            margin: 8px 0;
        }}
        
        .actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }}
        
        .btn {{
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: #ffffff;
            color: #000;
        }}
        
        .btn-primary:hover {{
            background: #f0f0f0;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.15);
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid #2a2a2a;
            color: #666;
            font-size: 0.9em;
        }}
            color: #ffffff;
            opacity: 0.7;
            font-size: 0.9rem;
        
        @media (max-width: 600px) {{
            .error-container {{
                padding: 40px 30px;
            }}
            .error-code {{
                font-size: 5em;
            }}
            .error-title {{
                font-size: 1.5em;
            }}
            .actions {{
                flex-direction: column;
            }}
            .btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">{status_code}</div>
        <h1 class="error-title">{info['title']}</h1>
        <p class="error-description">{info['description']}</p>
        
        {f'''
        <div class="error-details">
            <h4>Request Details</h4>
            <p><strong>Path:</strong> {path}</p>
            <p><strong>Method:</strong> {method}</p>
        </div>
        ''' if path else ''}
        
        <div class="actions">
            <a href="/" class="btn btn-primary">Go Home</a>
        </div>
        
        <div class="footer">
            <p>CREATESONLINE v{self.version} - AI-Native Web Framework</p>
        </div>
    </div>
        <img src="/static/image/favicon.ico" alt="CREATESONLINE" />
        <span>Powered by CREATESONLINE</span>
    </div>
</body>
</html>
        """
