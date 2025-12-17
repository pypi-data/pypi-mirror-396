"""
CREATESONLINE Database Fields
Field types that integrate with AI functionality.
"""
from typing import Any, Optional, Union, Dict, Callable
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Date, JSON
from sqlalchemy.types import TypeDecorator, VARCHAR
import json

# Base field class for compatibility
class CreatesonlineField:
    """
    Base CREATESONLINE field class for database abstraction.
    Provides compatibility layer for the Pure Independence implementation.
    """
    
    def __init__(self, 
                 primary_key: bool = False,
                 nullable: bool = True,
                 default: Any = None,
                 unique: bool = False,
                 index: bool = False,
                 **kwargs):
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
        self.extra_kwargs = kwargs
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column - must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement to_column method")


class AIEnhancedField(CreatesonlineField):
    """
    Base class for AI-enhanced fields that can be processed by AI models.
    """
    
    def __init__(self, 
                 ai_processable: bool = False,
                 ai_embedding: bool = False,
                 ai_searchable: bool = False,
                 ai_summarizable: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.ai_processable = ai_processable
        self.ai_embedding = ai_embedding  
        self.ai_searchable = ai_searchable
        self.ai_summarizable = ai_summarizable
        self.ai_metadata = {k: v for k, v in kwargs.items() if k.startswith('ai_')}


class StringField(AIEnhancedField):
    """Enhanced string field with AI capabilities."""
    
    def __init__(self, 
                 max_length: int = 255,
                 nullable: bool = True,
                 default: Optional[str] = None,
                 unique: bool = False,
                 index: bool = False,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.max_length = max_length
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            String(self.max_length),
            nullable=self.nullable,
            default=self.default,
            unique=self.unique,
            index=self.index
        )


class TextField(AIEnhancedField):
    """Enhanced text field for long content with AI capabilities."""
    
    def __init__(self,
                 nullable: bool = True,
                 default: Optional[str] = None,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.nullable = nullable
        self.default = default
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            Text,
            nullable=self.nullable,
            default=self.default
        )


class IntegerField(AIEnhancedField):
    """Enhanced integer field with AI capabilities."""
    
    def __init__(self,
                 nullable: bool = True,
                 default: Optional[int] = None,
                 unique: bool = False,
                 index: bool = False,
                 primary_key: bool = False,
                 autoincrement: bool = False,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
        self.primary_key = primary_key
        self.autoincrement = autoincrement
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            Integer,
            nullable=self.nullable,
            default=self.default,
            unique=self.unique,
            index=self.index,
            primary_key=self.primary_key,
            autoincrement=self.autoincrement
        )


class FloatField(AIEnhancedField):
    """Enhanced float field with AI capabilities."""
    
    def __init__(self,
                 nullable: bool = True,
                 default: Optional[float] = None,
                 unique: bool = False,
                 index: bool = False,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            Float,
            nullable=self.nullable,
            default=self.default,
            unique=self.unique,
            index=self.index
        )


class BooleanField(AIEnhancedField):
    """Enhanced boolean field with AI capabilities."""
    
    def __init__(self,
                 default: Optional[bool] = None,
                 nullable: bool = True,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.default = default
        self.nullable = nullable
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            Boolean,
            default=self.default,
            nullable=self.nullable
        )


class DateTimeField(AIEnhancedField):
    """Enhanced datetime field with AI capabilities."""
    
    def __init__(self,
                 auto_now: bool = False,
                 auto_now_add: bool = False,
                 default: Optional[Union[datetime, Callable]] = None,
                 nullable: bool = True,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        self.nullable = nullable
        
        if auto_now_add and default is None:
            self.default = datetime.utcnow
        elif auto_now and default is None:
            self.default = datetime.utcnow
        else:
            self.default = default
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        onupdate = datetime.utcnow if self.auto_now else None
        
        return Column(
            name,
            DateTime,
            default=self.default,
            onupdate=onupdate,
            nullable=self.nullable
        )


class DateField(AIEnhancedField):
    """Enhanced date field with AI capabilities."""
    
    def __init__(self,
                 auto_now: bool = False,
                 auto_now_add: bool = False,
                 default: Optional[Union[date, Callable]] = None,
                 nullable: bool = True,
                 **ai_kwargs):
        super().__init__(**ai_kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        self.nullable = nullable
        
        if auto_now_add and default is None:
            self.default = lambda: datetime.utcnow().date()
        elif auto_now and default is None:
            self.default = lambda: datetime.utcnow().date()
        else:
            self.default = default
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        onupdate = lambda: datetime.utcnow().date() if self.auto_now else None
        
        return Column(
            name,
            Date,
            default=self.default,
            onupdate=onupdate,
            nullable=self.nullable
        )


class JSONField(TypeDecorator, AIEnhancedField):
    """Enhanced JSON field with AI capabilities."""
    
    impl = VARCHAR
    cache_ok = True
    
    def __init__(self,
                 nullable: bool = True,
                 default: Optional[Union[dict, list]] = None,
                 **ai_kwargs):
        # Call parent constructors properly
        TypeDecorator.__init__(self)
        AIEnhancedField.__init__(self, **ai_kwargs)
        self.nullable = nullable
        self.default = default or {}
    
    def load_dialect_impl(self, dialect):
        """Load appropriate dialect implementation."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSON())
        else:
            return dialect.type_descriptor(VARCHAR())
    
    def process_bind_param(self, value, dialect):
        """Process value when binding to database."""
        if value is not None:
            return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Process value when retrieving from database."""
        if value is not None:
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return value
        return value
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column."""
        return Column(
            name,
            self,
            nullable=self.nullable,
            default=self.default
        )


class EmbeddingField(AIEnhancedField):
    """Special field for storing AI embeddings."""
    
    def __init__(self,
                 dimensions: int = 1536,  # OpenAI default
                 nullable: bool = True,
                 **ai_kwargs):
        super().__init__(ai_embedding=True, **ai_kwargs)
        self.dimensions = dimensions
        self.nullable = nullable
    
    def to_column(self, name: str) -> Column:
        """Convert to SQLAlchemy column (stores as JSON)."""
        return Column(
            name,
            JSON,
            nullable=self.nullable
        )


class SlugField(StringField):
    """URL-friendly slug field."""
    
    def __init__(self,
                 max_length: int = 100,
                 unique: bool = True,
                 index: bool = True,
                 **kwargs):
        super().__init__(
            max_length=max_length,
            unique=unique,
            index=index,
            **kwargs
        )


class EmailField(StringField):
    """Email field with validation."""
    
    def __init__(self,
                 max_length: int = 254,  # RFC 5321
                 unique: bool = False,
                 index: bool = True,
                 **kwargs):
        super().__init__(
            max_length=max_length,
            unique=unique,
            index=index,
            **kwargs
        )


class URLField(StringField):
    """URL field."""
    
    def __init__(self,
                 max_length: int = 2048,
                 **kwargs):
        super().__init__(
            max_length=max_length,
            **kwargs
        )


# Convenience functions for creating columns
def create_string_column(name: str, field: StringField) -> Column:
    """Create string column from field."""
    return field.to_column(name)

def create_text_column(name: str, field: TextField) -> Column:
    """Create text column from field."""
    return field.to_column(name)

def create_integer_column(name: str, field: IntegerField) -> Column:
    """Create integer column from field."""
    return field.to_column(name)

def create_float_column(name: str, field: FloatField) -> Column:
    """Create float column from field."""
    return field.to_column(name)

def create_boolean_column(name: str, field: BooleanField) -> Column:
    """Create boolean column from field."""
    return field.to_column(name)

def create_datetime_column(name: str, field: DateTimeField) -> Column:
    """Create datetime column from field."""
    return field.to_column(name)

def create_date_column(name: str, field: DateField) -> Column:
    """Create date column from field."""
    return field.to_column(name)

def create_json_column(name: str, field: JSONField) -> Column:
    """Create JSON column from field."""
    return field.to_column(name)

def create_embedding_column(name: str, field: EmbeddingField) -> Column:
    """Create embedding column from field."""
    return field.to_column(name)


# Field registry for AI processing
AI_FIELD_REGISTRY = {}

def register_ai_field(model_class, field_name: str, field: AIEnhancedField):
    """Register a field for AI processing."""
    model_name = model_class.__name__
    if model_name not in AI_FIELD_REGISTRY:
        AI_FIELD_REGISTRY[model_name] = {}
    
    AI_FIELD_REGISTRY[model_name][field_name] = {
        'field': field,
        'ai_processable': field.ai_processable,
        'ai_embedding': field.ai_embedding,
        'ai_searchable': field.ai_searchable,
        'ai_summarizable': field.ai_summarizable,
        'ai_metadata': field.ai_metadata
    }

def get_ai_fields(model_class) -> Dict[str, Dict]:
    """Get all AI-enhanced fields for a model."""
    model_name = model_class.__name__
    return AI_FIELD_REGISTRY.get(model_name, {})

def get_embedding_fields(model_class) -> Dict[str, Dict]:
    """Get all embedding fields for a model."""
    ai_fields = get_ai_fields(model_class)
    return {
        name: info for name, info in ai_fields.items()
        if info.get('ai_embedding', False)
    }

def get_searchable_fields(model_class) -> Dict[str, Dict]:
    """Get all searchable fields for a model."""
    ai_fields = get_ai_fields(model_class)
    return {
        name: info for name, info in ai_fields.items()
        if info.get('ai_searchable', False)
    }