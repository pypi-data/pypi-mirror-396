"""
CREATESONLINE Validation Models

Pure Python model validation.
Lightweight replacement for Pydantic BaseModel.
"""

import json
import sys
from typing import Any, Dict, List, Optional, Type, Union
from .fields import Field
from .validators import ValidationError

# Handle typing compatibility across Python versions
if sys.version_info >= (3, 10):
    from typing import get_type_hints
else:
    try:
        from typing import get_type_hints
    except ImportError:
        def get_type_hints(obj):
            return getattr(obj, '__annotations__', {})


class ModelMeta(type):
    """Metaclass for BaseModel to collect field definitions"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Collect fields from the class definition
        fields = {}
        
        # Inherit fields from base classes
        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)
        
        # Add fields from current class
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                fields[key] = value
                # Remove field from namespace to avoid conflicts
                namespace.pop(key)
        
        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Store fields on the class
        cls._fields = fields
        
        # Store field names for easier access
        cls._field_names = list(fields.keys())
        
        return cls


class BaseModel(metaclass=ModelMeta):
    """
    Base model class for data validation
    
    Pure Python implementation similar to Pydantic BaseModel.
    """
    
    _fields: Dict[str, Field] = {}
    _field_names: List[str] = []
    
    def __init__(self, **data):
        """
        Initialize model with data validation
        
        Args:
            **data: Data to validate and assign
        """
        self._validated_data = {}
        self._errors = {}
        
        # Process each field
        for field_name, field in self._fields.items():
            # Check for alias
            data_key = field.alias if field.alias else field_name
            
            # Get value from data
            if data_key in data:
                value = data[data_key]
            elif field.default is not None:
                value = field.default
            elif not field.required:
                value = None
            else:
                self._errors[field_name] = "Field is required"
                continue
            
            # Validate field
            try:
                validated_value = field.validate(value, field_name)
                self._validated_data[field_name] = validated_value
                # Set as attribute for easy access
                setattr(self, field_name, validated_value)
            except ValidationError as e:
                self._errors[field_name] = str(e)
        
        # Check for unknown fields
        known_keys = set(field.alias if field.alias else name for name, field in self._fields.items())
        unknown_keys = set(data.keys()) - known_keys
        if unknown_keys:
            for key in unknown_keys:
                self._errors[key] = f"Unknown field: {key}"
        
        # Raise validation error if there are any errors
        if self._errors:
            raise ValidationError(f"Validation failed: {self._errors}")
    
    @classmethod
    def validate(cls, data: Union[Dict[str, Any], 'BaseModel']) -> 'BaseModel':
        """
        Validate data and return model instance
        
        Args:
            data: Data to validate (dict or BaseModel)
        
        Returns:
            Validated model instance
        
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise ValidationError("Data must be a dictionary or model instance")
    
    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> 'BaseModel':
        """
        Parse object (alias for validate)
        
        Args:
            obj: Object to parse
        
        Returns:
            Validated model instance
        """
        return cls.validate(obj)
    
    @classmethod
    def parse_raw(cls, raw_data: Union[str, bytes], content_type: str = 'json') -> 'BaseModel':
        """
        Parse raw data (JSON, etc.)
        
        Args:
            raw_data: Raw data to parse
            content_type: Content type ('json' supported)
        
        Returns:
            Validated model instance
        """
        if content_type == 'json':
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode('utf-8')
            
            try:
                data = json.loads(raw_data)
                return cls.validate(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {e}")
        else:
            raise ValidationError(f"Unsupported content type: {content_type}")
    
    @classmethod
    def parse_file(cls, file_path: str, content_type: str = 'json', encoding: str = 'utf-8') -> 'BaseModel':
        """
        Parse data from file
        
        Args:
            file_path: Path to file
            content_type: Content type ('json' supported)
            encoding: File encoding
        
        Returns:
            Validated model instance
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                raw_data = f.read()
            return cls.parse_raw(raw_data, content_type)
        except IOError as e:
            raise ValidationError(f"Error reading file: {e}")
    
    def dict(
        self,
        include: Optional[Union[List[str], set]] = None,
        exclude: Optional[Union[List[str], set]] = None,
        by_alias: bool = False
    ) -> Dict[str, Any]:
        """
        Convert model to dictionary
        
        Args:
            include: Fields to include
            exclude: Fields to exclude
            by_alias: Use field aliases as keys
        
        Returns:
            Dictionary representation
        """
        result = {}
        
        for field_name, value in self._validated_data.items():
            # Check include/exclude filters
            if include is not None and field_name not in include:
                continue
            if exclude is not None and field_name in exclude:
                continue
            
            # Use alias if requested and available
            if by_alias and field_name in self._fields:
                field = self._fields[field_name]
                key = field.alias if field.alias else field_name
            else:
                key = field_name
            
            result[key] = value
        
        return result
    
    def json(
        self,
        include: Optional[Union[List[str], set]] = None,
        exclude: Optional[Union[List[str], set]] = None,
        by_alias: bool = False,
        indent: Optional[int] = None
    ) -> str:
        """
        Convert model to JSON string
        
        Args:
            include: Fields to include
            exclude: Fields to exclude
            by_alias: Use field aliases as keys
            indent: JSON indentation
        
        Returns:
            JSON string representation
        """
        data = self.dict(include=include, exclude=exclude, by_alias=by_alias)
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    def copy(
        self,
        update: Optional[Dict[str, Any]] = None,
        deep: bool = False
    ) -> 'BaseModel':
        """
        Create a copy of the model
        
        Args:
            update: Fields to update in the copy
            deep: Whether to perform deep copy
        
        Returns:
            Copied model instance
        """
        data = self.dict()
        
        if update:
            data.update(update)
        
        if deep:
            import copy
            data = copy.deepcopy(data)
        
        return self.__class__(**data)
    
    def update(self, update_data: Dict[str, Any]) -> 'BaseModel':
        """
        Update model with new data
        
        Args:
            update_data: Data to update
        
        Returns:
            Updated model instance
        """
        current_data = self.dict()
        current_data.update(update_data)
        return self.__class__(**current_data)
    
    @classmethod
    def schema(cls, by_alias: bool = True) -> Dict[str, Any]:
        """
        Generate JSON schema for the model
        
        Args:
            by_alias: Use field aliases in schema
        
        Returns:
            JSON schema dictionary
        """
        properties = {}
        required = []
        
        for field_name, field in cls._fields.items():
            # Use alias if requested and available
            schema_name = field.alias if by_alias and field.alias else field_name
            
            # Basic field schema
            field_schema = {
                'type': cls._get_json_type(field),
                'description': field.description
            }
            
            # Add field-specific constraints
            if hasattr(field, 'min_length') and field.min_length is not None:
                field_schema['minLength'] = field.min_length
            if hasattr(field, 'max_length') and field.max_length is not None:
                field_schema['maxLength'] = field.max_length
            if hasattr(field, 'min_value') and field.min_value is not None:
                field_schema['minimum'] = field.min_value
            if hasattr(field, 'max_value') and field.max_value is not None:
                field_schema['maximum'] = field.max_value
            if hasattr(field, 'pattern') and field.pattern is not None:
                field_schema['pattern'] = field.pattern
            if hasattr(field, 'choices') and field.choices is not None:
                field_schema['enum'] = field.choices
            
            # Default value
            if field.default is not None:
                field_schema['default'] = field.default
            
            properties[schema_name] = field_schema
            
            # Required fields
            if field.required and field.default is None:
                required.append(schema_name)
        
        schema = {
            'type': 'object',
            'properties': properties,
            'title': cls.__name__
        }
        
        if required:
            schema['required'] = required
        
        return schema
    
    @staticmethod
    def _get_json_type(field: Field) -> str:
        """Get JSON schema type for a field"""
        from .fields import (
            StringField, IntField, FloatField, BoolField,
            EmailField, URLField, DateField, ListField, DictField
        )
        
        if isinstance(field, (StringField, EmailField, URLField, DateField)):
            return 'string'
        elif isinstance(field, IntField):
            return 'integer'
        elif isinstance(field, FloatField):
            return 'number'
        elif isinstance(field, BoolField):
            return 'boolean'
        elif isinstance(field, ListField):
            return 'array'
        elif isinstance(field, DictField):
            return 'object'
        else:
            return 'string'  # Default fallback
    
    def __repr__(self) -> str:
        """String representation of the model"""
        fields_repr = ', '.join(f'{k}={v!r}' for k, v in self._validated_data.items())
        return f'{self.__class__.__name__}({fields_repr})'
    
    def __str__(self) -> str:
        """String representation of the model"""
        return self.__repr__()
    
    def __eq__(self, other) -> bool:
        """Check equality with another model"""
        if not isinstance(other, self.__class__):
            return False
        return self._validated_data == other._validated_data
    
    def __hash__(self) -> int:
        """Hash of the model"""
        return hash(tuple(sorted(self._validated_data.items())))
    
    def __getitem__(self, item: str) -> Any:
        """Get field value by name"""
        if item in self._validated_data:
            return self._validated_data[item]
        raise KeyError(f"Field '{item}' not found")
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set field value (with validation)"""
        if key in self._fields:
            field = self._fields[key]
            try:
                validated_value = field.validate(value, key)
                self._validated_data[key] = validated_value
                setattr(self, key, validated_value)
            except ValidationError as e:
                raise ValidationError(f"Validation failed for field '{key}': {e}")
        else:
            raise KeyError(f"Unknown field '{key}'")
    
    def __contains__(self, item: str) -> bool:
        """Check if field exists"""
        return item in self._validated_data
    
    def __iter__(self):
        """Iterate over field names"""
        return iter(self._validated_data)
    
    def keys(self):
        """Get field names"""
        return self._validated_data.keys()
    
    def values(self):
        """Get field values"""
        return self._validated_data.values()
    
    def items(self):
        """Get field items"""
        return self._validated_data.items()


# Utility functions for creating models dynamically
def create_model(
    model_name: str,
    fields: Dict[str, Field],
    base_class: Type[BaseModel] = BaseModel
) -> Type[BaseModel]:
    """
    Create a model class dynamically
    
    Args:
        model_name: Name of the model class
        fields: Dictionary of field definitions
        base_class: Base class to inherit from
    
    Returns:
        Dynamically created model class
    """
    # Create class attributes
    attrs = dict(fields)
    attrs['__module__'] = __name__
    
    # Create the class
    model_class = type(model_name, (base_class,), attrs)
    
    return model_class


# Validation shortcuts
def validate_data(data: Dict[str, Any], fields: Dict[str, Field]) -> Dict[str, Any]:
    """
    Validate data against field definitions without creating a model
    
    Args:
        data: Data to validate
        fields: Field definitions
    
    Returns:
        Validated data dictionary
    
    Raises:
        ValidationError: If validation fails
    """
    validated_data = {}
    errors = {}
    
    for field_name, field in fields.items():
        # Get value from data
        if field_name in data:
            value = data[field_name]
        elif field.default is not None:
            value = field.default
        elif not field.required:
            value = None
        else:
            errors[field_name] = "Field is required"
            continue
        
        # Validate field
        try:
            validated_value = field.validate(value, field_name)
            validated_data[field_name] = validated_value
        except ValidationError as e:
            errors[field_name] = str(e)
    
    # Check for unknown fields
    unknown_keys = set(data.keys()) - set(fields.keys())
    if unknown_keys:
        for key in unknown_keys:
            errors[key] = f"Unknown field: {key}"
    
    # Raise validation error if there are any errors
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return validated_data