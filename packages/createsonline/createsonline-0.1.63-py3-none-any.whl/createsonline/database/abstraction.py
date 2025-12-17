"""
CREATESONLINE Database Abstraction Layer

Pure Python database abstraction that wraps SQLAlchemy with a clean API.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union, Type
from contextlib import contextmanager
from urllib.parse import quote_plus

# Setup logger
logger = logging.getLogger(__name__)


def build_database_url(
    driver: str,
    username: str,
    password: str,
    host: str,
    port: int,
    database: str
) -> str:
    """
    Build a database URL with proper password encoding.
    
    Args:
        driver: Database driver (postgresql, mysql, sqlite, etc.)
        username: Database username
        password: Database password (will be URL-encoded)
        host: Database host
        port: Database port
        database: Database name
    
    Returns:
        Properly formatted database URL
    
    Example:
        >>> build_database_url('postgresql', 'user', '@pass', 'localhost', 5432, 'mydb')
        'postgresql://user:%40pass@localhost:5432/mydb'
    """
    encoded_password = quote_plus(password)
    return f"{driver}://{username}:{encoded_password}@{host}:{port}/{database}"


class DatabaseError(Exception):
    """Custom database error for better error handling"""
    pass

# Try to import SQLAlchemy, fallback to internal implementation if not available
try:
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey
    from sqlalchemy.orm import sessionmaker, declarative_base, Session
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Create placeholder classes
    class Session: pass
    class SQLAlchemyError(Exception): pass


class Database:
    """
    CREATESONLINE Database Abstraction
    
    Provides a clean, simple API that wraps SQLAlchemy complexity.
    Falls back to internal database implementation if SQLAlchemy is not available.
    """
    
    _instance = None  # Singleton instance
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10
    ):
        """
        Initialize database
        
        Args:
            database_url: Database connection URL
            echo: Enable SQL query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///createsonline.db')
        self.echo = echo or os.getenv('DATABASE_ECHO', 'false').lower() == 'true'
        
        if SQLALCHEMY_AVAILABLE:
            self._setup_sqlalchemy(pool_size, max_overflow)
        else:
            self._setup_fallback()
    
    @classmethod
    def get_instance(cls) -> 'Database':
        """Get singleton database instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def set_instance(cls, instance: 'Database'):
        """Set singleton database instance"""
        cls._instance = instance
    
    def _setup_sqlalchemy(self, pool_size: int, max_overflow: int):
        """Setup SQLAlchemy engine and session"""
        try:
            # Configure engine based on database type
            if self.database_url.startswith('sqlite'):
                # SQLite configuration
                engine_kwargs = {
                    'echo': self.echo,
                    'poolclass': StaticPool,
                    'connect_args': {'check_same_thread': False}
                }
            else:
                # PostgreSQL/MySQL configuration
                engine_kwargs = {
                    'echo': self.echo,
                    'pool_size': pool_size,
                    'max_overflow': max_overflow
                }
            
            # Check for async driver
            is_async = '+asyncpg' in self.database_url or '+aiosqlite' in self.database_url or '+aiomysql' in self.database_url
            
            if is_async:
                try:
                    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
                    from sqlalchemy.orm import sessionmaker as async_sessionmaker
                    
                    self.engine = create_async_engine(self.database_url, **engine_kwargs)
                    self.AsyncSessionLocal = async_sessionmaker(
                        self.engine, class_=AsyncSession, expire_on_commit=False
                    )
                    self.mode = 'sqlalchemy_async'
                    logger.info(" CREATESONLINE: Database initialized with Async SQLAlchemy")
                except ImportError:
                    logger.warning("Async SQLAlchemy dependencies not found. Falling back to sync.")
                    # Strip async driver for fallback if possible, or let it fail
                    self.engine = create_engine(self.database_url, **engine_kwargs)
                    self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                    self.mode = 'sqlalchemy'
            else:
                self.engine = create_engine(self.database_url, **engine_kwargs)
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                self.mode = 'sqlalchemy'

            self.metadata = MetaData()
            
            # Create declarative base
            self.Base = declarative_base(metadata=self.metadata)
            
            if self.mode == 'sqlalchemy':
                logger.info(" CREATESONLINE: Database initialized with SQLAlchemy (Sync)")
            
        except SQLAlchemyError as e:
            logger.warning(f"SQLAlchemy error: {e}")
            self._setup_fallback()
    
    def _setup_fallback(self):
        """Setup fallback database implementation"""
        # Import the existing database implementation
        from .. import database as legacy_db
        
        self.legacy_db = legacy_db.DatabaseConnection(self.database_url)
        self.mode = 'legacy'
        logger.info(" CREATESONLINE: Database initialized with legacy implementation")
    
    def get_session(self) -> Union[Session, 'LegacySession']:
        """Get database session"""
        if self.mode == 'sqlalchemy':
            return self.SessionLocal()
        elif self.mode == 'sqlalchemy_async':
            # For async, we return the async session factory or session
            # Note: This might break sync code expecting a sync session
            return self.AsyncSessionLocal()
        else:
            return LegacySession(self.legacy_db)
    
    @contextmanager
    def session(self):
        """Context manager for database sessions (Sync)"""
        if self.mode == 'sqlalchemy_async':
            raise RuntimeError("Cannot use sync session() context manager with Async Database. Use async_session() instead.")
            
        session = self.get_session()
        try:
            yield session
            if hasattr(session, 'commit'):
                session.commit()
        except Exception as e:
            if hasattr(session, 'rollback'):
                session.rollback()
            raise
        finally:
            if hasattr(session, 'close'):
                session.close()

    @contextmanager
    def session_scope(self):
        """Alias for session()"""
        with self.session() as s:
            yield s

    def async_session(self):
        """Context manager for async database sessions"""
        if self.mode != 'sqlalchemy_async':
             # Fallback to sync session wrapped in something? No, just raise error or return sync session if compatible?
             # For now, let's assume user knows what they are doing.
             raise RuntimeError("Database is not in async mode. Use session() instead.")
        
        return self.AsyncSessionLocal()
    
    def execute_raw(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute raw SQL query with proper error handling"""
        try:
            if self.mode == 'sqlalchemy':
                with self.session_scope() as session:
                    result = session.execute(query, params)
                    if query.strip().upper().startswith('SELECT'):
                        return [dict(row) for row in result.fetchall()]
                    else:
                        return [{'affected_rows': result.rowcount}]
            else:
                return self.legacy_db.execute(query, params)
                
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {query[:100]}... Error: {e}")
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error executing query: {query[:100]}... Error: {e}")
            raise DatabaseError(f"Unexpected database error: {str(e)}") from e
    
    def create_tables(self, models: List[Type[Any]] = None):
        """Create database tables"""
        if self.mode == 'sqlalchemy':
            if models:
                # Create tables for specific models
                for model in models:
                    model.metadata.create_all(bind=self.engine)
            else:
                # Create all tables
                self.Base.metadata.create_all(bind=self.engine)
        else:
            # Legacy implementation already creates tables
            pass
    
    def drop_tables(self, models: List[Type[Any]] = None):
        """Drop database tables"""
        if self.mode == 'sqlalchemy':
            if models:
                for model in models:
                    model.metadata.drop_all(bind=self.engine)
            else:
                self.Base.metadata.drop_all(bind=self.engine)
        else:
            # For legacy, would need to implement table dropping
            logger.warning("Table dropping not implemented in legacy mode")
    
    def get_table_names(self) -> List[str]:
        """Get list of table names"""
        if self.mode == 'sqlalchemy':
            self.metadata.reflect(bind=self.engine)
            return list(self.metadata.tables.keys())
        else:
            # For SQLite legacy implementation
            result = self.legacy_db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            return [row['name'] for row in result]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        return table_name in self.get_table_names()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        return {
            'database_url': self.database_url,
            'mode': self.mode,
            'sqlalchemy_available': SQLALCHEMY_AVAILABLE,
            'tables': self.get_table_names()
        }


