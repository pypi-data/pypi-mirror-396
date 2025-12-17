"""
CREATESONLINE Internal Request Handling

Request object and utilities for handling HTTP requests in internal ASGI mode.
"""
from typing import Dict, Any, Optional
from urllib.parse import parse_qs


class CreatesonlineInternalRequest:
    """Internal request object for zero-dependency mode"""
    
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self.method = scope.get('method', 'GET')
        self.path = scope.get('path', '/')
        self.url = self._build_url(scope)
        self.query_params = self._parse_query_string(scope.get('query_string', b'').decode())
        self.headers = self._parse_headers(scope.get('headers', []))
        self._body = None
        self._json_data = None
    
    def _build_url(self, scope) -> str:
        """Build full URL from ASGI scope"""
        scheme = scope.get('scheme', 'http')
        server = scope.get('server', ('localhost', 8000))
        host, port = server
        path = scope.get('path', '/')
        query_string = scope.get('query_string', b'').decode()
        
        if (scheme == 'https' and port == 443) or (scheme == 'http' and port == 80):
            url = f"{scheme}://{host}{path}"
        else:
            url = f"{scheme}://{host}:{port}{path}"
        
        if query_string:
            url += f"?{query_string}"
        
        return url
    
    def _parse_query_string(self, query_string: str) -> Dict[str, Any]:
        """Parse query string into dictionary"""
        if not query_string:
            return {}
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(query_string).items()}
    
    def _parse_headers(self, headers: list) -> Dict[str, str]:
        """Parse ASGI headers format to dictionary"""
        header_dict = {}
        for name, value in headers:
            key = name.decode('latin-1').lower()
            header_dict[key] = value.decode('latin-1')
        return header_dict
    
    async def json(self) -> Dict[str, Any]:
        """Parse request body as JSON"""
        if self._json_data is None:
            import json
            body = await self._get_body()
            try:
                self._json_data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._json_data = {}
        return self._json_data
    
    async def body(self) -> bytes:
        """Get raw request body"""
        return await self._get_body()
    
    async def _get_body(self) -> bytes:
        """Read body from request stream"""
        if self._body is None:
            body_parts = []
            while True:
                message = await self.receive()
                if message['type'] == 'http.request':
                    body_parts.append(message.get('body', b''))
                    if not message.get('more_body', False):
                        break
            self._body = b''.join(body_parts)
        return self._body
    
    @property
    def client_ip(self) -> Optional[str]:
        """Get client IP address"""
        client = self.scope.get('client')
        return client[0] if client else None
    
    @property
    def is_secure(self) -> bool:
        """Check if request is HTTPS"""
        return self.scope.get('scheme') == 'https'
