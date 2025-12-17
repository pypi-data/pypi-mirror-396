"""
Session Management for CREATESONLINE
Provides cookie-based session management with JWT tokens
"""
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class SessionManager:
    """Manages user sessions with JWT tokens"""
    
    def __init__(self, secret_key: Optional[str] = None, expiry_days: int = 30):
        """
        Initialize session manager
        
        Args:
            secret_key: Secret key for JWT signing (auto-generated if None)
            expiry_days: Session expiration in days (default: 30)
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.expiry_days = expiry_days
        self.algorithm = 'HS256'
    
    def create_session(self, user_id: int, user_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session token
        
        Args:
            user_id: User ID to store in session
            user_data: Additional user data to store (username, email, role, etc.)
        
        Returns:
            JWT token string
        """
        expiry = datetime.utcnow() + timedelta(days=self.expiry_days)
        
        payload = {
            'user_id': user_id,
            'exp': expiry,
            'iat': datetime.utcnow()
        }
        
        # Add optional user data
        if user_data:
            payload.update(user_data)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session token and return user data
        
        Args:
            token: JWT token string
        
        Returns:
            User data dict if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def get_user_id(self, token: str) -> Optional[int]:
        """
        Get user ID from session token
        
        Args:
            token: JWT token string
        
        Returns:
            User ID if valid, None if invalid/expired
        """
        payload = self.validate_session(token)
        if payload:
            return payload.get('user_id')
        return None
    
    def refresh_session(self, token: str) -> Optional[str]:
        """
        Refresh session token (extend expiry)
        
        Args:
            token: Current JWT token
        
        Returns:
            New JWT token with extended expiry, None if invalid
        """
        payload = self.validate_session(token)
        if not payload:
            return None
        
        # Remove old expiry
        payload.pop('exp', None)
        payload.pop('iat', None)
        
        # Create new token with new expiry
        user_id = payload.pop('user_id')
        return self.create_session(user_id, payload)


class SessionMiddleware:
    """
    ASGI Middleware for session management
    
    Adds session data to request object from cookies
    """
    
    def __init__(self, app, session_manager: SessionManager, cookie_name: str = 'session'):
        """
        Initialize session middleware
        
        Args:
            app: ASGI application
            session_manager: SessionManager instance
            cookie_name: Name of session cookie (default: 'session')
        """
        self.app = app
        self.session_manager = session_manager
        self.cookie_name = cookie_name
    
    async def __call__(self, scope, receive, send):
        """Process ASGI request with session handling"""
        if scope['type'] == 'http':
            # Extract session from cookies
            headers = scope.get('headers', [])
            cookies = {}
            
            for name, value in headers:
                if name == b'cookie':
                    cookie_str = value.decode('utf-8')
                    for cookie in cookie_str.split(';'):
                        cookie = cookie.strip()
                        if '=' in cookie:
                            key, val = cookie.split('=', 1)
                            cookies[key] = val
            
            # Validate session token
            session_token = cookies.get(self.cookie_name)
            session_data = None
            
            if session_token:
                session_data = self.session_manager.validate_session(session_token)
            
            # Add session to scope
            scope['session'] = session_data or {}
            scope['session_manager'] = self.session_manager
            scope['session_cookie_name'] = self.cookie_name
        
        # Pass to next middleware/app
        await self.app(scope, receive, send)


def get_session(request) -> Dict[str, Any]:
    """
    Get session data from request
    
    Args:
        request: Starlette/ASGI request object
    
    Returns:
        Session data dictionary (empty if no session)
    """
    return getattr(request, 'scope', {}).get('session', {})


def get_user_id(request) -> Optional[int]:
    """
    Get logged-in user ID from request session
    
    Args:
        request: Request object
    
    Returns:
        User ID if logged in, None otherwise
    """
    session = get_session(request)
    return session.get('user_id')


def is_authenticated(request) -> bool:
    """
    Check if user is authenticated
    
    Args:
        request: Request object
    
    Returns:
        True if user is logged in, False otherwise
    """
    return get_user_id(request) is not None


def set_session_cookie(response, token: str, cookie_name: str = 'session', max_age: int = 2592000):
    """
    Set session cookie in response
    
    Args:
        response: Response object
        token: JWT session token
        cookie_name: Cookie name (default: 'session')
        max_age: Cookie max age in seconds (default: 30 days)
    """
    # Add Set-Cookie header
    cookie_value = f"{cookie_name}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"
    
    # Check if response has headers attribute
    if hasattr(response, 'headers'):
        response.headers['Set-Cookie'] = cookie_value
    elif hasattr(response, 'init_headers'):
        response.init_headers.append(('Set-Cookie', cookie_value.encode()))
    
    return response


def clear_session_cookie(response, cookie_name: str = 'session'):
    """
    Clear session cookie (logout)
    
    Args:
        response: Response object
        cookie_name: Cookie name (default: 'session')
    """
    cookie_value = f"{cookie_name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
    
    if hasattr(response, 'headers'):
        response.headers['Set-Cookie'] = cookie_value
    elif hasattr(response, 'init_headers'):
        response.init_headers.append(('Set-Cookie', cookie_value.encode()))
    
    return response
