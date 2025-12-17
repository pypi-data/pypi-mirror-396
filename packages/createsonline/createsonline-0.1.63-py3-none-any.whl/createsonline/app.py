# createsonline/app.py
"""
CREATESONLINE Application Core

Main application class and request handling
"""

import sys
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union

# System requirements check
if sys.version_info < (3, 9):
    raise RuntimeError(f"CREATESONLINE requires Python 3.9+. Current: {sys.version}")

# Setup logging
logger = logging.getLogger("createsonline")

# Get version
from . import __version__


class CreatesonlineInternalApp:
    """
    Pure CREATESONLINE core application - ZERO external dependencies
    
    This is the internal implementation that works with just Python stdlib.
    Provides full AI-native framework capabilities without any external packages.
    """
    
    def __init__(
        self,
        title: str = "CREATESONLINE Application",
        description: str = "AI-powered application built with CREATESONLINE",
        version: str = "1.0.0",
        ai_config: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        **kwargs
    ):
        # Core application metadata
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.ai_config = ai_config or {}
        
        # Internal routing system
        self.routes = {}
        self.middleware = []
        self.startup_handlers = []
        self.shutdown_handlers = []
        
        # AI-native features (internal implementations)
        self.ai_enabled = True
        self.ai_features = []
        self.ai_services = CreatesonlineInternalAI()
        
        # Setup framework routes
        self._setup_framework_routes()
        
        logger.info(f"CREATESONLINE v{__version__} initialized (Internal Core)")
        logger.info(f"{self.title} - AI-Native Framework Ready")
    
    def _setup_framework_routes(self):
        """Setup built-in CREATESONLINE framework routes"""
        
        @self.get("/health")
        async def health_check(request):
            return {
                "status": "healthy",
                "framework": "CREATESONLINE",
                "version": __version__,
                "timestamp": datetime.utcnow().isoformat()
            }

        @self.get("/docs")
        async def docs(request):
            try:
                from createsonline.config.docs import APIDocumentationGenerator
                generator = APIDocumentationGenerator(self)
                return generator.generate_beautiful_api_docs()
            except Exception as exc:
                return {"error": "Docs unavailable", "message": str(exc)}, 500

        @self.get("/doc")
        async def doc_alias(request):
            from .server import InternalResponse
            return InternalResponse(b"", status_code=302, headers={"Location": "/docs"})
    
    # ========================================
    # PURE ASGI IMPLEMENTATION
    # ========================================
    
    async def __call__(self, scope, receive, send):
        """Pure ASGI interface - no external dependencies"""
        
        if scope['type'] == 'http':
            await self._handle_http(scope, receive, send)
        elif scope['type'] == 'websocket':
            await self._handle_websocket(scope, receive, send)
    
    async def _handle_http(self, scope, receive, send):
        """Handle HTTP requests with internal router"""
        
        # On first request, discover routes from routes.py to override decorators
        if getattr(self, '_needs_route_discovery', False):
            try:
                from .project_init import auto_discover_routes
                auto_discover_routes(self)
                self._needs_route_discovery = False
            except Exception:
                self._needs_route_discovery = False
        
        path = scope['path']
        method = scope['method']
        
        # Handle HEAD requests as GET requests (RFC 7231: HEAD should return same headers as GET, but no body)
        is_head_request = (method == 'HEAD')
        lookup_method = 'GET' if is_head_request else method
        route_key = f"{lookup_method}:{path}"
        
        # Create internal request object
        request = CreatesonlineInternalRequest(scope, receive)
        
        # Middleware processing (Pre-request)
        for middleware in self.middleware:
            if hasattr(middleware, 'before_request'):
                response = await middleware.before_request(request)
                if response:
                    # Middleware intercepted request
                    await self._send_response(send, response, is_head_request=is_head_request)
                    return

        try:
            # Check for static files first (before routing)
            if (method == 'GET' or is_head_request) and self._is_static_path(path):
                print(f"[DEBUG] Static file detected: {path}")
                await self._serve_static_file(path, send, is_head_request=is_head_request)
                return
            else:
                if method == 'GET':
                    print(f"[DEBUG] Not a static path: {path}")
            
            # Find matching route
            if route_key in self.routes:
                handler = self.routes[route_key]
                response_data = await handler(request)
                status = 200
            else:
                # 404 handler - check for custom not_found handler
                not_found_handler = self.routes.get('not_found') or self.routes.get('GET /404')
                if not_found_handler:
                    response_data = await not_found_handler(request)
                    status = 404
                else:
                    # Default 404 response
                    response_data = {
                        "error": "Not Found",
                        "path": path,
                        "method": method,
                        "framework": "CREATESONLINE",
                        "available_routes": list(self.routes.keys())
                    }
                    status = 404
            
            # Middleware processing (Post-request)
            for middleware in reversed(self.middleware):
                if hasattr(middleware, 'after_request'):
                    response_data = await middleware.after_request(request, response_data)

            # Send response (without body for HEAD requests)
            await self._send_response(send, response_data, status, is_head_request=is_head_request)

        except Exception as e:
            # Error handling - log the full traceback
            logger.exception(f"Request handling error for {method} {path}")
            # ALWAYS print to stderr for debugging
            import sys
            print(f"EXCEPTION IN HEAD REQUEST: {type(e).__name__}: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            error_data = {
                "error": "Internal Server Error",
                "message": str(e) if self.debug else "Something went wrong",
                "framework": "CREATESONLINE",
                "exception_type": type(e).__name__
            }
            await self._send_json_response(send, error_data, status=500, is_head_request=is_head_request)

    async def _send_response(self, send, response_data, status=200, is_head_request=False):
        """Unified response sender"""
        # Check for InternalResponse (duck typing or import)
        is_internal = False
        try:
            from .server import InternalResponse
            if isinstance(response_data, InternalResponse):
                is_internal = True
        except ImportError:
            pass

        if is_internal:
            await self._send_internal_response(send, response_data, is_head_request=is_head_request)
        elif isinstance(response_data, dict):
            await self._send_json_response(send, response_data, status=status, is_head_request=is_head_request)
        else:
            await self._send_text_response(send, str(response_data), status=status, is_head_request=is_head_request)
    
    async def _handle_websocket(self, scope, receive, send):
        """Handle WebSocket connections with security measures"""
        await send({'type': 'websocket.accept'})
        
        message_count = 0
        max_messages = 100
        
        while True:
            message = await receive()
            if message['type'] == 'websocket.disconnect':
                break
            elif message['type'] == 'websocket.receive':
                message_count += 1
                if message_count > max_messages:
                    logger.warning("WebSocket rate limit exceeded")
                    await send({'type': 'websocket.close', 'code': 1008})
                    break
                
                user_text = message.get('text', '')
                if user_text:
                    logger.info(f"WebSocket message received (length: {len(user_text)})")
                
                await send({
                    'type': 'websocket.send',
                    'text': json.dumps({
                        "framework": "CREATESONLINE",
                        "message": "WebSocket message processed",
                        "message_count": message_count
                    })
                })
    
    async def _send_json_response(self, send, data, status=200, is_head_request=False):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2 if self.debug else None).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'content-length', str(len(response_body)).encode()],
                [b'x-framework', b'CREATESONLINE'],
                [b'x-version', __version__.encode()],
                [b'x-mode', b'internal'],
            ],
        })
        
        # Don't send body for HEAD requests
        await send({
            'type': 'http.response.body',
            'body': b'' if is_head_request else response_body,
        })

    async def _send_internal_response(self, send, response, is_head_request=False):
        """Send InternalResponse object"""
        # Ensure headers are bytes
        headers = []
        for k, v in response.headers.items():
            headers.append([str(k).lower().encode(), str(v).encode()])
        
        # Add standard headers
        headers.append([b'content-length', str(len(response.content)).encode()])
        headers.append([b'x-framework', b'CREATESONLINE'])
        headers.append([b'x-mode', b'internal'])
        headers.append([b'x-version', __version__.encode()])
        
        await send({
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': headers,
        })
        
        # Don't send body for HEAD requests
        await send({
            'type': 'http.response.body',
            'body': b'' if is_head_request else response.content,
        })
    
    async def _send_text_response(self, send, text, status=200, is_head_request=False):
        """Send plain text or HTML response"""
        response_body = text.encode('utf-8')
        
        # Detect if it's HTML
        content_type = b'text/html; charset=utf-8' if text.strip().startswith('<!DOCTYPE') or text.strip().startswith('<html') else b'text/plain'
        
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', content_type],
                [b'content-length', str(len(response_body)).encode()],
                [b'x-framework', b'CREATESONLINE'],
                [b'x-mode', b'internal'],
                [b'x-version', __version__.encode()],
            ],
        })
        
        # Don't send body for HEAD requests
        await send({
            'type': 'http.response.body',
            'body': b'' if is_head_request else response_body,
        })
    
    def _is_static_path(self, path: str) -> bool:
        """Check if path is a static file request"""
        static_prefixes = ['/static/', '/css/', '/js/', '/images/', '/img/', '/assets/', '/media/', '/icons/']
        static_extensions = {'.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', 
                           '.woff', '.woff2', '.ttf', '.eot', '.pdf', '.txt', '.json', '.xml'}
        
        for prefix in static_prefixes:
            if path.startswith(prefix):
                return True
        
        for ext in static_extensions:
            if path.endswith(ext):
                return True
        
        return False
    
    async def _serve_static_file(self, path, send, is_head_request=False):
        """Serve static files using StaticFileHandler"""
        try:
            print(f"[DEBUG] _serve_static_file called with: {path}")
            logger.info(f"=== SERVING STATIC FILE: {path} ===")
            from .static_files import static_handler
            
            print(f"[DEBUG] Static dirs: {[str(d) for d in static_handler.static_dirs]}")
            logger.info(f"Static dirs: {[str(d) for d in static_handler.static_dirs]}")
            content, status_code, headers = static_handler.serve_file(path)
            print(f"[DEBUG] serve_file returned: status={status_code}, content_length={len(content)}")
            logger.info(f"Result: status={status_code}, content_length={len(content)}")
            
            header_list = [[k.encode() if isinstance(k, str) else k, 
                           v.encode() if isinstance(v, str) else v] 
                          for k, v in headers.items()]
            
            header_list.append([b'x-framework', b'CREATESONLINE'])
            
            await send({
                'type': 'http.response.start',
                'status': status_code,
                'headers': header_list,
            })
            
            await send({
                'type': 'http.response.body',
                'body': b'' if is_head_request else (content if isinstance(content, bytes) else content.encode('utf-8')),
            })
            
        except Exception as e:
            logger.error(f"Error serving static file {path}: {e}")
            import traceback
            traceback.print_exc()
            await self._send_json_response(send, {"error": "Static file error", "message": str(e)}, status=500, is_head_request=is_head_request)
    
    # ========================================
    # ROUTING DECORATORS
    # ========================================
    
    def get(self, path: str):
        """GET route decorator"""
        def decorator(func):
            self.routes[f"GET:{path}"] = func
            return func
        return decorator
    
    def post(self, path: str):
        """POST route decorator"""
        def decorator(func):
            self.routes[f"POST:{path}"] = func
            return func
        return decorator
    
    def put(self, path: str):
        """PUT route decorator"""
        def decorator(func):
            self.routes[f"PUT:{path}"] = func
            return func
        return decorator
    
    def delete(self, path: str):
        """DELETE route decorator"""
        def decorator(func):
            self.routes[f"DELETE:{path}"] = func
            return func
        return decorator
    
    def patch(self, path: str):
        """PATCH route decorator"""
        def decorator(func):
            self.routes[f"PATCH:{path}"] = func
            return func
        return decorator
    
    def options(self, path: str):
        """OPTIONS route decorator"""
        def decorator(func):
            self.routes[f"OPTIONS:{path}"] = func
            return func
        return decorator
    
    def head(self, path: str):
        """HEAD route decorator"""
        def decorator(func):
            self.routes[f"HEAD:{path}"] = func
            return func
        return decorator
    
    def route(self, path: str, methods: List[str] = None):
        """Multi-method route decorator"""
        if methods is None:
            methods = ["GET"]
        
        def decorator(func):
            for method in methods:
                self.routes[f"{method.upper()}:{path}"] = func
            return func
        return decorator
    
    # ========================================
    # AI-NATIVE FEATURES
    # ========================================
    
    def enable_ai_features(self, features: List[str]):
        """Enable AI features"""
        for feature in features:
            if feature not in self.ai_features:
                self.ai_features.append(feature)
                logger.info(f"AI Feature enabled: {feature}")
        return self
    
    # ========================================
    # LIFECYCLE EVENTS
    # ========================================
    
    def on_startup(self, func: Callable):
        """Register startup handler"""
        self.startup_handlers.append(func)
        return func
    
    def on_shutdown(self, func: Callable):
        """Register shutdown handler"""
        self.shutdown_handlers.append(func)
        return func
    
    # ========================================
    # SERVER RUNNER
    # ========================================
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the application"""
        from .server import run_server
        
        logger.info("Starting CREATESONLINE Pure Python Server")
        logger.info(f"Framework: CREATESONLINE v{__version__}")
        run_server(self, host=host, port=port, reload=reload)
    
    def add_middleware(self, middleware_class, **kwargs):
        """Add middleware to the pipeline"""
        middleware_instance = middleware_class(**kwargs)
        self.middleware.append(middleware_instance)
        return self


class CreatesonlineInternalRequest:
    """Internal request object"""
    
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self.path = scope['path']
        self.method = scope['method']
        self.headers = dict(scope.get('headers', []))
        self.query_params = self._parse_query_string(scope.get('query_string', b''))
        self.path_params = scope.get('path_params', {})
    
    def _parse_query_string(self, query_string):
        """Parse query string into dict"""
        if not query_string:
            return {}
        
        params = {}
        for pair in query_string.decode().split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
        return params
    
    async def json(self):
        """Parse JSON body"""
        body = await self._get_body()
        return json.loads(body.decode())
    
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


class CreatesonlineInternalAI:
    """Internal AI services"""
    
    def __init__(self):
        self.cache = {}
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using internal algorithms"""
        templates = {
            "hello": "Hello! Welcome to CREATESONLINE - the AI-Native framework.",
            "describe": f"CREATESONLINE is an innovative AI-native web framework.",
        }
        
        prompt_lower = prompt.lower()
        for key, template in templates.items():
            if key in prompt_lower:
                return template
        
        return f"CREATESONLINE AI Response: Generated content for '{prompt[:50]}...'"
    
    def get_embedding(self, text: str, dimensions: int = 128) -> List[float]:
        """Generate hash-based embeddings"""
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(dimensions):
            byte_index = i % len(hash_bytes)
            value = (hash_bytes[byte_index] / 255.0) - 0.5
            embedding.append(value)
        
        return embedding


