import streamlit as st
import time
from typing import Type, List, Optional
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from utils.base_service import BaseService


@handle_streamlit_error()
def generic_delete_page(
    entity_id: int,
    entity_name: str,
    service_class: Type[BaseService],
    redirect_path: Optional[str] = None,
    success_message: Optional[str] = None,
    redirect_delay: float = 1.5,
) -> None:
    """
    Generic dialog to confirm deletion of a record.
    
    Args:
        entity_id: ID of the entity to delete
        entity_name: Type of entity (e.g., "despesa G&A", "motorista")
        service_class: The service class responsible for deletion
        redirect_path: Path to redirect after successful deletion
        success_message: Custom success message
        redirect_delay: Delay in seconds before redirecting
    """
    # Personalized confirmation message
    st.write(f"Tem a certeza que deseja eliminar este {entity_name.capitalize()}?")
    
    st.warning("Esta ação não pode ser revertida.")
    
    # Confirmation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        btn_delete = st.button("Confirmar", type="primary", use_container_width=True)
    
    if btn_delete:
        with st.spinner(f"A eliminar {entity_name}...", show_time=True):
            service_class.delete(entity_id)
        
        # Show success message
        if not success_message:
            success_message = f"{entity_name.capitalize()} eliminado com sucesso!"

        st.success(success_message)
        
        # Redirect to the specified path
        if redirect_path:
            time.sleep(redirect_delay)
            switch_page(redirect_path)


@st.dialog("Eliminar Registos em Massa")
def generic_bulk_delete(
    record_ids: List[int],
    service_class: Type[BaseService],
    entity_name: str,
    session_key: str = None
):
    """
    Generic dialog to confirm deletion of multiple records.
    
    Args:
        record_ids: List of record IDs to delete
        service_class: The service class responsible for deletion
        entity_name: Name of the entities to be deleted (singular)
        session_key: Optional session state key to clear for refreshing data
    """
    count = len(record_ids)
    entity_plural = f"{entity_name}s" if not entity_name.endswith('s') else entity_name
    
    st.write(f"Tem a certeza que deseja eliminar {count} {entity_plural}?")
    st.warning("Esta ação não pode ser revertida.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        confirm_button = st.button("Confirmar", type="primary", use_container_width=True)
    
    if confirm_button:
        with st.spinner(f"A eliminar {count} {entity_plural}...", show_time=True):
            service_class.delete_many(record_ids)
        
        st.success(f"{count} {entity_plural} eliminados com sucesso!")
        
        # Clear session state if provided to force data reload
        if session_key and session_key in st.session_state:
            del st.session_state[session_key]
            
        st.rerun()
