"""
CREATESONLINE Validation Validators

Pure Python validation functions.
"""

import re
from typing import Any, Callable, Pattern, Union, List


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validator(func: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """
    Decorator to mark a function as a validator
    
    Args:
        func: Validator function
    
    Returns:
        Decorated validator function
    """
    def wrapper(value: Any) -> bool:
        try:
            result = func(value)
            if not result:
                raise ValidationError("Validation failed")
            return result
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validator error: {e}")
    
    wrapper._is_validator = True
    return wrapper


@validator
def required(value: Any) -> bool:
    """Validate that value is not None or empty"""
    if value is None:
        raise ValidationError("Field is required")
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        raise ValidationError("Field cannot be empty")
    return True


def min_length(length: int) -> Callable[[Any], bool]:
    """
    Create validator for minimum length
    
    Args:
        length: Minimum length
    
    Returns:
        Validator function
    """
    @validator
    def _min_length(value: Any) -> bool:
        if hasattr(value, '__len__'):
            if len(value) < length:
                raise ValidationError(f"Must be at least {length} characters/items long")
            return True
        raise ValidationError("Value must have length")
    
    return _min_length


def max_length(length: int) -> Callable[[Any], bool]:
    """
    Create validator for maximum length
    
    Args:
        length: Maximum length
    
    Returns:
        Validator function
    """
    @validator
    def _max_length(value: Any) -> bool:
        if hasattr(value, '__len__'):
            if len(value) > length:
                raise ValidationError(f"Must be at most {length} characters/items long")
            return True
        raise ValidationError("Value must have length")
    
    return _max_length


def min_value(minimum: Union[int, float]) -> Callable[[Any], bool]:
    """
    Create validator for minimum value
    
    Args:
        minimum: Minimum value
    
    Returns:
        Validator function
    """
    @validator
    def _min_value(value: Any) -> bool:
        if not isinstance(value, (int, float)):
            raise ValidationError("Value must be numeric")
        if value < minimum:
            raise ValidationError(f"Must be at least {minimum}")
        return True
    
    return _min_value


def max_value(maximum: Union[int, float]) -> Callable[[Any], bool]:
    """
    Create validator for maximum value
    
    Args:
        maximum: Maximum value
    
    Returns:
        Validator function
    """
    @validator
    def _max_value(value: Any) -> bool:
        if not isinstance(value, (int, float)):
            raise ValidationError("Value must be numeric")
        if value > maximum:
            raise ValidationError(f"Must be at most {maximum}")
        return True
    
    return _max_value


def regex_validator(pattern: Union[str, Pattern], message: str = None) -> Callable[[str], bool]:
    """
    Create validator for regex pattern matching
    
    Args:
        pattern: Regex pattern (string or compiled pattern)
        message: Custom error message
    
    Returns:
        Validator function
    """
    if isinstance(pattern, str):
        compiled_pattern = re.compile(pattern)
    else:
        compiled_pattern = pattern
    
    @validator
    def _regex_validator(value: str) -> bool:
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not compiled_pattern.match(value):
            error_msg = message or f"Value does not match pattern: {pattern}"
            raise ValidationError(error_msg)
        return True
    
    return _regex_validator


@validator
def email_validator(value: str) -> bool:
    """Validate email format"""
    if not isinstance(value, str):
        raise ValidationError("Email must be a string")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError("Invalid email format")
    return True


@validator
def url_validator(value: str) -> bool:
    """Validate URL format"""
    if not isinstance(value, str):
        raise ValidationError("URL must be a string")
    
    url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    if not re.match(url_pattern, value):
        raise ValidationError("Invalid URL format")
    return True


def in_range(min_val: Union[int, float], max_val: Union[int, float]) -> Callable[[Any], bool]:
    """
    Create validator for value within range
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
    
    Returns:
        Validator function
    """
    @validator
    def _in_range(value: Any) -> bool:
        if not isinstance(value, (int, float)):
            raise ValidationError("Value must be numeric")
        if not (min_val <= value <= max_val):
            raise ValidationError(f"Value must be between {min_val} and {max_val}")
        return True
    
    return _in_range


def one_of(choices: List[Any]) -> Callable[[Any], bool]:
    """
    Create validator for value in choices
    
    Args:
        choices: List of valid choices
    
    Returns:
        Validator function
    """
    @validator
    def _one_of(value: Any) -> bool:
        if value not in choices:
            raise ValidationError(f"Value must be one of: {choices}")
        return True
    
    return _one_of


def not_empty(value: Any) -> bool:
    """Validate that value is not empty"""
    if value is None:
        raise ValidationError("Value cannot be None")
    if isinstance(value, (str, list, dict, tuple, set)) and len(value) == 0:
        raise ValidationError("Value cannot be empty")
    return True


def positive(value: Union[int, float]) -> bool:
    """Validate that numeric value is positive"""
    if not isinstance(value, (int, float)):
        raise ValidationError("Value must be numeric")
    if value <= 0:
        raise ValidationError("Value must be positive")
    return True


def negative(value: Union[int, float]) -> bool:
    """Validate that numeric value is negative"""
    if not isinstance(value, (int, float)):
        raise ValidationError("Value must be numeric")
    if value >= 0:
        raise ValidationError("Value must be negative")
    return True


def non_negative(value: Union[int, float]) -> bool:
    """Validate that numeric value is non-negative"""
    if not isinstance(value, (int, float)):
        raise ValidationError("Value must be numeric")
    if value < 0:
        raise ValidationError("Value must be non-negative")
    return True


def alpha_validator(value: str) -> bool:
    """Validate that string contains only alphabetic characters"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    if not value.isalpha():
        raise ValidationError("Value must contain only alphabetic characters")
    return True


def alphanumeric_validator(value: str) -> bool:
    """Validate that string contains only alphanumeric characters"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    if not value.isalnum():
        raise ValidationError("Value must contain only alphanumeric characters")
    return True


def numeric_validator(value: str) -> bool:
    """Validate that string contains only numeric characters"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    if not value.isdigit():
        raise ValidationError("Value must contain only numeric characters")
    return True


def no_whitespace(value: str) -> bool:
    """Validate that string contains no whitespace"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    if ' ' in value or '\t' in value or '\n' in value:
        raise ValidationError("Value cannot contain whitespace")
    return True


def starts_with(prefix: str) -> Callable[[str], bool]:
    """
    Create validator for string starting with prefix
    
    Args:
        prefix: Required prefix
    
    Returns:
        Validator function
    """
    @validator
    def _starts_with(value: str) -> bool:
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not value.startswith(prefix):
            raise ValidationError(f"Value must start with '{prefix}'")
        return True
    
    return _starts_with


def ends_with(suffix: str) -> Callable[[str], bool]:
    """
    Create validator for string ending with suffix
    
    Args:
        suffix: Required suffix
    
    Returns:
        Validator function
    """
    @validator
    def _ends_with(value: str) -> bool:
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if not value.endswith(suffix):
            raise ValidationError(f"Value must end with '{suffix}'")
        return True
    
    return _ends_with


def contains(substring: str) -> Callable[[str], bool]:
    """
    Create validator for string containing substring
    
    Args:
        substring: Required substring
    
    Returns:
        Validator function
    """
    @validator
    def _contains(value: str) -> bool:
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if substring not in value:
            raise ValidationError(f"Value must contain '{substring}'")
        return True
    
    return _contains


def unique_items(value: List[Any]) -> bool:
    """Validate that list contains only unique items"""
    if not isinstance(value, list):
        raise ValidationError("Value must be a list")
    if len(value) != len(set(value)):
        raise ValidationError("List must contain only unique items")
    return True


def all_same_type(value: List[Any]) -> bool:
    """Validate that all items in list are of the same type"""
    if not isinstance(value, list):
        raise ValidationError("Value must be a list")
    if len(value) == 0:
        return True
    
    first_type = type(value[0])
    if not all(isinstance(item, first_type) for item in value):
        raise ValidationError("All items in list must be of the same type")
    return True


def password_strength(
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special: bool = True
) -> Callable[[str], bool]:
    """
    Create validator for password strength
    
    Args:
        min_length: Minimum password length
        require_uppercase: Require uppercase letters
        require_lowercase: Require lowercase letters
        require_digits: Require digits
        require_special: Require special characters
    
    Returns:
        Validator function
    """
    @validator
    def _password_strength(value: str) -> bool:
        if not isinstance(value, str):
            raise ValidationError("Password must be a string")
        
        if len(value) < min_length:
            raise ValidationError(f"Password must be at least {min_length} characters long")
        
        if require_uppercase and not any(c.isupper() for c in value):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if require_lowercase and not any(c.islower() for c in value):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if require_digits and not any(c.isdigit() for c in value):
            raise ValidationError("Password must contain at least one digit")
        
        if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value):
            raise ValidationError("Password must contain at least one special character")
        
        return True
    
    return _password_strength


