# createsonline/utils.py
"""
CREATESONLINE Shared Utilities Module

Common functions and utilities used across the framework.
Consolidates duplicate code patterns identified in the codebase.
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union, Callable

# Setup logging
logger = logging.getLogger("createsonline.utils")


# Common Import Error Handler
def get_import_error(module_name: str, feature_name: str = None) -> str:
    """
    Standardized import error message for optional dependencies.
    
    Args:
        module_name: Name of the missing module
        feature_name: Optional feature name that requires the module
    
    Returns:
        Formatted error message
    """
    if feature_name:
        return f" {feature_name} requires {module_name}. Install with: pip install {module_name}"
    return f" Module '{module_name}' not found. Install with: pip install {module_name}"


# Base Info Pattern
class BaseInfoProvider:
    """Base class for standardized info dictionary patterns"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.available = True
        self.features = []
        self.dependencies = []
    
    def get_info(self) -> Dict[str, Any]:
        """Get standardized info dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'available': self.available,
            'features': self.features,
            'dependencies': self.dependencies,
            'timestamp': datetime.utcnow().isoformat(),
            'framework': 'CREATESONLINE'
        }
    
    def add_feature(self, feature: str, description: str = None):
        """Add a feature to the info"""
        self.features.append({
            'name': feature,
            'description': description or f"Feature: {feature}",
            'enabled': True
        })
    
    def add_dependency(self, name: str, version: str = None, optional: bool = False):
        """Add a dependency to the info"""
        self.dependencies.append({
            'name': name,
            'version': version,
            'optional': optional,
            'available': self._check_dependency(name)
        })
    
    def _check_dependency(self, name: str) -> bool:
        """Check if dependency is available"""
        try:
            __import__(name)
            return True
        except ImportError:
            return False


# Metrics Base Class
class BaseMetrics:
    """Base metrics collection mixin"""
    
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.start_time = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def increment_requests(self):
        """Increment request counter"""
        self.requests += 1
        self.last_activity = datetime.utcnow()
    
    def increment_errors(self):
        """Increment error counter"""
        self.errors += 1
        self.last_activity = datetime.utcnow()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get standardized stats dictionary"""
        uptime = datetime.utcnow() - self.start_time
        
        return {
            'requests': self.requests,
            'errors': self.errors,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': self._format_uptime(uptime),
            'last_activity': self.last_activity.isoformat(),
            'error_rate': (self.errors / max(self.requests, 1)) * 100,
            'status': 'healthy' if self.errors == 0 else 'degraded'
        }
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """Format uptime in human readable format"""
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


# Response Formatter
class ResponseFormatter:
    """Standardized response formatting"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Format success response"""
        return {
            'status': 'success',
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'framework': 'CREATESONLINE'
        }
    
    @staticmethod
    def error(message: str, code: int = 500, details: Any = None) -> Dict[str, Any]:
        """Format error response"""
        return {
            'status': 'error',
            'message': message,
            'code': code,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'framework': 'CREATESONLINE'
        }
    
    @staticmethod
    def paginated(data: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
        """Format paginated response"""
        return {
            'status': 'success',
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            },
            'timestamp': datetime.utcnow().isoformat(),
            'framework': 'CREATESONLINE'
        }


# Security Utilities
class SecurityUtils:
    """Common security utilities"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Dict[str, str]:
        """
        Hash password with salt - recommends bcrypt for production.
        
        IMPORTANT: SHA-256 fallback is for development only!
        For production use, install bcrypt: pip install bcrypt
        
        Args:
            password: Plain text password to hash
            salt: Optional salt (used only for SHA-256 fallback, ignored for bcrypt)
            
        Returns:
            Dict with 'hash', 'salt', and 'method' keys
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Try to use bcrypt if available, fallback to SHA-256
        try:
            import bcrypt
            # bcrypt handles salting internally
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return {
                'hash': password_hash,
                'salt': '',  # bcrypt includes salt in hash
                'method': 'bcrypt'
            }
        except ImportError:
            # WARNING: SHA-256 fallback is for development only!
            # For production use, install bcrypt: pip install bcrypt
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return {
                'hash': password_hash,
                'salt': '',  # Empty salt for consistency with verify_password fallback
                'method': 'sha256'
            }
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str = None) -> bool:
        """Verify password against stored hash (consolidated implementation)"""
        # Try bcrypt first if hash looks like bcrypt format
        if stored_hash.startswith(('$2a$', '$2b$', '$2y$')):
            try:
                import bcrypt
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except ImportError:
                pass
        
        # Fallback to SHA-256 verification
        if salt:
            # Salted hash verification
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        else:
            # Simple hash verification (for backward compatibility)
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 1000, escape_html: bool = False) -> str:
        """Enhanced input sanitization with optional HTML escaping"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes and limit length
        value = value.replace('\x00', '').strip()[:max_length]
        
        # Optional HTML escaping for template safety
        if escape_html:
            # Basic HTML entity escaping
            value = (value
                     .replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&#x27;'))
        
        return value


# File Utilities
class FileUtils:
    """Common file operations"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists, create if needed"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Generate safe filename"""
        # Remove dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        safe_filename = ''.join(c for c in filename if c in safe_chars)
        
        # Limit length and ensure it's not empty
        safe_filename = safe_filename[:100]
        if not safe_filename:
            safe_filename = f"file_{secrets.token_hex(8)}"
        
        return safe_filename
    
    @staticmethod
    def get_file_info(path: str, include_error_details: bool = False) -> Dict[str, Any]:
        """Get file information with optional error details for debugging"""
        try:
            stat = os.stat(path)
            return {
                'path': path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_file': os.path.isfile(path),
                'is_dir': os.path.isdir(path),
                'exists': True
            }
        except Exception as e:
            result = {
                'path': path,
                'exists': False
            }
            
            # Include error details in development/debug mode
            if include_error_details:
                result['error'] = str(e)
                result['error_type'] = type(e).__name__
            
            return result


# Validation Utilities
class ValidationUtils:
    """Common validation functions"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_strong_password(password: str) -> Dict[str, Union[bool, List[str]]]:
        """Check password strength"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        
        return {
            'is_strong': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Union[bool, List[str]]]:
        """Validate required fields in data"""
        missing = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing.append(field)
        
        return {
            'is_valid': len(missing) == 0,
            'missing_fields': missing
        }


# Environment Utilities
class EnvUtils:
    """Environment variable utilities"""
    
    @staticmethod
    def get_env_bool(key: str, default: bool = False) -> bool:
        """Get boolean from environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_env_int(key: str, default: int = 0) -> int:
        """Get integer from environment variable"""
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_env_list(key: str, default: List[str] = None, separator: str = ',') -> List[str]:
        """Get list from environment variable"""
        value = os.getenv(key)
        if not value:
            return default or []
        
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get database configuration from environment"""
        return {
            'url': os.getenv('DATABASE_URL', 'sqlite:///createsonline.db'),
            'pool_size': EnvUtils.get_env_int('DATABASE_POOL_SIZE', 5),
            'max_overflow': EnvUtils.get_env_int('DATABASE_MAX_OVERFLOW', 10),
            'echo': EnvUtils.get_env_bool('DATABASE_ECHO', False),
            'auto_create_tables': EnvUtils.get_env_bool('DATABASE_AUTO_CREATE', True)
        }


# Decorator Utilities
def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    
                    import time
                    time.sleep(delay * (backoff ** attempt))
            
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    """Timing decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.debug(f"{func.__name__} executed in {duration:.3f}s")
            return result
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper