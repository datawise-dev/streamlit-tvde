import streamlit as st
import time
from typing import Type, Callable, Optional, Any
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
