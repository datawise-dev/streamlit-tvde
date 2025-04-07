from typing import Dict, List, Tuple, Callable, Any, Optional, Union
from datetime import date, datetime
import re

# Type definitions for better code clarity
ValidationResult = Tuple[bool, str]  # (is_valid, error_message)
Validator = Callable[[Any, str], ValidationResult]  # Function that validates a value
FieldValidator = Tuple[str, List[Validator]]  # (field_name, list_of_validators)


def validate_required(value: Any) -> ValidationResult:
    """
    Validates that a value is not empty or None.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return False, "Este campo é obrigatório."
    return True, ""


def validate_min_length(min_length: int) -> Validator:
    """
    Creates a validator that checks minimum string length.
    
    Args:
        min_length: The minimum allowed length
        
    Returns:
        Validator function
    """
    def validator(value: str) -> ValidationResult:
        if value is not None and len(str(value)) < min_length:
            return False, f"Deve ter pelo menos {min_length} caracteres."
        return True, ""
    return validator


def validate_max_length(max_length: int) -> Validator:
    """
    Creates a validator that checks maximum string length.
    
    Args:
        max_length: The maximum allowed length
        
    Returns:
        Validator function
    """
    def validator(value: str) -> ValidationResult:
        if value is not None and len(str(value)) > max_length:
            return False, f"Não pode ter mais de {max_length} caracteres."
        return True, ""
    return validator


def validate_numeric(value: Any) -> ValidationResult:
    """
    Validates that a value is numeric (int or float).
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is not None:
        try:
            float(value)
        except (ValueError, TypeError):
            return False, "Deve ser um valor numérico."
    return True, ""


def validate_min_value(min_value: Union[int, float]) -> Validator:
    """
    Creates a validator that checks minimum numeric value.
    
    Args:
        min_value: The minimum allowed value
        
    Returns:
        Validator function
    """
    def validator(value: Any) -> ValidationResult:
        if value is not None:
            try:
                if float(value) < min_value:
                    return False, f"Deve ser pelo menos {min_value}."
            except (ValueError, TypeError):
                pass  # Let validate_numeric handle type errors
        return True, ""
    return validator


def validate_min_value(min_value: Union[int, float]) -> Validator:
    """
    Creates a validator that checks minimum numeric value.
    
    Args:
        min_value: The minimum allowed value
        
    Returns:
        Validator function
    """
    def validator(value: Any) -> ValidationResult:
        if value is not None:
            try:
                if float(value) < min_value:
                    return False, f"Deve ser pelo menos {min_value}."
            except (ValueError, TypeError):
                pass  # Let validate_numeric handle type errors
        return True, ""
    return validator


def validate_max_value(max_value: Union[int, float]) -> Validator:
    """
    Creates a validator that checks maximum numeric value.
    
    Args:
        max_value: The maximum allowed value
        
    Returns:
        Validator function
    """
    def validator(value: Any) -> ValidationResult:
        if value is not None:
            try:
                if float(value) > max_value:
                    return False, f"Não pode ser maior que {max_value}."
            except (ValueError, TypeError):
                pass  # Let validate_numeric handle type errors
        return True, ""
    return validator


def validate_date_format(value: Any) -> ValidationResult:
    """
    Validates that a value is a valid date.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is not None and not isinstance(value, (date, datetime)):
        try:
            if isinstance(value, str):
                datetime.strptime(value, "%Y-%m-%d")
            else:
                return False, "Deve ser uma data válida no formato YYYY-MM-DD."
        except ValueError:
            return False, "Deve ser uma data válida no formato YYYY-MM-DD."
    return True, ""


def validate_regex(pattern: str, message: str) -> Validator:
    """
    Creates a validator that checks if value matches a regex pattern.
    
    Args:
        pattern: Regular expression pattern to match
        message: Custom error message
        
    Returns:
        Validator function
    """
    def validator(value: str) -> ValidationResult:
        if value is not None and not re.match(pattern, str(value)):
            return False, message
        return True, ""
    return validator


def validate_options(valid_values: List[Any], allow_default: bool = False, default_value: Any = None) -> callable:
    """
    Creates a validator that checks if a value is in a list of valid values.
    
    Args:
        valid_values: List of allowed values
        allow_default: Whether to allow a default value not in the list
        default_value: The default value to allow (typically None)
        
    Returns:
        A validator function
    """
    def validator(value: Any, field_name: str = "") -> Tuple[bool, str]:
        # Check if value is the allowed default
        if allow_default and value == default_value:
            return True, ""
            
        # Check if value is in valid values
        if value in valid_values:
            return True, ""
        
        # Value is invalid - create readable error message
        values_str = ", ".join(map(str, valid_values))
        return False, f"Must be one of: {values_str}"
    
    return validator


def validate_boolean(value: Any, field_name: str = "") -> Tuple[bool, str]:
    """
    Validates that a value is a boolean or can be interpreted as a boolean.
    
    Args:
        value: The value to validate
        field_name: Name of the field (for error message)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if it's already a boolean
    if isinstance(value, bool):
        return True, ""
    
    # Check if it's a string that can be interpreted as boolean
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ['true', 'false', 'yes', 'no', '1', '0', 'on', 'off']:
            return True, ""
    
    # Check if it's an integer that can be interpreted as boolean
    if isinstance(value, int) and value in [0, 1]:
        return True, ""
    
    # Invalid boolean value
    return False, "Must be a boolean value"


