"""
CREATESONLINE Database Abstraction Layer

Pure Python database abstraction with zero external dependencies (except SQLAlchemy).
Clean API that hides SQLAlchemy complexity while providing AI-native features.
"""

from .abstraction import Database, Connection, Transaction, build_database_url
from .models import CreatesonlineModel, QueryBuilder
from .fields import (
    CreatesonlineField, StringField, IntegerField, FloatField,
    BooleanField, DateTimeField, TextField, JSONField,
    EmbeddingField, SlugField, EmailField, URLField
)
from .migrations import MigrationManager, Migration

__all__ = [
    # Core database
    'Database',
    'Connection', 
    'Transaction',
    'build_database_url',
    
    # Models
    'CreatesonlineModel',
    'QueryBuilder',
    
    # Fields
    'CreatesonlineField',
    'StringField',
    'IntegerField',
    'FloatField',
    'BooleanField',
    'DateTimeField',
    'TextField',
    'JSONField',
    'EmbeddingField',
    'SlugField',
    'EmailField',
    'URLField',
    
    # Migrations
    'MigrationManager',
    'Migration'
]

# Global database instance
_database_instance = None

def get_database() -> Database:
    """Get global database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database()
    return _database_instance

def init_database(database_url: str = None, **kwargs) -> Database:
    """Initialize database with custom configuration"""
    global _database_instance
    _database_instance = Database(database_url=database_url, **kwargs)
    return _database_instance