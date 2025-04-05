import streamlit as st
import time
from typing import Dict, List, Callable, Any, Type, Tuple
from utils.base_service import BaseService
from utils.validators import (
    validate_required,
    validate_numeric,
    validate_min_value,
    validate_max_value,
    validate_date_format,
    validate_min_length,
    validate_max_length,
    validate_regex,
    validate_options,
    validate_boolean,
)


def create_record_validator(
    fields_config: List[Dict[str, Any]] = None,
) -> Callable:
    """
    Creates a record validator function.

    Args:
        fields_config: List of field configurations with constraints and validation rules

    Returns:
        A validator function that takes a record and returns (is_valid, error_messages)
    """
    if not fields_config:
        fields_config = []

    def validator(record: Dict) -> Tuple[bool, List[str]]:
        """
        Validates a record against field configurations.

        Args:
            record: The data record to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for field_def in fields_config:
            field = field_def.get("key")
            display_name = field_def.get("label")
            required = field_def.get("required", False)
            field_type = field_def.get("type", "text")
            custom_validator = field_def.get("validator")
            value = record.get(field)
            field_validators = []

            # Required validator first
            # Skip other validations if value is None (for non-required fields)
            if required:
                # Run only required validator (if present)
                is_valid, error_msg = validate_required(value)
                if not is_valid:
                    errors.append(f"{display_name}: {error_msg}")
                continue

            # Type-specific validations
            if field_type == "number":
                field_validators.append(validate_numeric)

                if "min_value" in field_def:
                    field_validators.append(validate_min_value(field_def["min_value"]))

                if "max_value" in field_def:
                    field_validators.append(validate_max_value(field_def["max_value"]))

            elif field_type == "date":
                field_validators.append(validate_date_format)

            elif field_type == "text":
                if "min_length" in field_def:
                    field_validators.append(
                        validate_min_length(field_def["min_length"])
                    )

                if "max_length" in field_def:
                    field_validators.append(
                        validate_max_length(field_def["max_length"])
                    )

                if "pattern" in field_def:
                    pattern = field_def["pattern"]
                    pattern_msg = field_def.get(
                        "pattern_message", "Must match the required format."
                    )
                    field_validators.append(validate_regex(pattern, pattern_msg))

            elif field_type == "select":
                options = field_def.get("options", [])
                default_value = field_def.get("default", None)
                field_validators.append(
                    validate_options(options, default_value=default_value)
                )

            elif field_type in ["checkbox", "toggle"]:
                field_validators.append(validate_boolean)
            
            if custom_validator:
                field_validators.append(custom_validator)

            # Execute all validators for this field
            for validator_func in field_validators:
                is_valid, error_msg = validator_func(value)
                if not is_valid:
                    # Ensure display_name is included in the error message
                    errors.append(f"{display_name}: {error_msg}")
                    # Break on first error for this field
                    break

        # Use the service class's validate method
        return len(errors) == 0, errors

    return validator


def create_generic_uploader(service_class: Type[BaseService]) -> Callable:
    """
    Creates a generic uploader function for entity records based on the service class's insert method.

    Args:
        service_class: The service class that has an insert method

    Returns:
        An uploader function that takes a list of records and returns True on success
    """

    def uploader(records: List[Dict]) -> bool:

        # Process each record individually
        success_count = 0
        errors = []

        for record in records:
            try:
                service_class.insert(record)
                success_count += 1
            except Exception as e:
                errors.append(str(e))

        if errors:
            if len(errors) == len(records):
                raise Exception(
                    f"Failed to import all records. First error: {errors[0]}"
                )
            else:
                raise Exception(
                    f"Imported {success_count} out of {len(records)} records. Error: {errors[0]}"
                )

        return True

    return uploader


def create_(data, entity_name, class_service, edit=False):
    try:
        with st.spinner("A adicionar dados...", show_time=True):
            class_service.insert(data)
        st.success(f"{entity_name.capitalize()} {'alterado' if edit else 'adicionado'} com sucesso!")
        time.sleep(2)
        # Clear form after successful insert
        st.rerun()
    except Exception as e:
        error_msg = f"Não foi possível {'alterar' if edit else 'adicionar'} o {entity_name}. "
        error_msg += "Verifique os dados e tente novamente."
        st.error(error_msg)
        st.error(str(e))