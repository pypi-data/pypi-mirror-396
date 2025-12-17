# createsonline/auth/models.py
"""
CREATESONLINE Authentication Models

User, Group, and Permission models for CREATESONLINE applications.
"""
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timedelta
import hashlib
import secrets
import hmac
from base64 import b64encode, b64decode
from typing import Optional, List
import re

# Create base class for CREATESONLINE models
Base = declarative_base()

# Pure Python password hashing functions
def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """
    Hash password using PBKDF2 with SHA-256 (pure Python implementation)
    
    Args:
        password: Plain text password
        salt: Optional salt bytes, generated if not provided
        
    Returns:
        Hashed password string in format: pbkdf2_sha256$iterations$salt$hash
    """
    if salt is None:
        salt = secrets.token_bytes(32)
    
    iterations = 100000  # OWASP recommended minimum
    
    # Use PBKDF2 with SHA-256
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    
    # Encode salt and key as base64
    salt_b64 = b64encode(salt).decode('ascii')
    key_b64 = b64encode(key).decode('ascii')
    
    return f"pbkdf2_sha256${iterations}${salt_b64}${key_b64}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password from database
        
    Returns:
        True if password matches
    """
    try:
        # Parse hash format: pbkdf2_sha256$iterations$salt$hash
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        
        iterations = int(parts[1])
        salt = b64decode(parts[2].encode('ascii'))
        stored_key = b64decode(parts[3].encode('ascii'))
        
        # Hash the provided password with same salt and iterations
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(stored_key, new_key)
        
    except (ValueError, TypeError, IndexError):
        return False

# Many-to-many association tables
user_groups = Table(
    'createsonline_user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('createsonline_users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('createsonline_groups.id'), primary_key=True)
)

user_permissions = Table(
    'createsonline_user_permissions', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('createsonline_users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('createsonline_permissions.id'), primary_key=True)
)

group_permissions = Table(
    'createsonline_group_permissions',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('createsonline_groups.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('createsonline_permissions.id'), primary_key=True)
)

class User(Base):
    """
    CREATESONLINE User Model
    
    Core user model for authentication and authorization.
    Provides all essential user management features.
    """
    __tablename__ = "createsonline_users"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    
    # Authentication
    password_hash = Column(String(128), nullable=False)
    
    # Permissions and status
    is_active = Column(Boolean, default=True, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    date_joined = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Profile information
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    password_reset_token = Column(String(100), nullable=True)
    email_verification_token = Column(String(100), nullable=True)
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    groups = relationship(
        "Group",
        secondary=user_groups,
        back_populates="users"
    )
    
    user_permissions = relationship(
        "Permission",
        secondary=user_permissions,
        back_populates="users"
    )
    
    @validates('username')
    def validate_username(self, key, username):
        """Validate username format"""
        if not username:
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return username
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if not email:
            raise ValueError("Email is required")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    def set_password(self, password: str) -> None:
        """
        Set user password with hashing
        
        Args:
            password: Plain text password
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        self.password_hash = hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify user password
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password is correct
        """
        return verify_password(password, self.password_hash)
    
    def check_password(self, password: str) -> bool:
        """Alias for verify_password"""
        return self.verify_password(password)
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (always True for valid user objects)"""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (always False for user objects)"""
        return False
    
    def get_all_permissions(self) -> List[str]:
        """
        Get all permissions for this user (direct + group permissions)
        
        Returns:
            List of permission codenames
        """
        permissions = set()
        
        # Add direct permissions
        for perm in self.user_permissions:
            permissions.add(f"{perm.content_type}.{perm.codename}")
        
        # Add group permissions
        for group in self.groups:
            for perm in group.permissions:
                permissions.add(f"{perm.content_type}.{perm.codename}")
        
        return list(permissions)
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            permission: Permission string in format "app.codename"
            
        Returns:
            True if user has permission
        """
        if self.is_superuser:
            return True
        
        return permission in self.get_all_permissions()
    
    def has_module_permission(self, app_label: str) -> bool:
        """
        Check if user has any permission for a module/app
        
        Args:
            app_label: Application label
            
        Returns:
            True if user has any permission for the app
        """
        if self.is_superuser:
            return True
        
        permissions = self.get_all_permissions()
        return any(perm.startswith(f"{app_label}.") for perm in permissions)
    
    def generate_password_reset_token(self) -> str:
        """Generate a password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        return token
    
    def generate_email_verification_token(self) -> str:
        """Generate an email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        return token
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.account_locked_until is None:
            return False
        return datetime.utcnow() < self.account_locked_until
    
    def lock_account(self, minutes: int = 30) -> None:
        """Lock account for specified minutes"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.failed_login_attempts = 0
    
    def unlock_account(self) -> None:
        """Unlock account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
    
    def record_login_attempt(self, success: bool) -> None:
        """Record login attempt"""
        if success:
            self.failed_login_attempts = 0
            self.last_login = datetime.utcnow()
            self.unlock_account()
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.lock_account()
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def __str__(self) -> str:
        return self.username

