# createsonline/performance/compression.py
"""
Ultra-Fast Response Compression for CREATESONLINE

Advanced compression algorithms that reduce bandwidth and improve speed:
- Brotli compression
- Gzip compression with custom levels
- Smart compression detection
- Streaming compression
"""

import gzip
import zlib
import json
from typing import Union, Dict, Any, Optional


class ResponseCompression:
    """
    Ultra-fast response compression system
    """
    
    def __init__(self):
        self.compression_threshold = 1024  # Only compress responses > 1KB
        self.compression_level = 6  # Balance between speed and ratio
        
        # Try to import brotli for better compression
        try:
            import brotli
            self.brotli_available = True
            self.brotli = brotli
        except ImportError:
            self.brotli_available = False
    
    def compress_response(self, content: Union[str, bytes], accept_encoding: str = "") -> Dict[str, Any]:
        """
        Compress response content with optimal algorithm
        
        Returns:
            {
                'content': compressed_bytes,
                'encoding': 'br'|'gzip'|'deflate'|None,
                'original_size': int,
                'compressed_size': int,
                'compression_ratio': float
            }
        """
        
        # Convert to bytes if needed
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        original_size = len(content_bytes)
        
        # Don't compress small responses
        if original_size < self.compression_threshold:
            return {
                'content': content_bytes,
                'encoding': None,
                'original_size': original_size,
                'compressed_size': original_size,
                'compression_ratio': 1.0
            }
        
        # Determine best compression method
        if self.brotli_available and 'br' in accept_encoding:
            return self._compress_brotli(content_bytes, original_size)
        elif 'gzip' in accept_encoding:
            return self._compress_gzip(content_bytes, original_size)
        elif 'deflate' in accept_encoding:
            return self._compress_deflate(content_bytes, original_size)
        else:
            # No compression
            return {
                'content': content_bytes,
                'encoding': None,
                'original_size': original_size,
                'compressed_size': original_size,
                'compression_ratio': 1.0
            }
    
    def _compress_brotli(self, content: bytes, original_size: int) -> Dict[str, Any]:
        """Compress with Brotli (best compression ratio)"""
        
        compressed = self.brotli.compress(
            content,
            quality=4,  # Fast compression
            lgwin=22    # Window size for better compression
        )
        
        return {
            'content': compressed,
            'encoding': 'br',
            'original_size': original_size,
            'compressed_size': len(compressed),
            'compression_ratio': original_size / len(compressed)
        }
    
    def _compress_gzip(self, content: bytes, original_size: int) -> Dict[str, Any]:
        """Compress with Gzip"""
        
        compressed = gzip.compress(content, compresslevel=self.compression_level)
        
        return {
            'content': compressed,
            'encoding': 'gzip',
            'original_size': original_size,
            'compressed_size': len(compressed),
            'compression_ratio': original_size / len(compressed)
        }
    
    def _compress_deflate(self, content: bytes, original_size: int) -> Dict[str, Any]:
        """Compress with Deflate"""
        
        compressed = zlib.compress(content, level=self.compression_level)
        
        return {
            'content': compressed,
            'encoding': 'deflate',
            'original_size': original_size,
            'compressed_size': len(compressed),
            'compression_ratio': original_size / len(compressed)
        }
    
    def should_compress(self, content_type: str, content_length: int) -> bool:
        """Determine if content should be compressed"""
        
        # Don't compress small content
        if content_length < self.compression_threshold:
            return False
        
        # Don't compress already compressed content
        non_compressible = [
            'image/', 'video/', 'audio/',
            'application/zip', 'application/gzip',
            'application/x-rar', 'application/pdf'
        ]
        
        for non_comp in non_compressible:
            if non_comp in content_type.lower():
                return False
        
        # Compress text-based content
        compressible = [
            'text/', 'application/json', 'application/xml',
            'application/javascript', 'application/css',
            'application/html'
        ]
        
        for comp in compressible:
            if comp in content_type.lower():
                return True
        
        return False
    
    def get_best_encoding(self, accept_encoding: str) -> Optional[str]:
        """Get the best compression encoding from Accept-Encoding header"""
        
        if not accept_encoding:
            return None
        
        accept_encoding = accept_encoding.lower()
        
        # Prefer brotli if available and supported
        if self.brotli_available and 'br' in accept_encoding:
            return 'br'
        elif 'gzip' in accept_encoding:
            return 'gzip'
        elif 'deflate' in accept_encoding:
            return 'deflate'
        else:
            return None


