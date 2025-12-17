# createsonline/ai/orm.py
"""
CREATESONLINE AI-Enhanced ORM

AI-powered database operations with smart queries and intelligent fields.
"""
from typing import Any, Dict, List, Optional, Type
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Create base model class for CREATESONLINE
Base = declarative_base()

class AIBaseModel(Base):
    """
    Base model class with AI enhancements for CREATESONLINE applications
    
    Provides automatic AI field processing and intelligent database operations.
    """
    __abstract__ = True
    
    # Standard fields for all models
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = sa.Column(
        sa.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    def __init__(self, **kwargs):
        """Initialize model with AI field processing"""
        super().__init__(**kwargs)
        self._ai_fields = {}
        self._discover_ai_fields()
    
    def _discover_ai_fields(self):
        """Discover AI fields in this model"""
        from createsonline.ai.fields import AIFieldMixin
        
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, type) and issubclass(attr, AIFieldMixin):
                self._ai_fields[attr_name] = attr
    
    async def compute_ai_fields(self):
        """Compute all AI fields for this instance"""
        from createsonline.ai.fields import AIComputedField, LLMField, VectorField
        
        for field_name, field in self._ai_fields.items():
            try:
                if isinstance(field, AIComputedField):
                    # Compute AI-predicted value
                    features = self._extract_features_for_field(field)
                    value = await field.compute_value(self, features)
                    setattr(self, field_name, value)
                    
                elif isinstance(field, LLMField):
                    # Generate content with LLM
                    template_data = self._extract_template_data_for_field(field)
                    content = await field.generate_content(self, template_data)
                    setattr(self, field_name, content)
                    
                elif isinstance(field, VectorField):
                    # Generate vector embedding
                    source_data = self._extract_source_data_for_field(field)
                    embedding = await field.generate_embedding(self, source_data)
                    setattr(self, field_name, embedding)
                    
            except Exception as e:
                pass
    
    def _extract_features_for_field(self, field) -> Dict[str, Any]:
        """Extract features for AI computation"""
        features = {}
        
        # Get features from field configuration
        feature_fields = field.ai_config.get('features', [])
        source_field = field.ai_config.get('source_field')
        
        if feature_fields:
            for feature_field in feature_fields:
                if hasattr(self, feature_field):
                    features[feature_field] = getattr(self, feature_field)
        elif source_field:
            if hasattr(self, source_field):
                features[source_field] = getattr(self, source_field)
        
        return features
    
    def _extract_template_data_for_field(self, field) -> Dict[str, Any]:
        """Extract template data for LLM generation"""
        template_data = {}
        
        # Extract all non-AI fields as template variables
        for attr_name in dir(self):
            if not attr_name.startswith('_') and hasattr(self, attr_name):
                value = getattr(self, attr_name)
                if isinstance(value, (str, int, float, bool)) and value is not None:
                    template_data[attr_name] = value
        
        return template_data
    
    def _extract_source_data_for_field(self, field) -> Any:
        """Extract source data for vector embedding"""
        source_field = field.ai_config.get('source_field')
        
        if source_field and hasattr(self, source_field):
            return getattr(self, source_field)
        
        # Fallback to description or name field
        for fallback_field in ['description', 'content', 'text', 'name']:
            if hasattr(self, fallback_field):
                return getattr(self, fallback_field)
        
        return str(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, (list, dict)):
                result[column.name] = value
            else:
                result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"

class AIEnhancedORM:
    """
    AI-Enhanced ORM for CREATESONLINE framework
    
    Provides intelligent database operations with AI capabilities.
    """
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize AI-Enhanced ORM
        
        Args:
            database_url: Database connection string
            echo: Enable SQL logging
        """
        self.database_url = database_url
        self.engine = sa.create_engine(database_url, echo=echo)
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        
        # AI services integration
        self._ai_enabled = True
        self._ai_cache = {}
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables in the database"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert ``CamelCase`` identifiers into ``snake_case`` table names."""

        import re

        if not name:
            return name

        snake = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", snake)
        return snake.replace("__", "_").strip("_").lower()

    async def smart_query(
        self,
        model: Type[AIBaseModel],
        natural_language_query: str
    ) -> List[AIBaseModel]:
        """
        Execute a query using natural language
        
        Args:
            model: Model class to query
            natural_language_query: Natural language query string
            
        Returns:
            List of query results
        """
        # TODO: Implement natural language to SQL transformation
        # For now, return basic query
        session = self.get_session()
        try:
            # Simple implementation - would be enhanced with AI
            query = session.query(model)
            
            # Basic keyword matching
            if 'recent' in natural_language_query.lower():
                query = query.order_by(model.created_at.desc())
            
            if 'limit' in natural_language_query.lower():
                # Extract number after 'limit'
                import re
                match = re.search(r'limit\s+(\d+)', natural_language_query.lower())
                if match:
                    limit = int(match.group(1))
                    query = query.limit(limit)
            
            return query.all()
            
        finally:
            session.close()
    
    def create_model_from_description(
        self,
        description: str,
        model_name: str = "GeneratedModel"
    ) -> Type[AIBaseModel]:
        """
        Generate a model class from natural language description
        
        Args:
            description: Natural language description of the model
            model_name: Name for the generated model
            
        Returns:
            Generated model class
        """
        # TODO: Implement AI-driven schema generation
        # For now, create a basic model
        
        attributes = {
            '__tablename__': self._to_snake_case(model_name),
            'name': sa.Column(sa.String(255), nullable=False),
            'description': sa.Column(sa.Text),
        }
        
        # Create dynamic model class
        GeneratedModel = type(model_name, (AIBaseModel,), attributes)

        return GeneratedModel

    def generate_schema_from_description(
        self,
        description: str,
        model_name: str = "GeneratedModel"
    ) -> Type[AIBaseModel]:
        """Backward compatible wrapper for deprecated API usage.

        Earlier revisions of the project exposed ``generate_schema_from_description``
        which delegated to the dynamic model creation helper.  The method was
        renamed during refactoring, but parts of the codebase – including the
        published tests – still rely on the original name.  Provide the thin
        alias so existing integrations continue to function while new code can
        adopt :meth:`create_model_from_description`.
        """

        return self.create_model_from_description(description, model_name)
    
    async def predict_related_entities(
        self, 
        instance: AIBaseModel
    ) -> Dict[str, List[Any]]:
        """
        Predict related entities using AI
        
        Args:
            instance: Model instance
            
        Returns:
            Dictionary of predicted related entities
        """
        # TODO: Implement AI-based relationship prediction
        return {}
    
    def get_model_statistics(self, model: Type[AIBaseModel]) -> Dict[str, Any]:
        """Get statistics for a model"""
        session = self.get_session()
        try:
            total_count = session.query(model).count()
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow().replace(day=1)  # Simplified
            recent_count = session.query(model).filter(
                model.created_at >= thirty_days_ago
            ).count()
            
            return {
                'total_records': total_count,
                'recent_records': recent_count,
                'model_name': model.__name__,
                'table_name': model.__tablename__
            }
            
        finally:
            session.close()

# Global ORM instance (initialized by application)
ai_orm: Optional[AIEnhancedORM] = None

def get_ai_orm() -> AIEnhancedORM:
    """Get the global AI ORM instance"""
    if ai_orm is None:
        raise RuntimeError("AI ORM not initialized. Call initialize_ai_orm() first.")
    return ai_orm

def initialize_ai_orm(database_url: str, echo: bool = False) -> AIEnhancedORM:
    """Initialize the global AI ORM instance"""
    global ai_orm
    ai_orm = AIEnhancedORM(database_url, echo)
    return ai_orm
