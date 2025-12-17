# createsonline/config/settings.py
"""
CREATESONLINE Settings Management

Simple, unified settings for CREATESONLINE applications.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path

class CreatesonlineSettings:
    """Simple settings manager for CREATESONLINE framework"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize settings from environment variables and .env file"""
        self.env_file = env_file or '.env'
        self._load_env_file()
        
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                # dotenv not installed, skip loading
                pass
    
    # Core application settings
    @property
    def DEBUG(self) -> bool:
        return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    @property
    def SECRET_KEY(self) -> str:
        return os.getenv('SECRET_KEY', 'createsonline-dev-key-change-in-production')
    
    @property
    def HOST(self) -> str:
        return os.getenv('HOST', '127.0.0.1')
    
    @property
    def PORT(self) -> int:
        return int(os.getenv('PORT', '8000'))
    
    @property
    def ENVIRONMENT(self) -> str:
        return os.getenv('ENVIRONMENT', 'development')
    
    # Database settings
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv('DATABASE_URL', 'sqlite:///./createsonline.db')
    
    @property
    def DATABASE_ECHO(self) -> bool:
        return os.getenv('DATABASE_ECHO', 'false').lower() in ('true', '1', 'yes')
    
    # AI settings
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def ANTHROPIC_API_KEY(self) -> Optional[str]:
        return os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def AI_CACHE_TTL(self) -> int:
        return int(os.getenv('AI_CACHE_TTL', '3600'))  # 1 hour
    
    @property
    def AI_ENABLED(self) -> bool:
        return os.getenv('AI_ENABLED', 'true').lower() in ('true', '1', 'yes')
    
    # Admin settings
    @property
    def ADMIN_ENABLED(self) -> bool:
        return os.getenv('ADMIN_ENABLED', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def ADMIN_PATH(self) -> str:
        return os.getenv('ADMIN_PATH', '/admin')
    
    # Authentication settings
    @property
    def AUTH_ENABLED(self) -> bool:
        return os.getenv('AUTH_ENABLED', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def SESSION_TIMEOUT(self) -> int:
        return int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
    
    @property
    def PASSWORD_MIN_LENGTH(self) -> int:
        return int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    
    # CORS settings
    @property
    def CORS_ORIGINS(self) -> list:
        origins = os.getenv('CORS_ORIGINS', '')
        if origins:
            return [origin.strip() for origin in origins.split(',')]
        return ['*'] if self.DEBUG else []
    
    # Static files settings (Django-style)
    @property
    def STATIC_URL(self) -> str:
        """URL prefix for static files"""
        return os.getenv('STATIC_URL', '/static/')
    
    @property
    def STATIC_ROOT(self) -> Optional[Path]:
        """Directory for collected static files (for production)"""
        static_root = os.getenv('STATIC_ROOT')
        return Path(static_root) if static_root else None
    
    @property
    def STATICFILES_DIRS(self) -> list:
        """Additional directories to search for static files"""
        # Get from environment (comma-separated paths)
        dirs_str = os.getenv('STATICFILES_DIRS', '')
        if dirs_str:
            return [Path(d.strip()) for d in dirs_str.split(',') if d.strip()]
        
        # Auto-discover: Look for 'static' directory in project root
        base_dir = Path.cwd()
        static_dir = base_dir / "static"
        
        if static_dir.exists():
            return [static_dir]
        return []
    
    @property
    def TEMPLATE_DIRS(self) -> list:
        """Directories to search for templates"""
        # Get from environment
        dirs_str = os.getenv('TEMPLATE_DIRS', '')
        if dirs_str:
            return [Path(d.strip()) for d in dirs_str.split(',') if d.strip()]
        
        # Auto-discover: Look for 'templates' directory in project root
        base_dir = Path.cwd()
        template_dir = base_dir / "templates"
        
        if template_dir.exists():
            return [template_dir]
        return []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key"""
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'DEBUG': self.DEBUG,
            'SECRET_KEY': self.SECRET_KEY,
            'HOST': self.HOST,
            'PORT': self.PORT,
            'ENVIRONMENT': self.ENVIRONMENT,
            'DATABASE_URL': self.DATABASE_URL,
            'DATABASE_ECHO': self.DATABASE_ECHO,
            'AI_ENABLED': self.AI_ENABLED,
            'AI_CACHE_TTL': self.AI_CACHE_TTL,
            'ADMIN_ENABLED': self.ADMIN_ENABLED,
            'ADMIN_PATH': self.ADMIN_PATH,
            'AUTH_ENABLED': self.AUTH_ENABLED,
            'SESSION_TIMEOUT': self.SESSION_TIMEOUT,
            'PASSWORD_MIN_LENGTH': self.PASSWORD_MIN_LENGTH,
            'CORS_ORIGINS': self.CORS_ORIGINS,
        }

# Global settings instance
settings = CreatesonlineSettings()