import streamlit as st
from typing import Type, Dict, Any, Optional, Tuple
from utils.error_handlers import handle_streamlit_error
from utils.base_service import BaseService


def check_edit_entity(
    entity_name: str,
    service_class: Type[BaseService],
) -> Tuple[int, Dict[str, Any]]:
    """
    Generic function to validate query parameters for ID and fetch existing entity data.

    Args:
        entity_name: Human-readable name of the entity (e.g., "veículo", "motorista")
        service_class: The service class responsible for data operations

    Returns:
        Tuple containing (entity_id, existing_data)

    Raises:
        SystemExit: If ID is missing, invalid, or entity is not found (via st.stop())
    """
    # Check if ID is in query parameters
    if "id" not in st.query_params:
        st.warning(f"ID do {entity_name} em falta")
        st.stop()

    try:
        # Parse ID from query parameters
        entity_id = int(st.query_params["id"])

        # Get entity data using the provided method
        existing_data = service_class.get(entity_id)

        # Check if entity exists
        if not existing_data:
            st.error(f"{entity_name.capitalize()} não encontrado.")
            st.stop()

        return entity_id, existing_data

    except (ValueError, TypeError):
        st.error(f"ID de {entity_name} inválido.")
        st.stop()


def edit_form_bottom(
    entity_id: str,
    entity_name: str,
    redirect_path: Optional[str],
    delete_dialog,
):
    # Botões de navegação e ações adicionais
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            redirect_path,
            label=f"Voltar à lista de {entity_name.capitalize()}",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            f"Eliminar {entity_name.capitalize()}",
            type="tertiary",
            icon="🗑️",
            use_container_width=True,
        ):
            delete_dialog(entity_id)