class Connection:
    """Database connection wrapper"""
    
    def __init__(self, database: Database):
        self.database = database
        self.session = database.get_session()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQL query"""
        return self.database.execute_raw(query, params)
    
    def commit(self):
        """Commit transaction"""
        if hasattr(self.session, 'commit'):
            self.session.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if hasattr(self.session, 'rollback'):
            self.session.rollback()
    
    def close(self):
        """Close connection"""
        if hasattr(self.session, 'close'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class Transaction:
    """Database transaction wrapper"""
    
    def __init__(self, database: Database):
        self.database = database
        self.session = None
    
    def __enter__(self):
        self.session = self.database.get_session()
        if hasattr(self.session, 'begin'):
            self.transaction = self.session.begin()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if hasattr(self.session, 'rollback'):
                self.session.rollback()
        else:
            if hasattr(self.session, 'commit'):
                self.session.commit()
        
        if hasattr(self.session, 'close'):
            self.session.close()


class LegacySession:
    """Wrapper for legacy database implementation to provide session-like interface"""
    
    def __init__(self, legacy_db):
        self.legacy_db = legacy_db
        self._changes = []
        self._dirty = False
    
    def execute(self, query: str, params: tuple = ()):
        """Execute query"""
        return self.legacy_db.execute(query, params)
    
    def add(self, instance):
        """Add instance with proper change tracking"""
        self._changes.append(('add', instance))
        self._dirty = True
    
    def delete(self, instance):
        """Delete instance with proper change tracking"""
        self._changes.append(('delete', instance))
        self._dirty = True
    
    def commit(self):
        """Commit changes - flush pending operations"""
        if not self._dirty:
            return
        
        
        try:
            for operation, instance in self._changes:
                if operation == 'add':
                    self._flush_add(instance)
                elif operation == 'delete':
                    self._flush_delete(instance)
            
            self._changes.clear()
            self._dirty = False
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            raise
    
    def _flush_add(self, instance):
        """Flush add operation to database"""
        # This is a simplified implementation
        # In a real ORM, this would use the instance's metadata
        table_name = getattr(instance.__class__, '__tablename__', 'unknown')
        
        # Extract data from instance
        data = {}
        for attr_name in dir(instance):
            if not attr_name.startswith('_') and not callable(getattr(instance, attr_name)):
                value = getattr(instance, attr_name)
                if value is not None:
                    data[attr_name] = value
        
        if data:
            result = self.legacy_db.insert(table_name, data)
    
    def _flush_delete(self, instance):
        """Flush delete operation to database"""
        table_name = getattr(instance.__class__, '__tablename__', 'unknown')
        
        # Use ID if available
        if hasattr(instance, 'id') and instance.id:
            result = self.legacy_db.delete(table_name, {'id': instance.id})
    
    def rollback(self):
        """Rollback changes"""
        self._changes.clear()
        self._dirty = False
    
    def close(self):
        """Close session"""
        if self._dirty:
            logger.warning("Closing session with uncommitted changes")
        self._changes.clear()
    
    def query(self, model_class):
        """Create query (basic implementation)"""
        return LegacyQuery(self.legacy_db, model_class)


class LegacyQuery:
    """Legacy query implementation for compatibility"""
    
    def __init__(self, legacy_db, model_class):
        self.legacy_db = legacy_db
        self.model_class = model_class
        self._filters = []
        self._limit = None
        self._offset = None
        self._order_by = []
    
    def filter(self, *criteria):
        """Add filter criteria"""
        self._filters.extend(criteria)
        return self
    
    def filter_by(self, **kwargs):
        """Add filter by keyword arguments"""
        for key, value in kwargs.items():
            self._filters.append(f"{key} = ?")
        return self
    
    def limit(self, limit_value):
        """Add limit"""
        self._limit = limit_value
        return self
    
    def offset(self, offset_value):
        """Add offset"""
        self._offset = offset_value
        return self
    
    def order_by(self, *columns):
        """Add order by"""
        self._order_by.extend(columns)
        return self
    
    def first(self):
        """Get first result"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def all(self):
        """Get all results"""
        # This is a simplified implementation
        # In practice, would need to parse model class and build proper query
        table_name = getattr(self.model_class, '__tablename__', 'unknown')
        query = f"SELECT * FROM {table_name}"
        
        if self._filters:
            query += " WHERE " + " AND ".join(self._filters)
        
        if self._order_by:
            query += " ORDER BY " + ", ".join(str(col) for col in self._order_by)
        
        if self._limit:
            query += f" LIMIT {self._limit}"
        
        if self._offset:
            query += f" OFFSET {self._offset}"
        
        return self.legacy_db.execute(query)
    
    def count(self):
        """Count results"""
        table_name = getattr(self.model_class, '__tablename__', 'unknown')
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        
        if self._filters:
            query += " WHERE " + " AND ".join(self._filters)
        
        result = self.legacy_db.execute(query)
        return result[0]['count'] if result else 0
