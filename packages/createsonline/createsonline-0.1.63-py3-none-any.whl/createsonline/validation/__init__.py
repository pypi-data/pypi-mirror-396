"""
CREATESONLINE Internal Validation System

Pure Python validation system with zero external dependencies.
Lightweight replacement for Pydantic with AI-native features.
"""

from .models import BaseModel, ValidationError
from .fields import (
    Field, StringField, IntField, FloatField, BoolField,
    EmailField, URLField, DateField, ListField, DictField,
    OptionalField, ChoiceField
)
from .validators import (
    validator, required, min_length, max_length,
    min_value, max_value, regex_validator, email_validator,
    url_validator
)

__all__ = [
    # Core classes
    'BaseModel',
    'ValidationError',
    
    # Fields
    'Field',
    'StringField',
    'IntField', 
    'FloatField',
    'BoolField',
    'EmailField',
    'URLField',
    'DateField',
    'ListField',
    'DictField',
    'OptionalField',
    'ChoiceField',
    
    # Validators
    'validator',
    'required',
    'min_length',
    'max_length', 
    'min_value',
    'max_value',
    'regex_validator',
    'email_validator',
    'url_validator'
]