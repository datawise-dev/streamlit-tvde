import streamlit as st
import time
import pandas as pd
from typing import Type, Dict, List, Callable, Any, Optional
from utils.base_service import BaseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import check_query_params, switch_page
from utils.bulk_import import entity_bulk_import_tab


@handle_streamlit_error()
def generate_add_page(
    entity_name: str,
    form_class: Callable,
    service_class: Type[BaseService],
    list_page_path: str = None,
    enable_bulk_import: bool = True,
    entity_name_plural: str = None,
    display_formatter: Callable = None,
    success_message: str = None,
    bulk_import_help: Dict[str, str] = None  # Novo parâmetro
):
    """
    Generate a generic add page for entities, with form instance shared between tabs.
    
    Args:
        entity_name: Singular name of the entity (e.g., "car", "driver")
        form_class: Form class or function for rendering the entity form
        service_class: The service class for data operations
        enable_bulk_import: Whether to show bulk import tab
        list_page_path: Path to the entity list page
        entity_name_plural: Plural form of entity name (defaults to "{entity_name}s")
        display_formatter: Function to preprocess data after form submission
        success_message: Custom success message (defaults to "{entity_name} adicionado com sucesso!")
        bulk_import_help: Dictionary of help content for bulk import tab (keys are section titles, values are content)
    """
    # Set defaults
    if entity_name_plural is None:
        entity_name_plural = f"{entity_name}s"
    
    # Set page title
    st.title(f"Adicionar {entity_name.capitalize()}")
    
    # Create a single instance of the form to be shared between tabs
    form = form_class()
    
    # Create tabs for manual entry and bulk import (only if enabled)
    if enable_bulk_import:
        tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
        
        with tab1:
            # Use the shared form instance for the manual tab
            _render_add_form(
                entity_name, 
                form, 
                service_class, 
                display_formatter, 
                success_message
            )
        
        with tab2:
            # Definir instruções padrão se não forem fornecidas instruções personalizadas
            default_help = {"Instruções": f"Carregue um ficheiro CSV ou Excel com os dados de {entity_name_plural}."}
            
            # Usar instruções personalizadas se fornecidas, caso contrário usar padrão
            help_content = bulk_import_help if bulk_import_help is not None else default_help
            
            # Use the same form instance to get field configurations for bulk import
            entity_bulk_import_tab(
                entity_name=entity_name_plural,
                service_class=service_class,
                fields_config=form.get_field_configs(),
                help_content=help_content
            )
    else:
        # Just render the form without tabs
        _render_add_form(
            entity_name, 
            form, 
            service_class, 
            display_formatter, 
            success_message
        )
    
    # Back button
    st.page_link(list_page_path, label=f"Voltar à lista de {entity_name_plural.capitalize()}", icon="⬅️")


def _render_add_form(
    entity_name: str,
    form,  # Note: Changed from form_class to form (instance)
    service_class: Type[BaseService],
    display_formatter: Callable = None,
    success_message: str = None
):
    """Render the add form and handle submission."""
    # Use the pre-instantiated form instead of creating a new one
    submit_button, data = form.render()
    
    if submit_button:
        # Process data before saving if formatter provided
        processed_data = data
        if display_formatter and callable(display_formatter):
            processed_data = display_formatter(data)
        else:
            processed_data = _preprocess_form_data(data)
        
        try:
            with st.spinner(f"A adicionar dados..."):
                _ = service_class.insert(processed_data)
                
                # Set success message
                if success_message is None:
                    success_message = f"{entity_name.capitalize()} adicionado com sucesso!"
                
                st.success(success_message)
                time.sleep(2)
                st.rerun()  # Clear form after successful insert
        except Exception as e:
            st.error(f"Erro ao adicionar {entity_name}.")
            st.error(str(e))