# ========================================
# MAIN FRAMEWORK API
# ========================================

def create_app(
    title: str = "CREATESONLINE Application",
    description: str = "AI-powered application built with CREATESONLINE",
    version: str = "1.0.0",
    ai_config: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    auto_init: bool = True,
    **kwargs
) -> CreatesonlineInternalApp:
    """Create a CREATESONLINE application instance
    
    Args:
        title: Application title
        description: Application description
        version: Application version
        ai_config: AI configuration dictionary
        debug: Enable debug mode
        auto_init: Automatically initialize project structure if needed (default: True)
        **kwargs: Additional configuration
    """
    
    # Auto-initialize project structure if needed (silent)
    if auto_init:
        try:
            from .project_init import init_project_if_needed
            init_project_if_needed(verbose=False)  # Silent initialization
        except Exception:
            pass  # Silent failure - don't break app startup
    
    # TRY: Use full-featured app if available
    try:
        from createsonline.config.app import CreatesonlineApp
        logger.info("Loading full-featured CREATESONLINE...")
        app_instance = CreatesonlineApp(
            title=title,
            description=description,
            version=version,
            ai_config=ai_config or {},
            debug=debug,
            **kwargs
        )
    except ImportError:
        # FALLBACK: Use internal core
        logger.info("Using CREATESONLINE Internal Core")
        app_instance = CreatesonlineInternalApp(
            title=title,
            description=description,
            version=version,
            ai_config=ai_config or {},
            debug=debug,
            **kwargs
        )
    
    # Auto-discover and register routes from routes.py (if exists)
    # DEFERRED: Will be applied at first request to override any @app.get decorators
    if auto_init:
        try:
            # Store the app instance for deferred route loading
            app_instance._needs_route_discovery = True
        except Exception:
            pass
    
    # Initialize database connection
    try:
        from .database import get_database
        db = get_database()
        logger.info(f"Database initialized: {db.database_url}")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
    
    return app_instance
