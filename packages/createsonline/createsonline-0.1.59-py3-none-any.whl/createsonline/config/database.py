# createsonline/config/database.py
"""
CREATESONLINE Database Configuration
Wrapper around the database abstraction layer for configuration management.
Supports SQLite, PostgreSQL, and MySQL database connections.

The actual database connection is handled by createsonline.database.abstraction.Database
"""
import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class DatabaseConfig:
    """Database configuration manager"""
    
    # Supported database engines
    SUPPORTED_ENGINES = ['sqlite', 'postgresql', 'mysql', 'mariadb']
    
    @staticmethod
    def get_database_url() -> str:
        """
        Get database URL from environment variable or config
        
        This integrates with createsonline.database.abstraction.Database which
        uses the same DATABASE_URL environment variable.
        
        Environment variable priority:
        1. DATABASE_URL - Complete database URL (used by Database class)
        2. DATABASE_ENGINE - Type of database (sqlite, postgresql, mysql)
        3. Uses SQLite as default
        
        Supported formats:
        - sqlite:///./db.sqlite3
        - postgresql://user:password@localhost:5432/dbname
        - postgresql+psycopg2://user:password@localhost:5432/dbname
        - mysql+pymysql://user:password@localhost:3306/dbname
        - mysql://user:password@localhost:3306/dbname
        
        Returns:
            Database URL string
        """
        # Check for complete DATABASE_URL first (same as Database.abstraction)
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        
        # Build from individual components
        engine = os.getenv('DATABASE_ENGINE', 'sqlite').lower()
        
        if engine == 'sqlite':
            db_path = os.getenv('DATABASE_PATH', './db.sqlite3')
            return f'sqlite:///{db_path}'
        
        elif engine in ['postgresql', 'postgres']:
            return DatabaseConfig._build_postgresql_url()
        
        elif engine in ['mysql', 'mariadb']:
            return DatabaseConfig._build_mysql_url()
        
        else:
            raise ValueError(f"Unsupported database engine: {engine}")
    
    @staticmethod
    def _build_postgresql_url() -> str:
        """Build PostgreSQL connection URL from environment variables"""
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'postgres')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'createsonline')
        
        # Use psycopg2 driver (can be overridden)
        driver = os.getenv('DB_DRIVER', 'psycopg2')
        
        if password:
            return f'postgresql+{driver}://{user}:{password}@{host}:{port}/{database}'
        else:
            return f'postgresql+{driver}://{user}@{host}:{port}/{database}'
    
    @staticmethod
    def _build_mysql_url() -> str:
        """Build MySQL/MariaDB connection URL from environment variables"""
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '3306')
        database = os.getenv('DB_NAME', 'createsonline')
        
        # Default to pymysql driver for compatibility
        driver = os.getenv('DB_DRIVER', 'pymysql')
        
        if password:
            return f'mysql+{driver}://{user}:{password}@{host}:{port}/{database}'
        else:
            return f'mysql+{driver}://{user}@{host}:{port}/{database}'
    
    @staticmethod
    def get_connection_info() -> Dict[str, Any]:
        """
        Get parsed connection information
        
        Returns:
            Dictionary with connection details
        """
        url = DatabaseConfig.get_database_url()
        parsed = urlparse(url)
        
        return {
            'engine': parsed.scheme.split('+')[0],
            'driver': parsed.scheme.split('+')[1] if '+' in parsed.scheme else None,
            'user': parsed.username,
            'password': parsed.password,
            'host': parsed.hostname,
            'port': parsed.port,
            'database': parsed.path.lstrip('/'),
            'url': url
        }
    
    @staticmethod
    def validate_connection() -> bool:
        """
        Validate database connection without running full migrations
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            from createsonline.database.abstraction import Database
            db = Database.get_instance()
            # Try to create a session and execute a simple query
            with db.session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    @staticmethod
    def get_environment_template() -> str:
        """
        Get template for .env file with database configuration examples
        
        Returns:
            String with .env template
        """
        return """# CREATESONLINE Database Configuration

# Option 1: Complete Database URL (uncomment and use one)
# DATABASE_URL=sqlite:///./db.sqlite3
# DATABASE_URL=postgresql://user:password@localhost:5432/createsonline
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/createsonline

# Option 2: Individual Components (used if DATABASE_URL not set)
# Database Engine: sqlite, postgresql, mysql, mariadb
DATABASE_ENGINE=sqlite

# SQLite Configuration (used when DATABASE_ENGINE=sqlite)
DATABASE_PATH=./db.sqlite3

# PostgreSQL Configuration (used when DATABASE_ENGINE=postgresql)
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=createsonline
# DB_DRIVER=psycopg2

# MySQL/MariaDB Configuration (used when DATABASE_ENGINE=mysql)
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=createsonline
# DB_DRIVER=pymysql
"""


__all__ = ['DatabaseConfig']
