"""
CREATESONLINE Database Models
Base model classes that wrap SQLAlchemy with clean API.
"""
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from .abstraction import Database

# SQLAlchemy base
SQLAlchemyBase = declarative_base()

class CreatesonlineModel(SQLAlchemyBase):
    """
    Base model class that provides clean API over SQLAlchemy.
    All CREATESONLINE models should inherit from this.
    """
    __abstract__ = True
    
    # Standard fields that every model gets
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """Initialize model with field values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def create(cls, **kwargs) -> 'CreatesonlineModel':
        """Create and save a new instance."""
        instance = cls(**kwargs)
        instance.save()
        return instance
    
    @classmethod
    def get(cls, id: int) -> Optional['CreatesonlineModel']:
        """Get instance by ID."""
        db = Database.get_instance()
        with db.session() as session:
            return session.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_by(cls, **filters) -> Optional['CreatesonlineModel']:
        """Get instance by field filters."""
        db = Database.get_instance()
        with db.session() as session:
            query = session.query(cls)
            for field, value in filters.items():
                if hasattr(cls, field):
                    query = query.filter(getattr(cls, field) == value)
            return query.first()
    
    @classmethod
    def filter(cls, **filters) -> List['CreatesonlineModel']:
        """Get all instances matching filters."""
        db = Database.get_instance()
        with db.session() as session:
            query = session.query(cls)
            for field, value in filters.items():
                if hasattr(cls, field):
                    query = query.filter(getattr(cls, field) == value)
            return query.all()
    
    @classmethod
    def all(cls) -> List['CreatesonlineModel']:
        """Get all instances."""
        db = Database.get_instance()
        with db.session() as session:
            return session.query(cls).all()
    
    @classmethod
    def count(cls, **filters) -> int:
        """Count instances matching filters."""
        db = Database.get_instance()
        with db.session() as session:
            query = session.query(cls)
            for field, value in filters.items():
                if hasattr(cls, field):
                    query = query.filter(getattr(cls, field) == value)
            return query.count()
    
    def save(self) -> 'CreatesonlineModel':
        """Save instance to database."""
        from sqlalchemy.orm import object_session
        
        db = Database.get_instance()
        session = object_session(self)
        
        if session is None:
            with db.session() as new_session:
                new_session.add(self)
                new_session.commit()
                new_session.refresh(self)
        else:
            session.add(self)
            session.commit()
            session.refresh(self)
        
        return self
    
    def update(self, **kwargs) -> 'CreatesonlineModel':
        """Update instance fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        return self.save()
    
    def delete(self) -> bool:
        """Delete instance from database."""
        from sqlalchemy.orm import object_session
        
        db = Database.get_instance()
        session = object_session(self)
        
        if session is None:
            with db.session() as new_session:
                # Merge the instance into the new session
                merged = new_session.merge(self)
                new_session.delete(merged)
                new_session.commit()
        else:
            session.delete(self)
            session.commit()
        
        return True
    
    def to_dict(self, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        exclude = exclude or []
        result = {}
        
        for column in self.__table__.columns:
            field_name = column.name
            if field_name not in exclude:
                value = getattr(self, field_name)
                
                # Handle datetime serialization
                if isinstance(value, datetime):
                    value = value.isoformat()
                
                result[field_name] = value
        
        return result
    
    def from_dict(self, data: Dict[str, Any]) -> 'CreatesonlineModel':
        """Update instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        return self
    
    @classmethod
    def bulk_create(cls, instances_data: List[Dict[str, Any]]) -> List['CreatesonlineModel']:
        """Create multiple instances efficiently."""
        db = Database.get_instance()
        instances = []
        
        with db.session() as session:
            for data in instances_data:
                instance = cls(**data)
                session.add(instance)
                instances.append(instance)
            
            session.commit()
            
            # Refresh all instances to get IDs
            for instance in instances:
                session.refresh(instance)
        
        return instances
    
    @classmethod
    def bulk_update(cls, updates: List[Dict[str, Any]], id_field: str = 'id') -> int:
        """Update multiple instances efficiently."""
        db = Database.get_instance()
        
        with db.session() as session:
            updated_count = 0
            
            for update_data in updates:
                if id_field not in update_data:
                    continue
                
                id_value = update_data.pop(id_field)
                update_data['updated_at'] = datetime.utcnow()
                
                result = session.query(cls).filter(
                    getattr(cls, id_field) == id_value
                ).update(update_data)
                
                updated_count += result
            
            session.commit()
            return updated_count
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


class QueryBuilder:
    """
    Fluent query builder for CREATESONLINE models.
    Provides intuitive query construction.
    """
    
    def __init__(self, model_class: Type[CreatesonlineModel]):
        self.model_class = model_class
        self.db = Database.get_instance()
        self._filters = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
    
    def where(self, field: str, operator: str = '=', value: Any = None) -> 'QueryBuilder':
        """Add WHERE clause."""
        if hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            
            if operator == '=':
                self._filters.append(column == value)
            elif operator == '!=':
                self._filters.append(column != value)
            elif operator == '>':
                self._filters.append(column > value)
            elif operator == '>=':
                self._filters.append(column >= value)
            elif operator == '<':
                self._filters.append(column < value)
            elif operator == '<=':
                self._filters.append(column <= value)
            elif operator == 'like':
                self._filters.append(column.like(value))
            elif operator == 'in':
                self._filters.append(column.in_(value))
            elif operator == 'not_in':
                self._filters.append(~column.in_(value))
            elif operator == 'is_null':
                self._filters.append(column.is_(None))
            elif operator == 'is_not_null':
                self._filters.append(column.is_not(None))
        
        return self
    
    def order_by(self, field: str, direction: str = 'asc') -> 'QueryBuilder':
        """Add ORDER BY clause."""
        if hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            if direction.lower() == 'desc':
                self._order_by.append(column.desc())
            else:
                self._order_by.append(column.asc())
        
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self._offset_value = count
        return self
    
    def _build_query(self, session):
        """Build SQLAlchemy query."""
        query = session.query(self.model_class)
        
        # Apply filters
        for filter_condition in self._filters:
            query = query.filter(filter_condition)
        
        # Apply ordering
        for order_condition in self._order_by:
            query = query.order_by(order_condition)
        
        # Apply offset
        if self._offset_value is not None:
            query = query.offset(self._offset_value)
        
        # Apply limit
        if self._limit_value is not None:
            query = query.limit(self._limit_value)
        
        return query
    
    def get(self) -> List[CreatesonlineModel]:
        """Execute query and return results."""
        with self.db.session() as session:
            query = self._build_query(session)
            return query.all()
    
    def first(self) -> Optional[CreatesonlineModel]:
        """Get first result."""
        with self.db.session() as session:
            query = self._build_query(session)
            return query.first()
    
    def count(self) -> int:
        """Count matching records."""
        with self.db.session() as session:
            query = session.query(self.model_class)
            
            # Apply filters only
            for filter_condition in self._filters:
                query = query.filter(filter_condition)
            
            return query.count()
    
    def exists(self) -> bool:
        """Check if any records match."""
        return self.count() > 0
    
    def delete(self) -> int:
        """Delete matching records."""
        with self.db.session() as session:
            query = session.query(self.model_class)
            
            # Apply filters only
            for filter_condition in self._filters:
                query = query.filter(filter_condition)
            
            count = query.count()
            query.delete()
            session.commit()
            
            return count
    
    def update(self, **values) -> int:
        """Update matching records."""
        values['updated_at'] = datetime.utcnow()
        
        with self.db.session() as session:
            query = session.query(self.model_class)
            
            # Apply filters only
            for filter_condition in self._filters:
                query = query.filter(filter_condition)
            
            count = query.update(values)
            session.commit()
            
            return count


# Convenience function for query building
def query(model_class: Type[CreatesonlineModel]) -> QueryBuilder:
    """Create a new query builder for the given model."""
    return QueryBuilder(model_class)


# ========================================
# ENHANCED AUDIT LOG MODEL
# ========================================

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json

class AuditLogType(Enum):
    """Types of operations that can be audited"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"


class AuditLogStatus(Enum):
    """Status of audited operations"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    CANCELLED = "cancelled"


class AuditLog:
    """Enhanced audit log model with rollback capabilities"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._ensure_audit_table()
    
    def _ensure_audit_table(self):
        """Ensure enhanced audit_logs table exists"""
        create_sql = f'''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id {'SERIAL' if self.db.db_type == 'postgresql' else 'INTEGER'} PRIMARY KEY{' AUTOINCREMENT' if self.db.db_type == 'sqlite' else ''},
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                operation_type VARCHAR(50) NOT NULL,
                table_name VARCHAR(100),
                record_id INTEGER,
                sql_query TEXT NOT NULL,
                original_prompt TEXT,
                parameters TEXT,
                status VARCHAR(20) NOT NULL,
                rows_affected INTEGER DEFAULT 0,
                error_message TEXT,
                user_id INTEGER REFERENCES createsonline_users(id),
                session_token VARCHAR(128),
                ip_address VARCHAR(45),
                user_agent TEXT,
                rollback_sql TEXT,
                rollback_status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(create_sql)
            self.db.connection.commit()
        except Exception as e:
            raise Exception(f"Failed to create enhanced audit_logs table: {e}")
    
    def log_operation(
        self, 
        operation_type: AuditLogType,
        sql_query: str,
        status: AuditLogStatus,
        table_name: str = None,
        record_id: int = None,
        original_prompt: str = None,
        parameters: Dict[str, Any] = None,
        rows_affected: int = 0,
        error_message: str = None,
        user_id: int = None,
        session_token: str = None,
        ip_address: str = None,
        user_agent: str = None,
        rollback_sql: str = None
    ) -> int:
        """Log an operation to the audit table"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type.value,
            'table_name': table_name,
            'record_id': record_id,
            'sql_query': sql_query,
            'original_prompt': original_prompt or '',
            'parameters': json.dumps(parameters) if parameters else None,
            'status': status.value,
            'rows_affected': rows_affected,
            'error_message': error_message or '',
            'user_id': user_id,
            'session_token': session_token,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'rollback_sql': rollback_sql,
            'rollback_status': None
        }
        
        try:
            audit_id = self.db.insert('audit_logs', log_entry)
            return audit_id
        except Exception as e:
            # Fallback logging if audit fails
            return None
    
    def get_by_id(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """Get audit log entry by ID"""
        try:
            placeholder = self.db._get_placeholder()
            result = self.db.execute(
                f"SELECT * FROM audit_logs WHERE id = {placeholder}",
                (audit_id,)
            )
            return result[0] if result else None
        except Exception:
            return None
    
    def get_recent(self, limit: int = 50, operation_type: AuditLogType = None) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        try:
            placeholder = self.db._get_placeholder()
            
            if operation_type:
                sql = f"""
                    SELECT * FROM audit_logs 
                    WHERE operation_type = {placeholder}
                    ORDER BY timestamp DESC 
                    LIMIT {limit}
                """
                params = (operation_type.value,)
            else:
                sql = f"""
                    SELECT * FROM audit_logs 
                    ORDER BY timestamp DESC 
                    LIMIT {limit}
                """
                params = ()
            
            return self.db.execute(sql, params)
        except Exception:
            return []
    
    def generate_rollback_sql(self, audit_id: int) -> Optional[str]:
        """Generate rollback SQL for a given audit entry"""
        audit_entry = self.get_by_id(audit_id)
        if not audit_entry:
            return None
        
        operation_type = audit_entry['operation_type']
        table_name = audit_entry['table_name']
        record_id = audit_entry['record_id']
        
        # For now, only handle simple cases
        if operation_type == 'insert' and record_id:
            # Rollback INSERT with DELETE
            return f"DELETE FROM {table_name} WHERE id = {record_id}"
        
        elif operation_type == 'delete' and record_id:
            # Rollback DELETE is complex - would need to store original data
            return f"-- Cannot auto-generate rollback for DELETE id={record_id} from {table_name}"
        
        elif operation_type == 'update':
            # Rollback UPDATE is complex - would need before/after values
            return f"-- Cannot auto-generate rollback for UPDATE on {table_name}"
        
        else:
            return f"-- No rollback available for {operation_type} operation"
    
    def execute_rollback(self, audit_id: int, dry_run: bool = True) -> Dict[str, Any]:
        """Execute rollback for an audit entry"""
        audit_entry = self.get_by_id(audit_id)
        if not audit_entry:
            return {'success': False, 'error': 'Audit entry not found'}
        
        # Check if already rolled back
        if audit_entry.get('rollback_status'):
            return {'success': False, 'error': 'Operation already rolled back'}
        
        # Generate rollback SQL
        rollback_sql = self.generate_rollback_sql(audit_id)
        if not rollback_sql or rollback_sql.startswith('--'):
            return {'success': False, 'error': 'Cannot generate rollback SQL for this operation'}
        
        if dry_run:
            return {
                'success': True,
                'rollback_sql': rollback_sql,
                'dry_run': True,
                'audit_entry': audit_entry
            }
        
        try:
            # Execute rollback
            result = self.db.execute(rollback_sql)
            
            # Update audit entry with rollback status
            self.db.update('audit_logs', 
                          {'rollback_sql': rollback_sql, 'rollback_status': 'completed'},
                          {'id': audit_id})
            
            # Log the rollback operation itself
            self.log_operation(
                operation_type=AuditLogType.DELETE,  # Or appropriate type
                sql_query=rollback_sql,
                status=AuditLogStatus.SUCCESS,
                table_name=audit_entry['table_name'],
                original_prompt=f"ROLLBACK of audit_id {audit_id}",
                rows_affected=len(result) if isinstance(result, list) else 1
            )
            
            return {
                'success': True,
                'rollback_sql': rollback_sql,
                'result': result,
                'audit_entry': audit_entry
            }
            
        except Exception as e:
            # Update audit entry with rollback error
            self.db.update('audit_logs',
                          {'rollback_sql': rollback_sql, 'rollback_status': f'error: {str(e)}'},
                          {'id': audit_id})
            
            return {
                'success': False,
                'error': str(e),
                'rollback_sql': rollback_sql,
                'audit_entry': audit_entry
            }


# Convenience function
def create_audit_log(db_connection) -> AuditLog:
    """Create an AuditLog instance"""
    return AuditLog(db_connection)