class Group(Base):
    """
    CREATESONLINE Group Model
    
    Groups are a way to categorize users and assign permissions.
    """
    __tablename__ = "createsonline_groups"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship(
        "User",
        secondary=user_groups,
        back_populates="groups"
    )
    
    permissions = relationship(
        "Permission",
        secondary=group_permissions,
        back_populates="groups"
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate group name"""
        if not name:
            raise ValueError("Group name is required")
        if len(name) < 2:
            raise ValueError("Group name must be at least 2 characters")
        return name
    
    def add_permission(self, permission: 'Permission') -> None:
        """Add permission to group"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: 'Permission') -> None:
        """Remove permission from group"""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission_codename: str) -> bool:
        """Check if group has specific permission"""
        return any(
            perm.codename == permission_codename 
            for perm in self.permissions
        )
    
    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name='{self.name}')>"
    
    def __str__(self) -> str:
        return self.name

class Permission(Base):
    """
    CREATESONLINE Permission Model
    
    Permissions define what actions users can perform.
    """
    __tablename__ = "createsonline_permissions"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Human-readable name
    codename = Column(String(100), nullable=False, index=True)  # Machine-readable code
    content_type = Column(String(100), nullable=False, index=True)  # App/model name
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship(
        "User",
        secondary=user_permissions,
        back_populates="user_permissions"
    )
    
    groups = relationship(
        "Group",
        secondary=group_permissions,
        back_populates="permissions"
    )
    
    # Unique constraint on codename + content_type
    __table_args__ = (
        sa.UniqueConstraint('codename', 'content_type', name='unique_permission'),
    )
    
    @validates('codename')
    def validate_codename(self, key, codename):
        """Validate permission codename"""
        if not codename:
            raise ValueError("Permission codename is required")
        if not re.match(r'^[a-z_]+$', codename):
            raise ValueError("Codename can only contain lowercase letters and underscores")
        return codename
    
    @validates('content_type')
    def validate_content_type(self, key, content_type):
        """Validate content type"""
        if not content_type:
            raise ValueError("Content type is required")
        return content_type
    
    @property
    def natural_key(self) -> str:
        """Get natural key for permission"""
        return f"{self.content_type}.{self.codename}"
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}', codename='{self.codename}')>"
    
    def __str__(self) -> str:
        return f"{self.content_type} | {self.name}"

# Helper functions for creating default permissions
def create_default_permissions() -> List[Permission]:
    """Create default CREATESONLINE permissions"""
    default_permissions = [
        # User management
        Permission(
            name="Can add user",
            codename="add_user", 
            content_type="auth"
        ),
        Permission(
            name="Can change user",
            codename="change_user",
            content_type="auth"
        ),
        Permission(
            name="Can delete user",
            codename="delete_user",
            content_type="auth"
        ),
        Permission(
            name="Can view user",
            codename="view_user",
            content_type="auth"
        ),
        
        # Group management
        Permission(
            name="Can add group",
            codename="add_group",
            content_type="auth"
        ),
        Permission(
            name="Can change group", 
            codename="change_group",
            content_type="auth"
        ),
        Permission(
            name="Can delete group",
            codename="delete_group",
            content_type="auth"
        ),
        Permission(
            name="Can view group",
            codename="view_group",
            content_type="auth"
        ),
        
        # Admin access
        Permission(
            name="Can access admin",
            codename="access_admin",
            content_type="admin"
        ),
        Permission(
            name="Can view admin dashboard",
            codename="view_dashboard",
            content_type="admin"
        ),
        
        # AI features
        Permission(
            name="Can use AI features",
            codename="use_ai",
            content_type="ai"
        ),
        Permission(
            name="Can manage AI models",
            codename="manage_ai_models",
            content_type="ai"
        ),
    ]
    
    return default_permissions

def create_superuser(
    username: str,
    email: str, 
    password: str,
    first_name: str = "",
    last_name: str = ""
) -> User:
    """
    Create a CREATESONLINE superuser
    
    Args:
        username: Username for superuser
        email: Email for superuser
        password: Password for superuser
        first_name: Optional first name
        last_name: Optional last name
        
    Returns:
        Created User instance
    """
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        email_verified=True
    )
    user.set_password(password)
    
    return user