def json_validator(value: str) -> bool:
    """Validate that string is valid JSON"""
    import json
    
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    try:
        json.loads(value)
        return True
    except json.JSONDecodeError:
        raise ValidationError("Value must be valid JSON")


def ipv4_validator(value: str) -> bool:
    """Validate IPv4 address format"""
    if not isinstance(value, str):
        raise ValidationError("IP address must be a string")
    
    parts = value.split('.')
    if len(parts) != 4:
        raise ValidationError("Invalid IPv4 address format")
    
    for part in parts:
        try:
            num = int(part)
            if not (0 <= num <= 255):
                raise ValidationError("Invalid IPv4 address - parts must be 0-255")
        except ValueError:
            raise ValidationError("Invalid IPv4 address - parts must be integers")
    
    return True


def credit_card_validator(value: str) -> bool:
    """Validate credit card number using Luhn algorithm"""
    if not isinstance(value, str):
        raise ValidationError("Credit card number must be a string")
    
    # Remove spaces and dashes
    cleaned = value.replace(' ', '').replace('-', '')
    
    if not cleaned.isdigit():
        raise ValidationError("Credit card number must contain only digits")
    
    if len(cleaned) < 13 or len(cleaned) > 19:
        raise ValidationError("Credit card number must be 13-19 digits long")
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    if luhn_checksum(cleaned) != 0:
        raise ValidationError("Invalid credit card number")
    
    return True


# Composite validators
def and_validator(*validators: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """
    Create validator that requires all validators to pass
    
    Args:
        *validators: Validator functions
    
    Returns:
        Combined validator function
    """
    @validator
    def _and_validator(value: Any) -> bool:
        for val in validators:
            if not val(value):
                return False
        return True
    
    return _and_validator


def or_validator(*validators: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """
    Create validator that requires at least one validator to pass
    
    Args:
        *validators: Validator functions
    
    Returns:
        Combined validator function
    """
    @validator
    def _or_validator(value: Any) -> bool:
        for val in validators:
            try:
                if val(value):
                    return True
            except ValidationError:
                continue
        raise ValidationError("None of the alternative validations passed")
    
    return _or_validator


def not_validator(validator_func: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """
    Create validator that inverts another validator
    
    Args:
        validator_func: Validator to invert
    
    Returns:
        Inverted validator function
    """
    @validator
    def _not_validator(value: Any) -> bool:
        try:
            result = validator_func(value)
            if result:
                raise ValidationError("Validation should have failed")
            return True
        except ValidationError:
            return True  # Original validator failed, so NOT validator passes
    
    return _not_validator