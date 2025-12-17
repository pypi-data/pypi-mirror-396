# createsonline/static_files.py
"""
CREATESONLINE Dynamic Static File Serving System

Automatically serves HTML, CSS, JS, and other static files
with intelligent MIME type detection and caching.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger("createsonline.static")

# Initialize mimetypes
mimetypes.init()

# Additional MIME types for modern web
CUSTOM_MIME_TYPES = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.svg': 'image/svg+xml',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.webp': 'image/webp',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.pdf': 'application/pdf',
    '.zip': 'application/zip',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
}


class StaticFileHandler:
    """
    Dynamic static file serving with intelligent routing
    """
    
    def __init__(self, static_dirs: list = None, template_dirs: list = None):
        """
        Initialize static file handler
        
        Args:
            static_dirs: List of directories to serve static files from
            template_dirs: List of directories to serve templates/HTML from
        """
        self._static_dirs = static_dirs
        self._template_dirs = template_dirs
        
        # Cache for file existence checks
        self._file_cache = {}
        
        logger.info("Static file handler initialized")
    
    @property
    def static_dirs(self):
        """Lazily evaluate static directories using Django-style settings"""
        if self._static_dirs is not None:
            return self._static_dirs
        
        # Import settings here to avoid circular imports
        from .config.settings import settings
        
        # Use STATICFILES_DIRS from settings (Django-style)
        staticfiles_dirs = settings.STATICFILES_DIRS
        
        if staticfiles_dirs:
            # Add subdirectories for better organization
            dirs = []
            for base_dir in staticfiles_dirs:
                dirs.append(base_dir)
                # Also add common subdirectories
                for subdir in ['css', 'js', 'images', 'img', 'icons']:
                    sub_path = base_dir / subdir
                    if sub_path.exists():
                        dirs.append(sub_path)
            return dirs
        
        # Fallback to current directory (backward compatibility)
        cwd = Path.cwd()
        dirs = [
            cwd / "static",
            cwd / "static" / "css",
            cwd / "static" / "js",
            cwd / "static" / "images",
            cwd / "static" / "icons",
        ]
        return dirs
    
    @property
    def template_dirs(self):
        """Lazily evaluate template directories using Django-style settings"""
        if self._template_dirs is not None:
            return self._template_dirs
        
        # Import settings here to avoid circular imports
        from .config.settings import settings
        
        # Use TEMPLATE_DIRS from settings
        template_dirs = settings.TEMPLATE_DIRS
        
        if template_dirs:
            return template_dirs
        
        # Fallback
        cwd = Path.cwd()
        return [cwd / "templates"]
    
    def get_mime_type(self, file_path: str) -> str:
        """
        Get MIME type for a file with fallback support
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        # Check custom types first
        if ext in CUSTOM_MIME_TYPES:
            return CUSTOM_MIME_TYPES[ext]
        
        # Fall back to system mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Default to octet-stream if unknown
        return mime_type or 'application/octet-stream'
    
    def find_file(self, relative_path: str) -> Optional[Path]:
        """
        Find a file in static or template directories
        
        Args:
            relative_path: Relative path to the file
            
        Returns:
            Absolute Path object if found, None otherwise
        """
        # Check cache first
        if relative_path in self._file_cache:
            cached_path = self._file_cache[relative_path]
            if cached_path and cached_path.exists():
                return cached_path
        
        # Remove leading slash if present
        relative_path = relative_path.lstrip('/')
        
        # Strip /static/ prefix if present (URLs come as /static/css/file.css)
        # but we want to search in static_dirs which already points to static/
        search_path = relative_path
        if search_path.startswith('static/'):
            search_path = search_path[7:]  # Remove 'static/' prefix
            logger.debug(f"Stripped 'static/' prefix: '{relative_path}' -> '{search_path}'")
        
        # PRIORITY 1: Check project root for root-level static files
        # (favicon.svg, logo.png, site.webmanifest, robots.txt, etc.)
        project_root = Path.cwd()
        root_file = project_root / search_path
        if root_file.exists() and root_file.is_file():
            # Security check: ensure it's a known static file type
            static_extensions = {'.svg', '.ico', '.png', '.jpg', '.jpeg', '.gif', 
                               '.webp', '.webmanifest', '.json', '.txt', '.xml'}
            if root_file.suffix.lower() in static_extensions:
                self._file_cache[relative_path] = root_file
                logger.debug(f"Found root-level file: {root_file}")
                return root_file
        
        # PRIORITY 2: Check static directories
        for static_dir in self.static_dirs:
            file_path = Path(static_dir) / search_path
            logger.debug(f"Checking: {file_path} (exists={file_path.exists()})")
            if file_path.exists() and file_path.is_file():
                self._file_cache[relative_path] = file_path
                logger.debug(f"Found file: {file_path}")
                return file_path
        
        # PRIORITY 3: Check template directories
        for template_dir in self.template_dirs:
            file_path = Path(template_dir) / search_path
            if file_path.exists() and file_path.is_file():
                self._file_cache[relative_path] = file_path
                return file_path
        
        # Cache miss
        self._file_cache[relative_path] = None
        return None
    
    def serve_file(self, relative_path: str) -> Tuple[bytes, int, Dict[str, str]]:
        """
        Serve a static file
        
        Args:
            relative_path: Relative path to the file
            
        Returns:
            Tuple of (content, status_code, headers)
        """
        file_path = self.find_file(relative_path)
        
        if not file_path:
            error_content = f"File not found: {relative_path}".encode()
            return error_content, 404, {'Content-Type': 'text/plain'}
        
        try:
            # Security check - ensure file is within allowed directories
            resolved_path = file_path.resolve()
            allowed = False
            
            # Allow project root for root-level static files
            project_root = Path.cwd().resolve()
            if str(resolved_path).startswith(str(project_root)):
                # Check if it's a known static file type
                static_extensions = {'.svg', '.ico', '.png', '.jpg', '.jpeg', '.gif', 
                                   '.webp', '.webmanifest', '.json', '.txt', '.xml',
                                   '.css', '.js', '.woff', '.woff2', '.ttf'}
                if resolved_path.suffix.lower() in static_extensions:
                    allowed = True
            
            # Also check configured static/template directories
            if not allowed:
                for static_dir in self.static_dirs + self.template_dirs:
                    if str(resolved_path).startswith(str(Path(static_dir).resolve())):
                        allowed = True
                        break
            
            if not allowed:
                error_content = b"Access denied"
                return error_content, 403, {'Content-Type': 'text/plain'}
            
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Get MIME type
            mime_type = self.get_mime_type(str(file_path))
            
            # Prepare headers
            headers = {
                'Content-Type': mime_type,
                'Content-Length': str(len(content)),
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
            }
            
            # Add additional headers for specific file types
            if mime_type.startswith('text/'):
                headers['Content-Type'] = f"{mime_type}; charset=utf-8"
            
            logger.debug(f"Serving file: {relative_path} ({mime_type}, {len(content)} bytes)")
            
            return content, 200, headers
            
        except Exception as e:
            logger.error(f"Error serving file {relative_path}: {e}")
            error_content = f"Error reading file: {str(e)}".encode()
            return error_content, 500, {'Content-Type': 'text/plain'}
    
    def list_files(self, directory: str = "") -> Dict[str, list]:
        """
        List all files in static directories (for debugging)
        
        Args:
            directory: Subdirectory to list (empty for all)
            
        Returns:
            Dictionary with file listings
        """
        files = {
            'static': [],
            'templates': []
        }
        
        # List static files
        for static_dir in self.static_dirs:
            base_dir = Path(static_dir) / directory
            if base_dir.exists():
                for file_path in base_dir.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(static_dir)
                        files['static'].append(str(rel_path))
        
        # List template files
        for template_dir in self.template_dirs:
            base_dir = Path(template_dir) / directory
            if base_dir.exists():
                for file_path in base_dir.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(template_dir)
                        files['templates'].append(str(rel_path))
        
        return files


