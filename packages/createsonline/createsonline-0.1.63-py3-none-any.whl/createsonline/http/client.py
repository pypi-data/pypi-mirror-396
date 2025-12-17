"""
CREATESONLINE Internal HTTP Client Implementation

Pure Python HTTP client with zero external dependencies.
Supports sync/async operations, authentication, file uploads, and more.
"""

import asyncio
import json
import ssl
import socket
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Union
import time


# Custom exception classes
class HTTPError(Exception):
    """Base HTTP error"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional['HTTPResponse'] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ConnectionError(HTTPError):
    """Connection failed"""
    pass


class TimeoutError(HTTPError):
    """Request timeout"""
    pass


class RequestError(HTTPError):
    """Invalid request"""
    pass


class HTTPResponse:
    """HTTP Response object"""
    
    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        url: str,
        encoding: str = 'utf-8'
    ):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.url = url
        self.encoding = encoding
        self._json_cache = None
    
    @property
    def text(self) -> str:
        """Get response as text"""
        return self.content.decode(self.encoding, errors='replace')
    
    def json(self) -> Dict[str, Any]:
        """Parse response as JSON"""
        if self._json_cache is None:
            try:
                self._json_cache = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise HTTPError(f"Failed to parse JSON: {e}")
        return self._json_cache
    
    @property
    def ok(self) -> bool:
        """Check if response is successful (2xx status code)"""
        return 200 <= self.status_code < 300
    
    def raise_for_status(self):
        """Raise HTTPError for bad responses"""
        if not self.ok:
            raise HTTPError(
                f"HTTP {self.status_code} Error",
                status_code=self.status_code,
                response=self
            )


class HTTPRequest:
    """HTTP Request object"""
    
    def __init__(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[float] = None
    ):
        self.method = method.upper()
        self.url = url
        self.headers = headers or {}
        self.data = data
        self.json_data = json_data
        self.files = files or {}
        self.params = params or {}
        self.auth = auth
        self.timeout = timeout or 30.0
        
        # Process URL with parameters
        if self.params:
            parsed = urllib.parse.urlparse(self.url)
            query_params = urllib.parse.parse_qs(parsed.query)
            query_params.update(self.params)
            query_string = urllib.parse.urlencode(query_params, doseq=True)
            self.url = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, query_string, parsed.fragment
            ))
        
        # Set Content-Type for JSON
        if self.json_data:
            self.headers['Content-Type'] = 'application/json'
            self.data = json.dumps(self.json_data).encode('utf-8')
        
        # Handle authentication
        if self.auth:
            import base64
            username, password = self.auth
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.headers['Authorization'] = f'Basic {credentials}'


class HTTPClient:
    """Synchronous HTTP Client"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 30.0,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.base_url = base_url
        self.default_headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Add User-Agent
        self.default_headers.setdefault(
            'User-Agent', 
            'CREATESONLINE-HTTP-Client/1.0'
        )
    
    def _build_url(self, url: str) -> str:
        """Build full URL with base URL"""
        if self.base_url and not url.startswith(('http://', 'https://')):
            return urllib.parse.urljoin(self.base_url, url)
        return url
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge default and request headers"""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
        return final_headers
    
    def _make_request(self, request: HTTPRequest) -> HTTPResponse:
        """Make the actual HTTP request"""
        url = self._build_url(request.url)
        headers = self._prepare_headers(request.headers)
        
        # Create urllib request
        req = urllib.request.Request(
            url=url,
            data=request.data if isinstance(request.data, bytes) else 
                 request.data.encode('utf-8') if request.data else None,
            headers=headers,
            method=request.method
        )
        
        # Create SSL context if needed
        ssl_context = None
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Make request with retry logic
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(
                    req, 
                    timeout=request.timeout,
                    context=ssl_context
                ) as response:
                    content = response.read()
                    status_code = response.getcode()
                    headers_dict = dict(response.headers)
                    
                    return HTTPResponse(
                        status_code=status_code,
                        headers=headers_dict,
                        content=content,
                        url=url
                    )
                    
            except urllib.error.HTTPError as e:
                # HTTP errors (4xx, 5xx) are not retried
                content = e.read() if hasattr(e, 'read') else b''
                return HTTPResponse(
                    status_code=e.code,
                    headers=dict(e.headers) if hasattr(e, 'headers') else {},
                    content=content,
                    url=url
                )
                
            except (urllib.error.URLError, socket.timeout, OSError) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                
                # Convert to our exception types
                if isinstance(e, socket.timeout):
                    raise TimeoutError(f"Request timeout after {request.timeout}s")
                else:
                    raise ConnectionError(f"Connection failed: {e}")
        
        # If we get here, all retries failed
        raise ConnectionError(f"Max retries exceeded: {last_error}")
    
    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> HTTPResponse:
        """Make HTTP request"""
        request = HTTPRequest(method, url, **kwargs)
        return self._make_request(request)
    
    def get(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP GET request"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP POST request"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP PUT request"""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP DELETE request"""
        return self.request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP PATCH request"""
        return self.request('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP HEAD request"""
        return self.request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> HTTPResponse:
        """HTTP OPTIONS request"""
        return self.request('OPTIONS', url, **kwargs)


class AsyncHTTPClient:
    """Asynchronous HTTP Client"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 30.0,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_connections: int = 100
    ):
        self.base_url = base_url
        self.default_headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_connections = max_connections
        
        # Add User-Agent
        self.default_headers.setdefault(
            'User-Agent', 
            'CREATESONLINE-Async-HTTP-Client/1.0'
        )
        
        # Connection semaphore for limiting concurrent connections
        self._connection_semaphore = asyncio.Semaphore(max_connections)
    
    def _build_url(self, url: str) -> str:
        """Build full URL with base URL"""
        if self.base_url and not url.startswith(('http://', 'https://')):
            return urllib.parse.urljoin(self.base_url, url)
        return url
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge default and request headers"""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
        return final_headers
    
    async def _make_request(self, request: HTTPRequest) -> HTTPResponse:
        """Make the actual async HTTP request"""
        async with self._connection_semaphore:
            url = self._build_url(request.url)
            headers = self._prepare_headers(request.headers)
            
            # Parse URL components
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            path = parsed.path or '/'
            if parsed.query:
                path += f'?{parsed.query}'
            
            # Create SSL context if needed
            ssl_context = None
            if parsed.scheme == 'https':
                ssl_context = ssl.create_default_context()
                if not self.verify_ssl:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            
            # Retry logic
            last_error = None
            for attempt in range(self.max_retries + 1):
                try:
                    # Open connection
                    if parsed.scheme == 'https':
                        reader, writer = await asyncio.wait_for(
                            asyncio.open_connection(host, port, ssl=ssl_context),
                            timeout=request.timeout
                        )
                    else:
                        reader, writer = await asyncio.wait_for(
                            asyncio.open_connection(host, port),
                            timeout=request.timeout
                        )
                    
                    try:
                        # Build HTTP request
                        http_request = f"{request.method} {path} HTTP/1.1\r\n"
                        http_request += f"Host: {host}\r\n"
                        
                        for key, value in headers.items():
                            http_request += f"{key}: {value}\r\n"
                        
                        if request.data:
                            content_length = len(request.data)
                            http_request += f"Content-Length: {content_length}\r\n"
                        
                        http_request += "Connection: close\r\n"
                        http_request += "\r\n"
                        
                        # Send request
                        writer.write(http_request.encode('utf-8'))
                        if request.data:
                            writer.write(request.data)
                        await writer.drain()
                        
                        # Read response
                        response_data = await asyncio.wait_for(
                            reader.read(),
                            timeout=request.timeout
                        )
                        
                        # Parse HTTP response
                        response_lines = response_data.decode('utf-8', errors='replace').split('\r\n')
                        status_line = response_lines[0]
                        status_code = int(status_line.split()[1])
                        
                        # Parse headers
                        response_headers = {}
                        body_start = 0
                        for i, line in enumerate(response_lines[1:], 1):
                            if line == '':
                                body_start = i + 1
                                break
                            if ':' in line:
                                key, value = line.split(':', 1)
                                response_headers[key.strip()] = value.strip()
                        
                        # Get body
                        body_text = '\r\n'.join(response_lines[body_start:])
                        content = body_text.encode('utf-8')
                        
                        return HTTPResponse(
                            status_code=status_code,
                            headers=response_headers,
                            content=content,
                            url=url
                        )
                        
                    finally:
                        writer.close()
                        await writer.wait_closed()
                
                except (asyncio.TimeoutError, OSError, ConnectionResetError) as e:
                    last_error = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    
                    # Convert to our exception types
                    if isinstance(e, asyncio.TimeoutError):
                        raise TimeoutError(f"Request timeout after {request.timeout}s")
                    else:
                        raise ConnectionError(f"Connection failed: {e}")
            
            # If we get here, all retries failed
            raise ConnectionError(f"Max retries exceeded: {last_error}")
    
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> HTTPResponse:
        """Make async HTTP request"""
        request = HTTPRequest(method, url, **kwargs)
        return await self._make_request(request)
    
    async def get(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP GET request"""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP POST request"""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP PUT request"""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP DELETE request"""
        return await self.request('DELETE', url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP PATCH request"""
        return await self.request('PATCH', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP HEAD request"""
        return await self.request('HEAD', url, **kwargs)
    
    async def options(self, url: str, **kwargs) -> HTTPResponse:
        """Async HTTP OPTIONS request"""
        return await self.request('OPTIONS', url, **kwargs)
    
    async def close(self):
        """Close the client and cleanup resources"""
        # In a more sophisticated implementation, we'd track open connections
        # and close them here. For now, connections are closed after each request.
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Convenience functions for quick HTTP requests
def get(url: str, **kwargs) -> HTTPResponse:
    """Quick HTTP GET request"""
    client = HTTPClient()
    return client.get(url, **kwargs)


def post(url: str, **kwargs) -> HTTPResponse:
    """Quick HTTP POST request"""
    client = HTTPClient()
    return client.post(url, **kwargs)


def put(url: str, **kwargs) -> HTTPResponse:
    """Quick HTTP PUT request"""
    client = HTTPClient()
    return client.put(url, **kwargs)


def delete(url: str, **kwargs) -> HTTPResponse:
    """Quick HTTP DELETE request"""
    client = HTTPClient()
    return client.delete(url, **kwargs)


async def async_get(url: str, **kwargs) -> HTTPResponse:
    """Quick async HTTP GET request"""
    async with AsyncHTTPClient() as client:
        return await client.get(url, **kwargs)


async def async_post(url: str, **kwargs) -> HTTPResponse:
    """Quick async HTTP POST request"""
    async with AsyncHTTPClient() as client:
        return await client.post(url, **kwargs)


async def async_put(url: str, **kwargs) -> HTTPResponse:
    """Quick async HTTP PUT request"""
    async with AsyncHTTPClient() as client:
        return await client.put(url, **kwargs)


async def async_delete(url: str, **kwargs) -> HTTPResponse:
    """Quick async HTTP DELETE request"""
    async with AsyncHTTPClient() as client:
        return await client.delete(url, **kwargs)