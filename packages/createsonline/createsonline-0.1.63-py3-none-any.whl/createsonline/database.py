# createsonline/database.py
"""
CREATESONLINE Database Connection Module

Provides database connectivity for SQLite (built-in) and PostgreSQL (optional).
Core functionality has zero external dependencies.

Optional Dependencies:
- python-dotenv: For .env file support (pip install python-dotenv)
- psycopg2: For PostgreSQL support (pip install psycopg2-binary)

Without these, the module falls back to:
- System environment variables only (no .env)
- SQLite-only database support
"""

import os
import json
import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

# Setup logging
logger = logging.getLogger("createsonline.database")

# Try to load dotenv if available (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.debug("dotenv not available - using system environment only")


class ParamStyle(Enum):
    """SQL parameter styles for different databases"""
    SQLITE = "?"
    POSTGRESQL = "%s"


class DatabaseConnection:
    """
    Pure Python database connection handler for CREATESONLINE.
    Supports SQLite (built-in) and PostgreSQL (via optional psycopg2).
    """
    
    def __init__(
        self, 
        database_url: Optional[str] = None,
        auto_create_tables: bool = True
    ):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///createsonline.db')
        self.connection = None
        self.db_type = self._detect_db_type()
        self.param_style = ParamStyle.SQLITE if self.db_type == 'sqlite' else ParamStyle.POSTGRESQL
        self.auto_create_tables = auto_create_tables
        
        # Initialize connection
        self._connect()
        
        if self.auto_create_tables:
            self._create_default_tables()
    
    def _detect_db_type(self) -> str:
        """Detect database type from URL"""
        if self.database_url.startswith('postgresql://'):
            return 'postgresql'
        elif self.database_url.startswith('sqlite://'):
            return 'sqlite'
        else:
            return 'sqlite'  # Default to SQLite
    
    def _get_placeholder(self) -> str:
        """Get appropriate SQL placeholder for database type"""
        return self.param_style.value
    
    def _validate_identifier(self, identifier: str) -> str:
        """Validate and sanitize SQL identifiers (table/column names)"""
        # Reserved SQL keywords to prevent injection and conflicts
        reserved_words = {
            'select', 'from', 'where', 'insert', 'update', 'delete', 'drop', 'create',
            'table', 'database', 'index', 'alter', 'grant', 'revoke', 'commit', 'rollback',
            'transaction', 'begin', 'end', 'union', 'join', 'inner', 'outer', 'left', 'right',
            'group', 'order', 'having', 'distinct', 'count', 'sum', 'avg', 'max', 'min',
            'and', 'or', 'not', 'null', 'true', 'false', 'is', 'like', 'in', 'exists'
        }
        
        # Allow only alphanumeric characters, underscores, and dots
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)?$', identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier}")
        
        # Check against reserved words (case-insensitive)
        if identifier.lower() in reserved_words:
            raise ValueError(f"SQL identifier '{identifier}' is a reserved word")
        
        return identifier
    
    def _connect(self):
        """Establish database connection"""
        if self.db_type == 'sqlite':
            # Extract SQLite path from URL
            db_path = self.database_url.replace('sqlite:///', '').replace('sqlite://', '')
            if db_path == ':memory:':
                self.connection = sqlite3.connect(':memory:', check_same_thread=False)
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
                self.connection = sqlite3.connect(db_path, check_same_thread=False)
            
            # Enable row factory for dict-like access
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {db_path}")
            
        elif self.db_type == 'postgresql':
            try:
                import psycopg2
                import psycopg2.extras
                self.connection = psycopg2.connect(
                    self.database_url,
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
                logger.info("Connected to PostgreSQL database")
            except ImportError:
                logger.warning("PostgreSQL support requires psycopg2. Falling back to SQLite.")
                self.database_url = 'sqlite:///createsonline.db'
                self.db_type = 'sqlite'
                self.param_style = ParamStyle.SQLITE
                return self._connect()
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                raise
    
    def _create_default_tables(self):
        """Create default CREATESONLINE framework tables"""
        # Consolidated user table (removing duplicate users table)
        user_table_sql = '''
            CREATE TABLE IF NOT EXISTS createsonline_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                password_hash VARCHAR(128) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_staff BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                profile_picture TEXT,
                bio TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP,
                password_reset_token VARCHAR(128),
                email_verification_token VARCHAR(128),
                email_verified BOOLEAN DEFAULT FALSE
            )
        ''' if self.db_type == 'postgresql' else '''
            CREATE TABLE IF NOT EXISTS createsonline_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                password_hash VARCHAR(128) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_staff BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                profile_picture TEXT,
                bio TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP,
                password_reset_token VARCHAR(128),
                email_verification_token VARCHAR(128),
                email_verified BOOLEAN DEFAULT FALSE
            )
        '''
        
        tables = {
            'createsonline_users': user_table_sql,
            'ai_conversations': f'''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id {'SERIAL' if self.db_type == 'postgresql' else 'INTEGER'} PRIMARY KEY{' AUTOINCREMENT' if self.db_type == 'sqlite' else ''},
                    user_id INTEGER REFERENCES createsonline_users(id),
                    conversation_data TEXT NOT NULL,
                    ai_model VARCHAR(50) DEFAULT 'createsonline-internal',
                    tokens_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'app_settings': f'''
                CREATE TABLE IF NOT EXISTS app_settings (
                    id {'SERIAL' if self.db_type == 'postgresql' else 'INTEGER'} PRIMARY KEY{' AUTOINCREMENT' if self.db_type == 'sqlite' else ''},
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    description TEXT,
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'admin_sessions': f'''
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    id {'SERIAL' if self.db_type == 'postgresql' else 'INTEGER'} PRIMARY KEY{' AUTOINCREMENT' if self.db_type == 'sqlite' else ''},
                    user_id INTEGER REFERENCES createsonline_users(id),
                    session_token VARCHAR(128) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
        
        for table_name, sql in tables.items():
            try:
                cursor = self.connection.cursor()
                cursor.execute(sql)
                self.connection.commit()
                logger.info(f"Table '{table_name}' ready")
            except Exception as e:
                logger.error(f"Error creating table '{table_name}': {e}")
                raise
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                if self.db_type == 'sqlite':
                    return [dict(row) for row in cursor.fetchall()]
                else:
                    return cursor.fetchall()
            else:
                self.connection.commit()
                return [{"affected_rows": cursor.rowcount}]
                
        except Exception as e:
            logger.exception(f"Database query failed: {query[:100]}...")
            self.connection.rollback()
            raise  # Re-raise the exception instead of swallowing it
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert data into table and return ID"""
        safe_table = self._validate_identifier(table)
        columns = ', '.join([self._validate_identifier(k) for k in data.keys()])
        placeholders = ', '.join([self._get_placeholder()] * len(data))
        
        if self.db_type == 'postgresql':
            # PostgreSQL needs RETURNING for ID
            query = f"INSERT INTO {safe_table} ({columns}) VALUES ({placeholders}) RETURNING id"
        else:
            query = f"INSERT INTO {safe_table} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            
            # Return last inserted ID
            if self.db_type == 'sqlite':
                row_id = cursor.lastrowid
                self.connection.commit()
                return row_id
            else:
                # PostgreSQL with RETURNING
                row_id = cursor.fetchone()['id'] if cursor.rowcount > 0 else None
                self.connection.commit()
                return row_id
                
        except Exception as e:
            logger.error(f"Insert error: {e}")
            self.connection.rollback()
            return None
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update data in table"""
        safe_table = self._validate_identifier(table)
        placeholder = self._get_placeholder()
        set_clause = ', '.join([f"{self._validate_identifier(k)} = {placeholder}" for k in data.keys()])
        where_clause = ' AND '.join([f"{self._validate_identifier(k)} = {placeholder}" for k in where.keys()])
        
        query = f"UPDATE {safe_table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(where.values())
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Update error: {e}")
            self.connection.rollback()
            return 0
    
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete data from table"""
        safe_table = self._validate_identifier(table)
        placeholder = self._get_placeholder()
        where_clause = ' AND '.join([f"{self._validate_identifier(k)} = {placeholder}" for k in where.keys()])
        query = f"DELETE FROM {safe_table} WHERE {where_clause}"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(where.values()))
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Delete error: {e}")
            self.connection.rollback()
            return 0
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username from consolidated users table"""
        placeholder = self._get_placeholder()
        result = self.execute(f"SELECT * FROM createsonline_users WHERE username = {placeholder}", (username,))
        return result[0] if result else None
    
    def create_admin_user(self, username: str, email: str, password: str) -> Optional[int]:
        """Create admin user with hashed password"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return self.insert('createsonline_users', {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'email_verified': True
        })
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """Create admin session and return token"""
        import secrets
        session_token = secrets.token_urlsafe(32)
        
        # Session expires in 24 hours
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(hours=24)
        
        self.insert('admin_sessions', {
            'user_id': user_id,
            'session_token': session_token,
            'expires_at': expires_at.isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent
        })
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return user data"""
        placeholder = self._get_placeholder()
        query = f'''
            SELECT u.*, s.expires_at 
            FROM createsonline_users u 
            JOIN admin_sessions s ON u.id = s.user_id 
            WHERE s.session_token = {placeholder} AND s.expires_at > CURRENT_TIMESTAMP
        '''
        result = self.execute(query, (session_token,))
        return result[0] if result else None
    
    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        placeholder = self._get_placeholder()
        result = self.execute(f"SELECT value FROM app_settings WHERE key = {placeholder}", (key,))
        if result:
            try:
                return json.loads(result[0]['value'])
            except:
                return result[0]['value']
        return default
    
    def set_app_setting(self, key: str, value: Any, description: str = None):
        """Set application setting"""
        # Check if setting exists
        placeholder = self._get_placeholder()
        existing = self.execute(f"SELECT id FROM app_settings WHERE key = {placeholder}", (key,))
        
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        if existing:
            self.update('app_settings', 
                       {'value': value_str, 'updated_at': datetime.now().isoformat()}, 
                       {'key': key})
        else:
            self.insert('app_settings', {
                'key': key,
                'value': value_str,
                'description': description or f"Setting for {key}"
            })
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash (uses consolidated SecurityUtils)"""
        try:
            from .utils import SecurityUtils
            return SecurityUtils.verify_password(password, password_hash)
        except ImportError:
            # Fallback to simple verification for standalone use
            import hashlib
            import secrets
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            return secrets.compare_digest(computed_hash, password_hash)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global database instance
_db_instance = None

def get_database() -> DatabaseConnection:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance

def init_database(database_url: str = None) -> DatabaseConnection:
    """Initialize database with custom URL"""
    global _db_instance
    _db_instance = DatabaseConnection(database_url)
    return _db_instance