# Global static file handler instance
static_handler = StaticFileHandler()


def configure_static_handler(static_dirs: list = None, template_dirs: list = None):
    """
    Manually configure the global static handler (optional).
    
    By default, the handler auto-discovers directories using Django-style settings.
    Only use this if you need to override the auto-discovery.
    
    Args:
        static_dirs: List of static file directories
        template_dirs: List of template directories
    """
    global static_handler
    
    if static_dirs:
        print(f"[DEBUG] Manually configuring static_handler with: {[str(d) for d in static_dirs]}")
        static_handler._static_dirs = static_dirs
    
    if template_dirs:
        static_handler._template_dirs = template_dirs
    
    static_handler._file_cache = {}  # Clear cache


def serve_static(path: str) -> Tuple[bytes, int, Dict[str, str]]:
    """
    Convenience function to serve static files
    
    Args:
        path: Path to the file
        
    Returns:
        Tuple of (content, status_code, headers)
    """
    return static_handler.serve_file(path)


def serve_template(path: str) -> Tuple[bytes, int, Dict[str, str]]:
    """
    Convenience function to serve HTML templates
    
    Args:
        path: Path to the template
        
    Returns:
        Tuple of (content, status_code, headers)
    """
    # Ensure .html extension
    if not path.endswith('.html'):
        path = f"{path}.html"
    
    return static_handler.serve_file(path)
