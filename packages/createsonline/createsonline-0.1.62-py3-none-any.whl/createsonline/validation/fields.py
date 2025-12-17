"""
CREATESONLINE Validation Fields

Pure Python field validation.
"""

import re
import sys
from datetime import datetime, date
from .validators import ValidationError

# Handle typing compatibility
if sys.version_info >= (3, 9):
    from typing import Any, Optional, List, Dict, Union, Callable
else:
    # Fallback for older Python versions (shouldn't happen since we require 3.9+)
    from typing import Any, List, Dict, Union, Callable
    Optional = Union


class Field:
    """
    Base validation field
    
    Pure Python field validation with custom validators.
    """
    
    def __init__(
        self,
        default: Any = None,
        required: bool = True,
        validators: Optional[List[Callable[[Any], bool]]] = None,
        description: Optional[str] = None,
        alias: Optional[str] = None
    ):
        """
        Initialize field
        
        Args:
            default: Default value if not provided
            required: Whether field is required
            validators: List of validator functions
            description: Field description
            alias: Alternative field name
        """
        self.default = default
        self.required = required
        self.validators = validators or []
        self.description = description
        self.alias = alias
        
        # Add required validator if field is required
        if self.required and default is None:
            self.validators.insert(0, self._required_validator)
    
    def _required_validator(self, value: Any) -> bool:
        """Check if value is not None/empty"""
        if value is None:
            raise ValidationError("Field is required")
        if isinstance(value, (str, list, dict)) and len(value) == 0:
            raise ValidationError("Field cannot be empty")
        return True
    
    def validate(self, value: Any, field_name: str = "field") -> Any:
        """
        Validate field value
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
        
        Returns:
            Validated and converted value
        
        Raises:
            ValidationError: If validation fails
        """
        # Handle None values
        if value is None:
            if not self.required and self.default is not None:
                return self.default
            elif not self.required:
                return None
        
        # Type conversion
        try:
            value = self.convert_type(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid type for {field_name}: {e}")
        
        # Run validators
        for validator in self.validators:
            try:
                if not validator(value):
                    raise ValidationError(f"Validation failed for {field_name}")
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Validator error for {field_name}: {e}")
        
        return value
    
    def convert_type(self, value: Any) -> Any:
        """Convert value to appropriate type (override in subclasses)"""
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field definition to dictionary"""
        return {
            'type': self.__class__.__name__,
            'default': self.default,
            'required': self.required,
            'description': self.description,
            'alias': self.alias
        }


class StringField(Field):
    """String field with length validation"""
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize string field
        
        Args:
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regex pattern to match
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        
        # Add length validators
        if min_length is not None:
            self.validators.append(lambda x: self._validate_min_length(x))
        if max_length is not None:
            self.validators.append(lambda x: self._validate_max_length(x))
        if pattern is not None:
            self.validators.append(lambda x: self._validate_pattern(x))
    
    def _validate_min_length(self, value: str) -> bool:
        if len(value) < self.min_length:
            raise ValidationError(f"String too short, minimum length is {self.min_length}")
        return True
    
    def _validate_max_length(self, value: str) -> bool:
        if len(value) > self.max_length:
            raise ValidationError(f"String too long, maximum length is {self.max_length}")
        return True
    
    def _validate_pattern(self, value: str) -> bool:
        if not re.match(self.pattern, value):
            raise ValidationError(f"String does not match pattern: {self.pattern}")
        return True
    
    def convert_type(self, value: Any) -> str:
        """Convert value to string"""
        if isinstance(value, str):
            return value
        return str(value)


class IntField(Field):
    """Integer field with range validation"""
    
    def __init__(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize integer field
        
        Args:
            min_value: Minimum value
            max_value: Maximum value
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.min_value = min_value
        self.max_value = max_value
        
        # Add range validators
        if min_value is not None:
            self.validators.append(lambda x: self._validate_min_value(x))
        if max_value is not None:
            self.validators.append(lambda x: self._validate_max_value(x))
    
    def _validate_min_value(self, value: int) -> bool:
        if value < self.min_value:
            raise ValidationError(f"Value too small, minimum is {self.min_value}")
        return True
    
    def _validate_max_value(self, value: int) -> bool:
        if value > self.max_value:
            raise ValidationError(f"Value too large, maximum is {self.max_value}")
        return True
    
    def convert_type(self, value: Any) -> int:
        """Convert value to integer"""
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError("Cannot convert to integer")
        raise ValueError("Cannot convert to integer")


class FloatField(Field):
    """Float field with range validation"""
    
    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize float field
        
        Args:
            min_value: Minimum value
            max_value: Maximum value
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.min_value = min_value
        self.max_value = max_value
        
        # Add range validators
        if min_value is not None:
            self.validators.append(lambda x: self._validate_min_value(x))
        if max_value is not None:
            self.validators.append(lambda x: self._validate_max_value(x))
    
    def _validate_min_value(self, value: float) -> bool:
        if value < self.min_value:
            raise ValidationError(f"Value too small, minimum is {self.min_value}")
        return True
    
    def _validate_max_value(self, value: float) -> bool:
        if value > self.max_value:
            raise ValidationError(f"Value too large, maximum is {self.max_value}")
        return True
    
    def convert_type(self, value: Any) -> float:
        """Convert value to float"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValueError("Cannot convert to float")
        raise ValueError("Cannot convert to float")


class BoolField(Field):
    """Boolean field"""
    
    def convert_type(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError("Cannot convert string to boolean")
        if isinstance(value, (int, float)):
            return bool(value)
        raise ValueError("Cannot convert to boolean")


class EmailField(StringField):
    """Email field with email validation"""
    
    def __init__(self, **kwargs):
        """Initialize email field"""
        super().__init__(**kwargs)
        self.validators.append(self._validate_email)
    
    def _validate_email(self, value: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError("Invalid email format")
        return True


class URLField(StringField):
    """URL field with URL validation"""
    
    def __init__(self, **kwargs):
        """Initialize URL field"""
        super().__init__(**kwargs)
        self.validators.append(self._validate_url)
    
    def _validate_url(self, value: str) -> bool:
        """Validate URL format"""
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        if not re.match(url_pattern, value):
            raise ValidationError("Invalid URL format")
        return True


class DateField(Field):
    """Date field with date parsing"""
    
    def __init__(self, format: str = "%Y-%m-%d", **kwargs):
        """
        Initialize date field
        
        Args:
            format: Date format string
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        self.format = format
    
    def convert_type(self, value: Any) -> date:
        """Convert value to date"""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, self.format).date()
            except ValueError:
                raise ValueError(f"Date does not match format {self.format}")
        raise ValueError("Cannot convert to date")


class ListField(Field):
    """List field with item validation"""
    
    def __init__(
        self,
        item_field: Optional[Field] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize list field
        
        Args:
            item_field: Field for validating list items
            min_items: Minimum number of items
            max_items: Maximum number of items
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.item_field = item_field
        self.min_items = min_items
        self.max_items = max_items
        
        # Add list size validators
        if min_items is not None:
            self.validators.append(lambda x: self._validate_min_items(x))
        if max_items is not None:
            self.validators.append(lambda x: self._validate_max_items(x))
    
    def _validate_min_items(self, value: list) -> bool:
        if len(value) < self.min_items:
            raise ValidationError(f"List too short, minimum items is {self.min_items}")
        return True
    
    def _validate_max_items(self, value: list) -> bool:
        if len(value) > self.max_items:
            raise ValidationError(f"List too long, maximum items is {self.max_items}")
        return True
    
    def convert_type(self, value: Any) -> list:
        """Convert value to list"""
        if isinstance(value, list):
            return value
        if isinstance(value, (tuple, set)):
            return list(value)
        # Single item becomes list of one item
        return [value]
    
    def validate(self, value: Any, field_name: str = "field") -> list:
        """Validate list and its items"""
        # Validate the list itself
        validated_list = super().validate(value, field_name)
        
        if validated_list is None:
            return None
        
        # Validate each item if item_field is provided
        if self.item_field:
            validated_items = []
            for i, item in enumerate(validated_list):
                try:
                    validated_item = self.item_field.validate(item, f"{field_name}[{i}]")
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"Item {i} in {field_name}: {e}")
            return validated_items
        
        return validated_list


class DictField(Field):
    """Dictionary field with key/value validation"""
    
    def __init__(
        self,
        key_field: Optional[Field] = None,
        value_field: Optional[Field] = None,
        **kwargs
    ):
        """
        Initialize dictionary field
        
        Args:
            key_field: Field for validating dictionary keys
            value_field: Field for validating dictionary values
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.key_field = key_field
        self.value_field = value_field
    
    def convert_type(self, value: Any) -> dict:
        """Convert value to dictionary"""
        if isinstance(value, dict):
            return value
        raise ValueError("Cannot convert to dictionary")
    
    def validate(self, value: Any, field_name: str = "field") -> dict:
        """Validate dictionary and its keys/values"""
        # Validate the dictionary itself
        validated_dict = super().validate(value, field_name)
        
        if validated_dict is None:
            return None
        
        # Validate keys and values if field validators are provided
        if self.key_field or self.value_field:
            validated_items = {}
            for key, val in validated_dict.items():
                # Validate key
                if self.key_field:
                    try:
                        validated_key = self.key_field.validate(key, f"{field_name} key")
                    except ValidationError as e:
                        raise ValidationError(f"Key '{key}' in {field_name}: {e}")
                else:
                    validated_key = key
                
                # Validate value
                if self.value_field:
                    try:
                        validated_value = self.value_field.validate(val, f"{field_name}[{key}]")
                    except ValidationError as e:
                        raise ValidationError(f"Value for key '{key}' in {field_name}: {e}")
                else:
                    validated_value = val
                
                validated_items[validated_key] = validated_value
            
            return validated_items
        
        return validated_dict


class OptionalField(Field):
    """Optional field wrapper"""
    
    def __init__(self, inner_field: Field, **kwargs):
        """
        Initialize optional field
        
        Args:
            inner_field: The field to make optional
            **kwargs: Base field arguments
        """
        # Override required to False
        kwargs['required'] = False
        super().__init__(**kwargs)
        
        self.inner_field = inner_field
        # Copy inner field properties but make it non-required
        self.inner_field.required = False
    
    def validate(self, value: Any, field_name: str = "field") -> Any:
        """Validate optional field"""
        if value is None:
            return self.default
        
        return self.inner_field.validate(value, field_name)
    
    def convert_type(self, value: Any) -> Any:
        """Use inner field's type conversion"""
        return self.inner_field.convert_type(value)


class ChoiceField(Field):
    """Field that validates against a set of choices"""
    
    def __init__(self, choices: List[Any], **kwargs):
        """
        Initialize choice field
        
        Args:
            choices: List of valid choices
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        
        self.choices = choices
        self.validators.append(self._validate_choice)
    
    def _validate_choice(self, value: Any) -> bool:
        if value not in self.choices:
            raise ValidationError(f"Value must be one of: {self.choices}")
        return True


# Utility function for creating optional fields
def Optional(field: Field, default: Any = None) -> OptionalField:
    """Create an optional version of a field"""
    return OptionalField(field, default=default)


# Common field factory functions
def String(min_length=None, max_length=None, pattern=None, **kwargs):
    """Create a string field"""
    return StringField(min_length=min_length, max_length=max_length, pattern=pattern, **kwargs)


def Int(min_value=None, max_value=None, **kwargs):
    """Create an integer field"""
    return IntField(min_value=min_value, max_value=max_value, **kwargs)


def Float(min_value=None, max_value=None, **kwargs):
    """Create a float field"""
    return FloatField(min_value=min_value, max_value=max_value, **kwargs)


def Bool(**kwargs) -> BoolField:
    """Create a boolean field"""
    return BoolField(**kwargs)


def Email(**kwargs) -> EmailField:
    """Create an email field"""
    return EmailField(**kwargs)


def URL(**kwargs) -> URLField:
    """Create a URL field"""
    return URLField(**kwargs)


def Date(format: str = "%Y-%m-%d", **kwargs) -> DateField:
    """Create a date field"""
    return DateField(format=format, **kwargs)


def List(item_field=None, min_items=None, max_items=None, **kwargs):
    """Create a list field"""
    return ListField(item_field=item_field, min_items=min_items, max_items=max_items, **kwargs)


def Dict(key_field=None, value_field=None, **kwargs):
    """Create a dictionary field"""
    return DictField(key_field=key_field, value_field=value_field, **kwargs)


def Choice(choices, **kwargs):
    """Create a choice field"""
    return ChoiceField(choices=choices, **kwargs)