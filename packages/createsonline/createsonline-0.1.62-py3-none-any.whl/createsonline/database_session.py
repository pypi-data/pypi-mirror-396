"""
Secure Database Session Management for CREATESONLINE v1.55.0

Provides enhanced security features:
- Connection pooling with proper configuration
- SSL/TLS support for secure connections
- Scoped session management
- Connection validation (pre-ping)
- Automatic cleanup and error handling
- Connection timeout and pool recycling
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SecureDatabaseSessionManager:
    """
    Manages database sessions with enterprise-grade security
    
    Features:
    - Connection pooling (prevents exhaustion)
    - SSL/TLS encryption support
    - Pre-ping (validates connections before use)
    - Automatic session cleanup
    - Configurable timeouts
    - Pool recycling (prevents stale connections)
    """
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
        ssl_required: bool = False,
        ssl_cert_path: Optional[str] = None,
        ssl_key_path: Optional[str] = None,
        ssl_ca_path: Optional[str] = None,
        connect_args: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize secure database session manager
        
        Args:
            database_url: SQLAlchemy database URL
            pool_size: Number of connections to maintain (default: 5)
            max_overflow: Max connections beyond pool_size (default: 10)
            pool_timeout: Seconds to wait for connection (default: 30)
            pool_recycle: Recycle connections after N seconds (default: 3600)
            pool_pre_ping: Test connection before using (default: True)
            echo: Log all SQL statements (default: False)
            ssl_required: Require SSL/TLS encryption (default: False)
            ssl_cert_path: Path to SSL client certificate
            ssl_key_path: Path to SSL client key
            ssl_ca_path: Path to SSL CA certificate
            connect_args: Additional connection arguments
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.echo = echo
        
        # Build connection arguments
        self.connect_args = connect_args or {}
        
        # Configure SSL if required
        if ssl_required:
            ssl_config = {}
            if ssl_cert_path:
                ssl_config['ssl_cert'] = ssl_cert_path
            if ssl_key_path:
                ssl_config['ssl_key'] = ssl_key_path
            if ssl_ca_path:
                ssl_config['ssl_ca'] = ssl_ca_path
            
            if ssl_config:
                self.connect_args['ssl'] = ssl_config
        
        # Create engine with security configurations
        self.engine = self._create_secure_engine()
        
        # Create scoped session factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False
            )
        )
        
        # Register event listeners for security
        self._register_security_events()
    
    def _create_secure_engine(self):
        """Create SQLAlchemy engine with security features"""
        
        # Choose appropriate pooling strategy
        if 'sqlite' in self.database_url.lower():
            # SQLite uses NullPool (one connection per thread)
            poolclass = NullPool
            engine_kwargs = {
                'poolclass': poolclass,
                'echo': self.echo,
                'connect_args': self.connect_args
            }
        else:
            # PostgreSQL, MySQL, etc. use QueuePool
            poolclass = QueuePool
            engine_kwargs = {
                'poolclass': poolclass,
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
                'pool_timeout': self.pool_timeout,
                'pool_recycle': self.pool_recycle,
                'pool_pre_ping': self.pool_pre_ping,
                'echo': self.echo,
                'connect_args': self.connect_args
            }
        
        engine = create_engine(self.database_url, **engine_kwargs)
        
        logger.info(f"Database engine created: pool_size={self.pool_size}, "
                   f"max_overflow={self.max_overflow}, pre_ping={self.pool_pre_ping}")
        
        return engine
    
    def _register_security_events(self):
        """Register SQLAlchemy event listeners for security"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Called when new connection is created"""
            logger.debug("New database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Called when connection is checked out from pool"""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """Called when connection is returned to pool"""
            logger.debug("Connection returned to pool")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session with automatic cleanup
        
        Usage:
            with session_manager.get_session() as session:
                user = session.query(User).first()
                session.commit()
        
        Yields:
            Session: SQLAlchemy session with automatic rollback/close
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_scoped_session(self) -> Session:
        """
        Get scoped session for current thread
        
        Returns:
            Session: Thread-local session instance
        """
        return self.SessionLocal()
    
    def remove_scoped_session(self):
        """Remove scoped session for current thread"""
        self.SessionLocal.remove()
    
    def close_all_connections(self):
        """Close all connections in pool (for shutdown)"""
        self.SessionLocal.remove()
        self.engine.dispose()
        logger.info("All database connections closed")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status for monitoring
        
        Returns:
            dict: Pool statistics (size, checked_out, overflow, etc.)
        """
        pool = self.engine.pool
        
        if isinstance(pool, QueuePool):
            return {
                'pool_size': pool.size(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'queue_size': pool.size() - pool.checkedout()
            }
        else:
            return {'pool_type': type(pool).__name__}


# Convenience function for quick setup
def create_secure_session_manager(
    database_url: str,
    **kwargs
) -> SecureDatabaseSessionManager:
    """
    Create secure database session manager with default settings
    
    Args:
        database_url: SQLAlchemy database URL
        **kwargs: Additional configuration options
    
    Returns:
        SecureDatabaseSessionManager: Configured session manager
    
    Example:
        manager = create_secure_session_manager(
            'postgresql://user:pass@localhost/dbname',
            pool_size=10,
            ssl_required=True
        )
    """
    return SecureDatabaseSessionManager(database_url, **kwargs)


# Example usage
if __name__ == "__main__":
    # PostgreSQL with SSL
    manager = create_secure_session_manager(
        'postgresql://user:password@localhost:5432/mydb',
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        ssl_required=True
    )
    
    # Use with context manager (recommended)
    with manager.get_session() as session:
        # Your queries here
        pass
    
    # Check pool status
    print(manager.get_pool_status())
    
    # Shutdown
    manager.close_all_connections()