def validate_license_plate(value: str) -> ValidationResult:
    """
    Validates that a value is a valid Portuguese license plate.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Portuguese license plate format: XX-XX-XX or XX-XX-XX (newer format)
    pattern = r'^[A-Z0-9]{2}-[A-Z0-9]{2}-[A-Z0-9]{2}$'
    if value is not None and not re.match(pattern, str(value)):
        return False, "Deve ser uma matrícula válida no formato XX-XX-XX."
    return True, ""


def validate_nif(value: str) -> ValidationResult:
    """
    Validates that a value is a valid Portuguese NIF (tax number).
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or value.strip() == "":
        return True, ""  # Empty is allowed, use required validator if needed
        
    # Check if it's a 9-digit number
    if not re.match(r'^\d{9}$', str(value)):
        return False, "Deve ser um NIF válido (9 dígitos)."
        
    # Validate the check digit
    try:
        nif = [int(digit) for digit in value]
        check_sum = sum(nif[i] * (9 - i) for i in range(8))
        check_digit = 11 - (check_sum % 11)
        if check_digit >= 10:
            check_digit = 0
            
        if check_digit != nif[8]:
            return False, "Formato de NIF inválido."
    except (ValueError, IndexError):
        return False, "Formato de NIF inválido."
        
    return True, ""


def validate_postal_code(value: str) -> ValidationResult:
    """
    Validates that a value is a valid Portuguese postal code.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or value.strip() == "":
        return True, ""  # Empty is allowed, use required validator if needed
        
    # Portuguese postal code format: XXXX-XXX
    if not re.match(r'^\d{4}-\d{3}$', str(value)):
        return False, "Deve ser um código postal válido no formato XXXX-XXX."
    return True, ""


def validate_date_range(start_field: str, end_field: str) -> Callable[[Dict], ValidationResult]:
    """
    Creates a validator that checks that a start date is before or equal to an end date.
    
    Args:
        start_field: Field name of the start date
        end_field: Field name of the end date
        
    Returns:
        Function that validates a dictionary of values
    """
    def validator(data: Dict) -> ValidationResult:
        start = data.get(start_field)
        end = data.get(end_field)
        
        if start is None or end is None:
            return True, ""  # Skip validation if either date is missing
            
        # Convert string dates to date objects if needed
        if isinstance(start, str):
            try:
                start = datetime.strptime(start, "%Y-%m-%d").date()
            except ValueError:
                return False, f"A data de início é inválida."
                
        if isinstance(end, str):
            try:
                end = datetime.strptime(end, "%Y-%m-%d").date()
            except ValueError:
                return False, f"A data de fim é inválida."
                
        if start > end:
            return False, f"A data de início não pode ser posterior à data de fim."
            
        return True, ""
    return validator


def validate_data(data: Dict, field_validators: List[FieldValidator], 
                  cross_validators: List[Callable[[Dict], ValidationResult]] = None) -> List[str]:
    """
    Validates a dictionary of data against multiple field validators and cross-field validators.
    
    Args:
        data: Dictionary of data to validate
        field_validators: List of (field_name, validators_list) tuples
        cross_validators: List of functions that validate across multiple fields
        
    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    
    # Field validation
    for field_name, validators in field_validators:
        value = data.get(field_name)
        
        for validator in validators:
            is_valid, error_message = validator(value)
            if not is_valid:
                errors.append(error_message)
                break  # Stop validating this field after first error
    
    # Cross-field validation
    if cross_validators:
        for validator in cross_validators:
            is_valid, error_message = validator(data)
            if not is_valid:
                errors.append(error_message)
    
    return errors
