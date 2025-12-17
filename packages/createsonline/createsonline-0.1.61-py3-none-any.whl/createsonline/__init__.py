# createsonline/__init__.py
"""
CREATESONLINE - The AI-Native Web Framework

Build Intelligence Into Everything
"""

from pathlib import Path

def _get_version():
    """Get version from package metadata or VERSION file"""
    try:
        # Try to get version from package metadata (works when installed via pip)
        from importlib.metadata import version
        return version('createsonline')
    except Exception:
        # Fallback to VERSION file (for development)
        version_file = Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return '1.41.0'

__version__ = _get_version()
__framework_name__ = 'CREATESONLINE'
__tagline__ = 'Build Intelligence Into Everything'
__author__ = 'Ahmed Hassan'
__license__ = 'MIT'

# Import main API
from .app import CreatesonlineInternalApp, create_app
from .server import run_server
from .static_files import StaticFileHandler, serve_static, serve_template
from .templates import render_template, render_to_response, TemplateEngine
from .project_init import ProjectInitializer, auto_discover_routes, init_project_if_needed

# Session and Authentication (v1.55.0)
from .session import (
    SessionManager,
    SessionMiddleware,
    get_session,
    get_user_id,
    is_authenticated,
    set_session_cookie,
    clear_session_cookie
)
from .decorators import (
    require_login,
    require_role,
    require_any_role,
    require_permission,
    optional_login
)

# Secure Database Sessions (v1.55.0)
from .database_session import (
    SecureDatabaseSessionManager,
    create_secure_session_manager
)

__all__ = [
    'create_app',
    'CreatesonlineInternalApp',
    'run_server',
    'StaticFileHandler',
    'serve_static',
    'serve_template',
    'render_template',
    'render_to_response',
    'TemplateEngine',
    'ProjectInitializer',
    'auto_discover_routes',
    'init_project_if_needed',
    # Session & Auth (v1.55.0)
    'SessionManager',
    'SessionMiddleware',
    'get_session',
    'get_user_id',
    'is_authenticated',
    'set_session_cookie',
    'clear_session_cookie',
    'require_login',
    'require_role',
    'require_any_role',
    'require_permission',
    'optional_login',
    # Secure Database Sessions (v1.55.0)
    'SecureDatabaseSessionManager',
    'create_secure_session_manager',
    '__version__',
]


