# createsonline/testing.py
"""
CREATESONLINE Testing Module

Provides test client and utilities for testing CREATESONLINE applications.
Pure Python implementation without external dependencies.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Union
from urllib.parse import urlencode, urlparse, parse_qs

# Setup logging
logger = logging.getLogger("createsonline.testing")


class TestResponse:
    """Test response object mimicking HTTP response"""
    
    def __init__(self, status_code: int, content: Union[str, bytes, dict], headers: Dict[str, str] = None):
        self.status_code = status_code
        self.headers = headers or {}
        
        if isinstance(content, dict):
            self._content = json.dumps(content).encode()
            self.headers.setdefault('content-type', 'application/json')
        elif isinstance(content, str):
            self._content = content.encode()
            self.headers.setdefault('content-type', 'text/plain')
        else:
            self._content = content
    
    @property
    def content(self) -> bytes:
        return self._content
    
    @property
    def text(self) -> str:
        return self._content.decode()
    
    def json(self) -> Dict[str, Any]:
        """Parse response as JSON"""
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            raise ValueError("Response is not valid JSON")


class TestClient:
    """
    Test client for CREATESONLINE applications.
    Provides methods to test HTTP endpoints without external dependencies.
    """
    
    def __init__(self, app):
        self.app = app
        self.base_url = "http://testserver"
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop for async operations"""
        if self._loop is None or self._loop.is_closed():
            try:
                # Try to get existing loop
                self._loop = asyncio.get_event_loop()
                if self._loop.is_closed():
                    raise RuntimeError("Loop is closed")
            except RuntimeError:
                # Create new loop if none exists
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    def _build_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Build request object from parameters"""
        # Parse URL
        parsed = urlparse(url if url.startswith('http') else self.base_url + url)
        
        request = {
            'method': method.upper(),
            'url': url,
            'path': parsed.path,
            'query_params': parse_qs(parsed.query),
            'headers': kwargs.get('headers', {}),
            'body': None
        }
        
        # Handle JSON data
        if 'json' in kwargs:
            request['body'] = json.dumps(kwargs['json'])
            request['headers']['content-type'] = 'application/json'
        
        # Handle form data
        elif 'data' in kwargs:
            if isinstance(kwargs['data'], dict):
                request['body'] = urlencode(kwargs['data'])
                request['headers']['content-type'] = 'application/x-www-form-urlencoded'
            else:
                request['body'] = kwargs['data']
        
        # Handle files
        elif 'files' in kwargs:
            # Simple file handling (for testing purposes)
            request['body'] = str(kwargs['files'])
            request['headers']['content-type'] = 'multipart/form-data'
        
        return request
    
    async def _execute_request(self, request: Dict[str, Any]) -> TestResponse:
        """Execute request against the CREATESONLINE app"""
        try:
            # Find matching route in app
            path = request['path']
            method = request['method']
            route_key = f"{method}:{path}"
            
            # Check if app has routes (support both internal and full app)
            routes = None
            if hasattr(self.app, 'routes') and isinstance(self.app.routes, dict):
                routes = self.app.routes
            elif hasattr(self.app, '_internal_routes'):
                routes = self.app._internal_routes
            
            if routes and route_key in routes:
                handler = routes[route_key]
                
                # Create mock request object for handler
                class MockRequest:
                    def __init__(self, method, path, query_params, headers, body):
                        self.method = method
                        self.path = path
                        self.query_params = query_params
                        self.headers = headers
                        self._body = body
                    
                    async def json(self):
                        """Async json method for handlers that await request.json()"""
                        if self._body and 'json' in self.headers.get('content-type', ''):
                            return json.loads(self._body)
                        return {}
                
                mock_request = MockRequest(
                    method, path, 
                    request.get('query_params', {}),
                    request.get('headers', {}),
                    request.get('body', '')
                )
                
                # Call the handler
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(mock_request)
                else:
                    result = handler(mock_request)
                
                # Handle different response types including (data, status) and (data, status, headers) tuples
                if isinstance(result, tuple):
                    if len(result) == 3:
                        data, status, headers = result
                        return TestResponse(status, data, headers)
                    elif len(result) == 2:
                        data, status = result
                        return TestResponse(status, data)
                elif isinstance(result, dict):
                    return TestResponse(200, result)
                elif isinstance(result, (str, bytes)):
                    return TestResponse(200, result)
                else:
                    return TestResponse(200, str(result))
            else:
                # Try fallback to app's HTTP handler if available
                if hasattr(self.app, '_handle_http'):
                    # Parse URL to get query string
                    from urllib.parse import urlparse
                    parsed = urlparse(request.get('url', path))
                    query_string = parsed.query.encode() if parsed.query else b''
                    
                    # Build ASGI scope for internal handler
                    scope = {
                        'type': 'http',
                        'method': method,
                        'path': path,
                        'query_string': query_string,
                        'headers': [(k.encode(), v.encode()) for k, v in request.get('headers', {}).items()]
                    }
                    
                    # Mock receive function
                    async def receive():
                        return {
                            'type': 'http.request',
                            'body': request['body'].encode() if request.get('body') else b'',
                            'more_body': False
                        }
                    
                    # Mock send function to capture response
                    response_data = {'status': 200, 'body': b'', 'headers': []}
                    
                    async def send(message):
                        if message['type'] == 'http.response.start':
                            response_data['status'] = message['status']
                            response_data['headers'] = message.get('headers', [])
                        elif message['type'] == 'http.response.body':
                            response_data['body'] += message.get('body', b'')
                    
                    # Execute request through app (use __call__ for ASGI)
                    await self.app(scope, receive, send)
                    
                    # Convert headers back to dict
                    headers = {k.decode(): v.decode() for k, v in response_data['headers']}
                    
                    # Try to parse as JSON, fallback to text
                    body = response_data['body']
                    if headers.get('content-type', '').startswith('application/json'):
                        try:
                            content = json.loads(body.decode())
                        except:
                            content = body.decode()
                    else:
                        content = body.decode()
                    
                    return TestResponse(response_data['status'], content, headers)
                else:
                    return TestResponse(404, {"error": "Not found", "path": path, "method": method})
                    
        except Exception as e:
            logger.error(f"Test request error: {e}")
            return TestResponse(500, {"error": f"Internal server error: {str(e)}"})
    
    def request(self, method: str, url: str, **kwargs) -> TestResponse:
        """Generic request method with proper async handling"""
        request = self._build_request(method, url, **kwargs)
        
        try:
            # Check if we're in an async context
            import asyncio
            try:
                current_loop = asyncio.get_running_loop()
                # We're already in a running loop - need to create new loop
                import concurrent.futures
                import threading
                
                def run_in_new_loop():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self._execute_request(request))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_new_loop)
                    return future.result()
                    
            except RuntimeError:
                # No running loop - we can create our own
                loop = self._get_loop()
                return loop.run_until_complete(self._execute_request(request))
                
        except Exception as e:
            logger.error(f"Request execution failed: {e}")
            return TestResponse(500, {"error": f"Test execution failed: {str(e)}"})
    
    def get(self, url: str, **kwargs) -> TestResponse:
        """Send GET request"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> TestResponse:
        """Send POST request"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> TestResponse:
        """Send PUT request"""
        return self.request('PUT', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> TestResponse:
        """Send PATCH request"""
        return self.request('PATCH', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> TestResponse:
        """Send DELETE request"""
        return self.request('DELETE', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> TestResponse:
        """Send OPTIONS request"""
        return self.request('OPTIONS', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> TestResponse:
        """Send HEAD request"""
        return self.request('HEAD', url, **kwargs)


# Test utilities
class TestDatabase:
    """In-memory test database for testing"""
    
    def __init__(self):
        from .database import DatabaseConnection
        self.db = DatabaseConnection('sqlite:///:memory:')
    
    def reset(self):
        """Reset test database"""
        # Drop all tables and recreate
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            cursor.execute(f"DROP TABLE {table[0]}")
        
        self.db.connection.commit()
        self.db._create_default_tables()
    
    def seed_admin_user(self, username: str = "admin", email: str = "admin@test.com", password: str = "admin123"):
        """Create test admin user"""
        return self.db.create_admin_user(username, email, password)


def create_test_app():
    """Create a test CREATESONLINE app"""
    from . import create_app
    return create_app(title="Test App", debug=False)