"""
Authentication Decorators for CREATESONLINE
Provides @require_login and @require_role decorators
"""
from functools import wraps
from typing import List, Union, Callable, Optional
from createsonline.session import get_session, get_user_id


def require_login(redirect_to: str = '/login'):
    """
    Decorator to require user login
    
    Usage:
        @require_login()
        async def dashboard(request):
            user_id = get_user_id(request)
            return {"user_id": user_id}
        
        @require_login(redirect_to='/account/login')
        async def profile(request):
            return {"page": "profile"}
    
    Args:
        redirect_to: URL to redirect to if not logged in (default: '/login')
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            user_id = get_user_id(request)
            
            if user_id is None:
                # User not logged in - redirect
                return {"redirect": redirect_to}, 302
            
            # User logged in - proceed
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_role(roles: Union[str, List[str]], redirect_to: str = '/login', role_key: str = 'role'):
    """
    Decorator to require specific user role(s)
    
    Usage:
        @require_role('admin')
        async def admin_panel(request):
            return {"page": "admin"}
        
        @require_role(['admin', 'moderator'])
        async def manage_users(request):
            return {"page": "manage_users"}
        
        @require_role('seller', redirect_to='/account/login', role_key='user_role')
        async def seller_dashboard(request):
            return {"page": "seller"}
    
    Args:
        roles: Required role(s) - single string or list of strings
        redirect_to: URL to redirect if not authorized (default: '/login')
        role_key: Session key for role (default: 'role')
    
    Returns:
        Decorator function
    """
    # Normalize roles to list
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            session = get_session(request)
            user_id = session.get('user_id')
            user_role = session.get(role_key)
            
            if user_id is None:
                # Not logged in - redirect to login
                return {"redirect": redirect_to}, 302
            
            if user_role not in roles:
                # Wrong role - return 403 Forbidden
                return {
                    "error": "Access Denied",
                    "message": f"This page requires {' or '.join(roles)} role"
                }, 403
            
            # Authorized - proceed
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_any_role(roles: List[str], redirect_to: str = '/login', role_key: str = 'role'):
    """
    Decorator to require any of the specified roles (alias for require_role)
    
    Same as require_role but more explicit name for multiple roles
    
    Usage:
        @require_any_role(['admin', 'moderator', 'staff'])
        async def admin_area(request):
            return {"page": "admin_area"}
    """
    return require_role(roles, redirect_to, role_key)


def require_permission(permission: str, redirect_to: str = '/login', permission_key: str = 'permissions'):
    """
    Decorator to require specific permission
    
    Usage:
        @require_permission('can_edit_products')
        async def edit_product(request):
            return {"page": "edit_product"}
        
        @require_permission('can_delete_users', redirect_to='/dashboard')
        async def delete_user(request):
            return {"page": "delete_user"}
    
    Args:
        permission: Required permission string
        redirect_to: URL to redirect if not authorized
        permission_key: Session key for permissions list (default: 'permissions')
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            session = get_session(request)
            user_id = session.get('user_id')
            permissions = session.get(permission_key, [])
            
            if user_id is None:
                # Not logged in
                return {"redirect": redirect_to}, 302
            
            if permission not in permissions:
                # Missing permission
                return {
                    "error": "Access Denied",
                    "message": f"This action requires '{permission}' permission"
                }, 403
            
            # Has permission - proceed
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def optional_login(func: Callable):
    """
    Decorator for routes that work with or without login
    
    Adds user info to kwargs if logged in, but doesn't require it
    
    Usage:
        @optional_login
        async def homepage(request, user_id=None, **kwargs):
            if user_id:
                return {"message": f"Welcome back, user {user_id}!"}
            else:
                return {"message": "Welcome, guest!"}
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        user_id = get_user_id(request)
        session = get_session(request)
        
        # Add user info to kwargs
        kwargs['user_id'] = user_id
        kwargs['session'] = session
        
        return await func(request, *args, **kwargs)
    
    return wrapper
