import streamlit as st
from typing import Dict, List, Callable, Any, Type, Tuple
import logging
from utils.bulk_import import bulk_import_component
from services.base_service import BaseService

logger = logging.getLogger(__name__)

def create_generic_validator(
    service_class: Type[BaseService],
    field_constraints: Dict[str, Dict[str, Any]] = None,
) -> Callable:
    """
    Creates a generic validator function for entity records based on the service class's validate method.
    
    Args:
        service_class: The service class that has a validate method
        field_constraints: Additional constraints for specific fields (e.g., valid categories)
        
    Returns:
        A validator function that takes a record and returns (is_valid, error_messages)
    """
    def validator(record: Dict) -> Tuple[bool, List[str]]:
        # Apply additional field constraints if provided
        if field_constraints:
            for field, constraints in field_constraints.items():
                if field in record and record[field] is not None:
                    if 'valid_values' in constraints and record[field] not in constraints['valid_values']:
                        return False, [f"{field} must be one of: {', '.join(constraints['valid_values'])}"]
        
        # Add default values for missing fields if needed
        if hasattr(service_class, 'DEFAULT_VALUES'):
            for field, value in service_class.DEFAULT_VALUES.items():
                if field not in record:
                    record[field] = value
        
        # Use the service class's validate method
        return service_class.validate(record)
    
    return validator


def create_generic_uploader(service_class: Type[BaseService], insert_method_name: str) -> Callable:
    """
    Creates a generic uploader function for entity records based on the service class's insert method.
    
    Args:
        service_class: The service class that has an insert method
        insert_method_name: Name of the insert method to use (e.g., 'insert_car', 'insert_driver')
        
    Returns:
        An uploader function that takes a list of records and returns True on success
    """
    def uploader(records: List[Dict]) -> bool:
        # Get the insert method
        insert_method = getattr(service_class, insert_method_name)
        
        # Process each record individually
        success_count = 0
        errors = []
        
        for record in records:
            try:
                insert_method(record)
                success_count += 1
            except Exception as e:
                errors.append(str(e))
        
        if errors:
            if len(errors) == len(records):
                raise Exception(f"Failed to import all records. First error: {errors[0]}")
            else:
                raise Exception(f"Imported {success_count} out of {len(records)} records. Error: {errors[0]}")
        
        return True
    
    return uploader


def entity_bulk_import_tab(
    entity_name: str,
    service_class: Type[BaseService],
    standard_fields: List[str],
    field_display_names: Dict[str, str],
    field_constraints: Dict[str, Dict[str, Any]] = None,
    insert_method_name: str = None,
    help_content: Dict[str, str] = None
):
    """
    Renders a bulk import tab for an entity type.
    
    Args:
        entity_name: Name of the entity (e.g., "cars", "drivers")
        service_class: The service class for the entity
        standard_fields: List of standard field names
        field_display_names: Dictionary mapping field names to display names
        field_constraints: Additional constraints for specific fields
        insert_method_name: Name of the insert method (defaults to "insert_{entity_name[:-1]}")
        help_content: Optional help content to display in expanders
    """
    # Default insert method name if not provided
    if insert_method_name is None:
        # Convert plural to singular (e.g., "cars" -> "car")
        entity_singular = entity_name[:-1] if entity_name.endswith('s') else entity_name
        insert_method_name = f"insert_{entity_singular}"
    
    # Create validator and uploader functions
    validator = create_generic_validator(service_class, field_constraints)
    uploader = create_generic_uploader(service_class, insert_method_name)
    
    # Use the bulk import component
    with st.container(border=1):
        bulk_import_component(
            entity_name=entity_name,
            standard_fields=standard_fields,
            validation_function=validator,
            upload_function=uploader,
            field_display_names=field_display_names
        )
    
    # Display help content if provided
    if help_content:
        for title, content in help_content.items():
            with st.expander(title):
                st.info(content)