class StreamingCompression:
    """
    Streaming compression for large responses
    """
    
    def __init__(self, encoding: str = 'gzip'):
        self.encoding = encoding
        
        if encoding == 'gzip':
            self.compressor = zlib.compressobj(
                level=6,
                method=zlib.DEFLATED,
                wbits=zlib.MAX_WBITS | 16  # Add gzip header
            )
        elif encoding == 'deflate':
            self.compressor = zlib.compressobj(level=6)
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
    
    def compress_chunk(self, chunk: bytes) -> bytes:
        """Compress a chunk of data"""
        return self.compressor.compress(chunk)
    
    def finalize(self) -> bytes:
        """Finalize compression and return remaining data"""
        return self.compressor.flush()


class JSONCompression:
    """
    Specialized JSON compression with optimizations
    """
    
    def __init__(self):
        self.common_keys = [
            'id', 'name', 'type', 'value', 'data', 'status', 'message',
            'error', 'success', 'timestamp', 'created', 'updated'
        ]
        
        # Build key mapping for compression
        self.key_map = {key: chr(65 + i) for i, key in enumerate(self.common_keys)}
        self.reverse_key_map = {v: k for k, v in self.key_map.items()}
    
    def compress_json(self, data: Dict[str, Any]) -> str:
        """Compress JSON by replacing common keys with single characters"""
        
        def replace_keys(obj):
            if isinstance(obj, dict):
                new_obj = {}
                for key, value in obj.items():
                    new_key = self.key_map.get(key, key)
                    new_obj[new_key] = replace_keys(value)
                return new_obj
            elif isinstance(obj, list):
                return [replace_keys(item) for item in obj]
            else:
                return obj
        
        compressed_data = replace_keys(data)
        return json.dumps(compressed_data, separators=(',', ':'))
    
    def decompress_json(self, compressed_str: str) -> Dict[str, Any]:
        """Decompress JSON by restoring original keys"""
        
        def restore_keys(obj):
            if isinstance(obj, dict):
                new_obj = {}
                for key, value in obj.items():
                    original_key = self.reverse_key_map.get(key, key)
                    new_obj[original_key] = restore_keys(value)
                return new_obj
            elif isinstance(obj, list):
                return [restore_keys(item) for item in obj]
            else:
                return obj
        
        data = json.loads(compressed_str)
        return restore_keys(data)


# Global compression instance
_global_compressor = None

def get_compressor() -> ResponseCompression:
    """Get global compression instance"""
    global _global_compressor
    if _global_compressor is None:
        _global_compressor = ResponseCompression()
    return _global_compressor


def compress_middleware():
    """Middleware for automatic response compression"""
    
    def middleware(app):
        original_call = app.__call__
        compressor = get_compressor()
        
        async def compressed_app(scope, receive, send):
            if scope['type'] != 'http':
                await original_call(scope, receive, send)
                return
            
            # Get Accept-Encoding header
            headers = dict(scope.get('headers', []))
            accept_encoding = headers.get(b'accept-encoding', b'').decode()
            
            # Wrap send to compress response
            async def compressed_send(message):
                if message['type'] == 'http.response.start':
                    # Store response start for later
                    compressed_send.response_start = message
                elif message['type'] == 'http.response.body':
                    body = message.get('body', b'')
                    
                    if body and hasattr(compressed_send, 'response_start'):
                        # Get content type
                        headers = dict(compressed_send.response_start.get('headers', []))
                        content_type = headers.get(b'content-type', b'').decode()
                        
                        # Compress if appropriate
                        if compressor.should_compress(content_type, len(body)):
                            result = compressor.compress_response(body, accept_encoding)
                            
                            if result['encoding']:
                                # Update headers
                                new_headers = []
                                for name, value in compressed_send.response_start.get('headers', []):
                                    if name.lower() != b'content-length':
                                        new_headers.append([name, value])
                                
                                new_headers.extend([
                                    [b'content-encoding', result['encoding'].encode()],
                                    [b'content-length', str(result['compressed_size']).encode()],
                                    [b'x-compression-ratio', f"{result['compression_ratio']:.2f}".encode()]
                                ])
                                
                                compressed_send.response_start['headers'] = new_headers
                                body = result['content']
                    
                    # Send response start if not sent yet
                    if hasattr(compressed_send, 'response_start'):
                        await send(compressed_send.response_start)
                        del compressed_send.response_start
                    
                    # Send compressed body
                    await send({
                        'type': 'http.response.body',
                        'body': body,
                        'more_body': message.get('more_body', False)
                    })
                else:
                    await send(message)
            
            await original_call(scope, receive, compressed_send)
        
        return compressed_app
    
    return middleware
