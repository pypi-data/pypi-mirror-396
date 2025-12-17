# createsonline/security/__init__.py
"""
CREATESONLINE Security Module

Ultra-high security implementations that prevent vulnerabilities:
- SQL injection protection
- XSS prevention
- CSRF protection
- Rate limiting
- Input validation
- Authentication & authorization
- Encryption utilities
"""

__all__ = [
    'SecurityManager',
    'InputValidator',
    'RateLimiter',
    'CSRFProtection',
    'XSSProtection',
    'SQLInjectionProtection',
    'encrypt_password',
    'verify_password',
    'generate_secure_token',
    'secure_middleware'
]

from .core import SecurityManager, secure_middleware
from .validation import InputValidator
from .rate_limiting import RateLimiter
from .csrf import CSRFProtection
from .xss import XSSProtection
from .encryption import encrypt_password, verify_password, generate_secure_token
from .sql_protection import SQLInjectionProtection