@handle_streamlit_error()
def generate_edit_page(
    entity_name: str,
    form_class: Callable,
    service_class: Type[BaseService],
    list_page_path: str,
    delete_dialog: Callable = None,
    entity_name_plural: str = None,
    display_formatter: Callable = None,
    success_message: str = None,
    id_field: str = "id"
):
    """
    Generate a generic edit page for entities.
    
    Args:
        entity_name: Singular name of the entity (e.g., "car", "driver")
        form_class: Form class or function for rendering the entity form
        service_class: The service class for data operations
        list_page_path: Path to the entity list page
        delete_dialog: Function to show delete confirmation dialog
        entity_name_plural: Plural form of entity name (defaults to "{entity_name}s")
        display_formatter: Function to preprocess data after form submission
        success_message: Custom success message (defaults to "{entity_name} atualizado com sucesso!")
        id_field: Name of the ID field in query parameters (defaults to "id")
    """
    from utils.navigation import check_query_params
    
    # Set defaults
    if entity_name_plural is None:
        entity_name_plural = f"{entity_name}s"
    
    # Check query parameters and get entity data
    check_query_params()
    entity_id, existing_data = _check_edit_entity(entity_name, service_class, id_field)
    
    # Set page title
    st.title(f"Editar {entity_name.capitalize()}")
    
    # Render edit form
    form = form_class(existing_data)
    submit_button, data = form.render()
    
    if submit_button:
        # Process data before saving if formatter provided
        processed_data = data
        if display_formatter and callable(display_formatter):
            processed_data = display_formatter(data)
        else:
            processed_data = _preprocess_form_data(data)
        
        try:
            with st.spinner(f"A atualizar dados..."):
                service_class.update(entity_id, processed_data)
                
                # Set success message
                if success_message is None:
                    success_message = f"{entity_name.capitalize()} atualizado com sucesso!"
                
                st.success(success_message)
        except Exception as e:
            st.error(f"Erro ao atualizar {entity_name}.")
            st.error(str(e))
    
    # Navigation and action buttons
    _render_edit_buttons(entity_id, entity_name, list_page_path, delete_dialog)


def _render_edit_buttons(
    entity_id: int,
    entity_name: str,
    list_page_path: str,
    delete_dialog: Callable = None
):
    """Render edit page buttons (back and delete)."""
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            list_page_path,
            label=f"Voltar à lista de {entity_name.capitalize()}s",
            icon="⬅️",
            use_container_width=True,
        )
    
    if delete_dialog and callable(delete_dialog):
        with col2:
            if st.button(
                f"Eliminar {entity_name.capitalize()}",
                type="tertiary",
                icon="🗑️",
                use_container_width=True,
            ):
                delete_dialog(entity_id)


def _check_edit_entity(
    entity_name: str,
    service_class: Type[BaseService],
    id_field: str = "id"
) -> tuple:
    """
    Validate query parameters for ID and fetch existing entity data.

    Args:
        entity_name: Human-readable name of the entity (e.g., "veículo", "motorista")
        service_class: The service class responsible for data operations
        id_field: Name of the ID field in query parameters

    Returns:
        Tuple containing (entity_id, existing_data)

    Raises:
        SystemExit: If ID is missing, invalid, or entity is not found (via st.stop())
    """
    # Check if ID is in query parameters
    if id_field not in st.query_params:
        st.warning(f"ID do {entity_name} em falta")
        st.stop()

    try:
        # Parse ID from query parameters
        entity_id = int(st.query_params[id_field])

        # Get entity data
        existing_data = service_class.get(entity_id)

        # Check if entity exists
        if not existing_data:
            st.error(f"{entity_name.capitalize()} não encontrado.")
            st.stop()

        return entity_id, existing_data

    except (ValueError, TypeError):
        st.error(f"ID de {entity_name} inválido.")
        st.stop()


def _preprocess_form_data(data):
    """Process form data before sending to service layer."""
    processed_data = data.copy()
    
    # Convert date objects to strings
    for key, value in processed_data.items():
        if hasattr(value, 'strftime'):  # Is a date object
            processed_data[key] = value.strftime("%Y-%m-%d")
    
    return processed_data
