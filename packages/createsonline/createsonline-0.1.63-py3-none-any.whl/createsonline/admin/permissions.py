# createsonline/admin/permissions.py
"""
CREATESONLINE Admin Permission System

Permission decorators and helpers for admin views.
"""
from functools import wraps
from typing import Callable, Optional


class PermissionDenied(Exception):
    """Raised when user doesn't have required permission"""
    pass


def staff_required(func: Callable) -> Callable:
    """
    Decorator to require user to be staff
    
    Usage:
        @staff_required
        async def my_view(request):
            ...
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        user = getattr(request, 'user', None)
        
        if not user or not user.is_staff:
            return await self._show_login(request, error="Staff access required")
        
        return await func(self, request, *args, **kwargs)
    
    return wrapper


def superuser_required(func: Callable) -> Callable:
    """
    Decorator to require user to be superuser
    
    Usage:
        @superuser_required
        async def my_view(request):
            ...
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        user = getattr(request, 'user', None)
        
        if not user or not user.is_superuser:
            return await self._show_permission_denied(request, "Superuser access required")
        
        return await func(self, request, *args, **kwargs)
    
    return wrapper


def permission_required(permission: str, raise_exception: bool = True) -> Callable:
    """
    Decorator to require specific permission
    
    Args:
        permission: Permission string like "auth.add_user"
        raise_exception: If True, raise PermissionDenied; else redirect to login
    
    Usage:
        @permission_required("auth.add_user")
        async def my_view(request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user or not user.has_permission(permission):
                if raise_exception:
                    raise PermissionDenied(f"Permission required: {permission}")
                return await self._show_permission_denied(
                    request,
                    f"You don't have permission: {permission}"
                )
            
            return await func(self, request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def permissions_required(*permissions, require_all: bool = True) -> Callable:
    """
    Decorator to require multiple permissions
    
    Args:
        *permissions: Permission strings
        require_all: If True, require all permissions; else require any
    
    Usage:
        @permissions_required("auth.add_user", "auth.change_user")
        async def my_view(request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user:
                return await self._show_permission_denied(request, "Authentication required")
            
            if require_all:
                # User must have all permissions
                missing = [p for p in permissions if not user.has_permission(p)]
                if missing:
                    return await self._show_permission_denied(
                        request,
                        f"Missing permissions: {', '.join(missing)}"
                    )
            else:
                # User must have at least one permission
                if not any(user.has_permission(p) for p in permissions):
                    return await self._show_permission_denied(
                        request,
                        f"Requires one of: {', '.join(permissions)}"
                    )
            
            return await func(self, request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def module_permission_required(app_label: str) -> Callable:
    """
    Decorator to require any permission for a module
    
    Args:
        app_label: Application label like "auth"
    
    Usage:
        @module_permission_required("auth")
        async def my_view(request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user or not user.has_module_permission(app_label):
                return await self._show_permission_denied(
                    request,
                    f"No permissions for module: {app_label}"
                )
            
            return await func(self, request, *args, **kwargs)
        
        return wrapper
    
    return decorator


class PermissionChecker:
    """Helper class for checking permissions in templates and views"""
    
    def __init__(self, user):
        self.user = user
    
    def has_perm(self, permission: str) -> bool:
        """Check if user has permission"""
        if not self.user:
            return False
        return self.user.has_permission(permission)
    
    def has_perms(self, permissions: list, require_all: bool = True) -> bool:
        """Check if user has multiple permissions"""
        if not self.user:
            return False
        
        if require_all:
            return all(self.user.has_permission(p) for p in permissions)
        else:
            return any(self.user.has_permission(p) for p in permissions)
    
    def has_module_perms(self, app_label: str) -> bool:
        """Check if user has any permission for module"""
        if not self.user:
            return False
        return self.user.has_module_permission(app_label)
    
    @property
    def is_staff(self) -> bool:
        """Check if user is staff"""
        return self.user and self.user.is_staff
    
    @property
    def is_superuser(self) -> bool:
        """Check if user is superuser"""
        return self.user and self.user.is_superuser
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user and self.user.is_authenticated


def get_model_permissions(model_class) -> list:
    """
    Get default permissions for a model
    
    Returns:
        List of permission codenames
    """
    model_name = model_class.__name__.lower()
    return [
        f"add_{model_name}",
        f"change_{model_name}",
        f"delete_{model_name}",
        f"view_{model_name}",
    ]


def create_model_permissions(model_class, content_type: str):
    """
    Create Permission objects for a model
    
    Args:
        model_class: SQLAlchemy model class
        content_type: Content type string (e.g., "auth")
    
    Returns:
        List of Permission instances
    """
    from createsonline.auth.models import Permission
    
    model_name = model_class.__name__.lower()
    verbose_name = model_class.__name__.replace('_', ' ').title()
    
    permissions = [
        Permission(
            name=f"Can add {verbose_name}",
            codename=f"add_{model_name}",
            content_type=content_type
        ),
        Permission(
            name=f"Can change {verbose_name}",
            codename=f"change_{model_name}",
            content_type=content_type
        ),
        Permission(
            name=f"Can delete {verbose_name}",
            codename=f"delete_{model_name}",
            content_type=content_type
        ),
        Permission(
            name=f"Can view {verbose_name}",
            codename=f"view_{model_name}",
            content_type=content_type
        ),
    ]
    
    return permissions
