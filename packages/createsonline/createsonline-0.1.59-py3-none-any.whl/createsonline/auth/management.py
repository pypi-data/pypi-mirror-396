# createsonline/auth/management.py
"""
CREATESONLINE User Management Commands
Provides Django-like utilities for user creation and management (Django-style interactive prompts)
"""
import getpass
import re
import sys
from typing import Optional, Tuple
from createsonline.auth.models import User, hash_password
from createsonline.database.abstraction import Database


class UserManagement:
    """User management utility class"""
    
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    MIN_PASSWORD_LENGTH = 8
    
    @staticmethod
    def create_superuser(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        interactive: bool = True
    ) -> Tuple[bool, str]:
        """
        Create a new superuser account
        
        Args:
            username: Superuser username (prompted if not provided and interactive=True)
            email: Superuser email (prompted if not provided and interactive=True)
            password: Superuser password (prompted if not provided and interactive=True)
            interactive: Whether to prompt for missing values
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            db = Database.get_instance()
            
            # Get or prompt for username
            if not username:
                if not interactive:
                    return False, "Username is required"
                username = UserManagement._prompt_username()
            
            # Check if username already exists
            # Handle both sync and async DB modes
            if db.mode == 'sqlalchemy_async':
                # Cannot run async query in sync method easily without event loop
                # For CLI tools, we might need to run this in an async wrapper or use a sync engine for CLI
                # For now, let's assume CLI uses sync engine (default)
                print("Warning: Async database mode detected in sync CLI command. This might fail.")
            
            with db.session() as session:
                existing = session.query(User).filter(User.username == username).first()
                if existing:
                    return False, f"Username '{username}' already exists"
            
            # Get or prompt for email
            if not email:
                if not interactive:
                    return False, "Email is required"
                email = UserManagement._prompt_email()
            
            # Get or prompt for password
            if not password:
                if not interactive:
                    return False, "Password is required"
                password = UserManagement._prompt_password()
            
            # Validate password
            if len(password) < UserManagement.MIN_PASSWORD_LENGTH:
                return False, f"Password must be at least {UserManagement.MIN_PASSWORD_LENGTH} characters long"
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create superuser
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            
            with db.session() as session:
                session.add(user)
                session.commit()
            
            return True, f"Superuser '{username}' created successfully!"
            
        except Exception as e:
            return False, f"Error creating superuser: {str(e)}"
    
    @staticmethod
    def _prompt_username() -> str:
        """Prompt user for username with validation"""
        while True:
            username = input("Username: ").strip()
            
            if not username:
                print("Username cannot be empty.")
                continue
            
            if len(username) < 3:
                print("Username must be at least 3 characters long.")
                continue
            
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                print("Username can only contain letters, numbers, hyphens, and underscores.")
                continue
            
            # Check if already exists
            try:
                db = Database.get_instance()
                with db.session() as session:
                    existing = session.query(User).filter(User.username == username).first()
                    if existing:
                        print(f"Username '{username}' already exists.")
                        continue
            except Exception:
                pass
            
            return username
    
    @staticmethod
    def _prompt_email() -> str:
        """Prompt user for email with validation"""
        while True:
            email = input("Email address: ").strip()
            
            if not email:
                print("Email cannot be empty.")
                continue
            
            if not re.match(UserManagement.EMAIL_REGEX, email):
                print("Enter a valid email address.")
                continue
            
            return email
    
    @staticmethod
    def _prompt_password() -> str:
        """Prompt user for password with confirmation"""
        while True:
            password = getpass.getpass("Password: ")
            
            if len(password) < UserManagement.MIN_PASSWORD_LENGTH:
                print(f"Password must be at least {UserManagement.MIN_PASSWORD_LENGTH} characters long.")
                continue
            
            # Check password strength (basic checks)
            if not any(c.isupper() for c in password):
                confirm = input("Password lacks uppercase letters. Continue anyway? [y/N]: ").strip().lower()
                if confirm != 'y':
                    continue
            
            if not any(c.isdigit() for c in password):
                confirm = input("Password lacks numeric characters. Continue anyway? [y/N]: ").strip().lower()
                if confirm != 'y':
                    continue
            
            # Confirm password
            password_confirm = getpass.getpass("Password (again): ")
            
            if password != password_confirm:
                print("Passwords do not match.")
                continue
            
            return password
    
    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        is_staff: bool = False,
        is_superuser: bool = False,
        is_active: bool = True
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Create a regular user
        
        Args:
            username: User username
            email: User email
            password: User password
            is_staff: Whether user is staff
            is_superuser: Whether user is superuser
            is_active: Whether user is active
            
        Returns:
            Tuple of (success: bool, message: str, user: Optional[User])
        """
        try:
            db = Database.get_instance()
            
            # Validate email
            if not re.match(UserManagement.EMAIL_REGEX, email):
                return False, "Invalid email format", None
            
            # Check if username exists
            with db.session() as session:
                existing = session.query(User).filter(User.username == username).first()
                if existing:
                    return False, f"Username '{username}' already exists", None
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create user
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=is_active
            )
            
            with db.session() as session:
                session.add(user)
                session.commit()
            
            return True, f"User '{username}' created successfully!", user
            
        except Exception as e:
            return False, f"Error creating user: {str(e)}", None


__all__ = ['UserManagement']
