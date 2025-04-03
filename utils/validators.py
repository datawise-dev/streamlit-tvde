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


# Example validators for specific entities
def get_revenue_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for revenue data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('start_date', [validate_required, validate_date_format]),
        ('end_date', [validate_required, validate_date_format]),
        ('driver_name', [validate_required]),
        ('license_plate', [validate_required, validate_license_plate]),
        ('platform', [validate_required]),
        ('gross_revenue', [validate_required, validate_numeric, validate_min_value(0)]),
        ('commission_percentage', [validate_numeric, validate_min_value(0), validate_max_value(100)]),
        ('num_travels', [validate_numeric, validate_min_value(0)]),
        ('num_kilometers', [validate_numeric, validate_min_value(0)])
    ]
    
    cross_validators = [
        validate_date_range('start_date', 'end_date')
    ]
    
    return field_validators, cross_validators


def get_driver_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for driver data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('display_name', [validate_required]),
        ('first_name', [validate_required]),
        ('last_name', [validate_required]),
        ('nif', [validate_required, validate_nif]),
        ('postal_code', [validate_postal_code])
    ]
    
    cross_validators = []
    
    return field_validators, cross_validators


def get_car_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for car data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('license_plate', [validate_required, validate_license_plate]),
        ('brand', [validate_required]),
        ('model', [validate_required]),
        ('acquisition_cost', [validate_required, validate_numeric, validate_min_value(0)]),
        ('acquisition_date', [validate_required, validate_date_format]),
        ('category', [validate_required])
    ]
    
    cross_validators = []
    
    return field_validators, cross_validators


def get_hr_expense_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for HR expense data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('driver_id', [validate_required, validate_numeric]),
        ('start_date', [validate_required, validate_date_format]),
        ('end_date', [validate_required, validate_date_format]),
        ('payment_date', [validate_required, validate_date_format]),
        ('base_salary', [validate_required, validate_numeric, validate_min_value(0)]),
        ('working_days', [validate_required, validate_numeric, validate_min_value(0)]),
        ('meal_allowance_per_day', [validate_required, validate_numeric, validate_min_value(0)])
    ]
    
    cross_validators = [
        validate_date_range('start_date', 'end_date')
    ]
    
    return field_validators, cross_validators


def get_car_expense_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for car expense data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('car_id', [validate_required, validate_numeric]),
        ('expense_type', [validate_required]),
        ('start_date', [validate_required, validate_date_format]),
        ('end_date', [validate_date_format]),  # Not required
        ('amount', [validate_required, validate_numeric, validate_min_value(0)]),
        ('description', [validate_max_length(500)])  # Not required, but with max length
    ]
    
    # Cross-field validators
    cross_validators = []
    
    # Add date range validator only for credit expenses
    def validate_credit_date_range(data: Dict) -> ValidationResult:
        if data.get('expense_type') == 'Credit' and data.get('end_date') is None:
            return False, "End date is required for Credit expenses"
        return True, ""
    
    # Add validator for date range
    cross_validators.append(validate_date_range('start_date', 'end_date'))
    
    # Add validator for credit expense date requirements
    cross_validators.append(validate_credit_date_range)
    
    return field_validators, cross_validators


def get_ga_expense_validators() -> Tuple[List[FieldValidator], List[Callable]]:
    """
    Get validators for G&A expense data.
    
    Returns:
        Tuple of (field_validators, cross_validators)
    """
    field_validators = [
        ('expense_type', [validate_required]),
        ('start_date', [validate_required, validate_date_format]),
        ('end_date', [validate_date_format]),  # Not required
        ('payment_date', [validate_date_format]),  # Not required
        ('amount', [validate_required, validate_numeric, validate_min_value(0)]),
        ('vat', [validate_numeric, validate_min_value(0), validate_max_value(100)]),  # VAT percentage 0-100
        ('description', [validate_max_length(500)])  # Not required, but with max length
    ]
    
    # Cross-field validators
    cross_validators = [
        validate_date_range('start_date', 'end_date')
    ]
    
    return field_validators, cross_validators
