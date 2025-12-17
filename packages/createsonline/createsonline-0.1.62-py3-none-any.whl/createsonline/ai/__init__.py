# createsonline/ai/__init__.py
"""
CREATESONLINE AI Module

Intelligent field types and AI services for CREATESONLINE applications.
Provides AIComputedField, LLMField, VectorField and smart AI capabilities.
"""

# Import main AI components
try:
    from .fields import (
        AIComputedField,
        LLMField, 
        VectorField,
        SmartTextField,
        PredictionField,
        EmbeddingField
    )
    from .services import (
        OpenAIService,
        AnthropicService,
        LocalMLService,
        VectorService
    )
    from .query import (
        SmartQueryEngine,
        NaturalLanguageQuery,
        AIQueryProcessor
    )
    from .models import (
        AIBaseModel,
        IntelligentMixin
    )
    
    _AI_AVAILABLE = True
except ImportError as e:
    # Graceful handling during development
    AIComputedField = None
    LLMField = None
    VectorField = None
    _AI_AVAILABLE = False
    _IMPORT_ERROR = str(e)

# AI module metadata
__version__ = "0.1.0"
__description__ = "CREATESONLINE AI capabilities and intelligent field types"

# Default AI settings
DEFAULT_AI_SETTINGS = {
    "default_llm_provider": "openai",
    "default_llm_model": "gpt-4",
    "default_embedding_model": "text-embedding-ada-002",
    "vector_dimensions": 1536,
    "batch_size": 32,
    "max_tokens": 500,
    "temperature": 0.7,
    "enable_caching": True,
    "cache_ttl": 3600,  # 1 hour
    "enable_async": True,
    "timeout": 30
}

def is_available() -> bool:
    """Check if AI module is properly loaded"""
    return _AI_AVAILABLE

def get_import_error() -> str:
    """Get import error if AI module failed to load"""
    if _AI_AVAILABLE:
        return ""
    return getattr(globals(), '_IMPORT_ERROR', "Unknown import error")

def get_ai_info() -> dict:
    """Get AI module information"""
    return {
        "module": "createsonline.ai",
        "version": __version__,
        "description": __description__,
        "available": _AI_AVAILABLE,
        "field_types": [
            "AIComputedField - ML predictions",
            "LLMField - Language model generation", 
            "VectorField - Embedding storage",
            "SmartTextField - AI-enhanced text",
            "PredictionField - Real-time predictions",
            "EmbeddingField - Semantic embeddings"
        ],
        "services": [
            "OpenAI Integration",
            "Anthropic Claude",
            "Local ML Models",
            "Vector Search",
            "Smart Query Engine"
        ],
        "capabilities": [
            "Natural language queries",
            "Semantic similarity search",
            "Content generation",
            "Predictive analytics",
            "Intelligent data processing",
            "Automated insights"
        ],
        "default_settings": DEFAULT_AI_SETTINGS
    }

# AI configuration management
class AIConfig:
    """Global AI configuration for CREATESONLINE"""
    
    def __init__(self):
        self.settings = DEFAULT_AI_SETTINGS.copy()
        self._services = {}
    
    def configure(self, **kwargs):
        """Configure AI settings"""
        self.settings.update(kwargs)
    
    def get_service(self, service_type: str):
        """Get AI service instance"""
        if service_type not in self._services:
            if service_type == "openai":
                from .services import OpenAIService
                self._services[service_type] = OpenAIService(self.settings)
            elif service_type == "anthropic":
                from .services import AnthropicService
                self._services[service_type] = AnthropicService(self.settings)
            elif service_type == "vector":
                from .services import VectorService
                self._services[service_type] = VectorService(self.settings)
            elif service_type == "local_ml":
                from .services import LocalMLService
                self._services[service_type] = LocalMLService(self.settings)
        
        return self._services.get(service_type)
    
    def reset(self):
        """Reset to default configuration"""
        self.settings = DEFAULT_AI_SETTINGS.copy()
        self._services.clear()

# Global AI configuration instance
ai_config = AIConfig()

# Convenience functions for quick AI operations
def generate_text(prompt: str, model: str = None, **kwargs) -> str:
    """Quick text generation using LLM"""
    if not _AI_AVAILABLE:
        raise ImportError("AI module not available")
    
    service = ai_config.get_service("openai")
    return service.generate_text(prompt, model=model, **kwargs)

def get_embedding(text: str, model: str = None) -> list:
    """Quick text embedding generation"""
    if not _AI_AVAILABLE:
        raise ImportError("AI module not available")
    
    service = ai_config.get_service("openai")
    return service.get_embedding(text, model=model)

def similarity_search(query: str, documents: list, top_k: int = 5) -> list:
    """Quick similarity search"""
    if not _AI_AVAILABLE:
        raise ImportError("AI module not available")
    
    service = ai_config.get_service("vector")
    return service.similarity_search(query, documents, top_k=top_k)

def predict(data: dict, model_name: str) -> dict:
    """Quick ML prediction"""
    if not _AI_AVAILABLE:
        raise ImportError("AI module not available")
    
    service = ai_config.get_service("local_ml")
    return service.predict(data, model_name)

# Export AI components
__all__ = [
    'AIComputedField',
    'LLMField',
    'VectorField', 
    'SmartTextField',
    'PredictionField',
    'EmbeddingField',
    'OpenAIService',
    'AnthropicService',
    'LocalMLService',
    'VectorService',
    'SmartQueryEngine',
    'NaturalLanguageQuery',
    'AIQueryProcessor',
    'AIBaseModel',
    'IntelligentMixin',
    'ai_config',
    'generate_text',
    'get_embedding',
    'similarity_search',
    'predict',
    'is_available',
    'get_ai_info',
    'DEFAULT_AI_SETTINGS'
]