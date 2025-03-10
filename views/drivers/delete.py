import streamlit as st
import time
from services.driver_service import DriverService
from utils.error_handlers import handle_streamlit_error


@st.dialog("Eliminar Motorista")
@handle_streamlit_error()
def driver_delete(driver_id, driver_name):
    """Dialog to confirm driver deletion."""
    st.write(f"Tem a certeza que deseja eliminar o motorista **{driver_name}**?")
    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            with st.spinner("A eliminar motorista...", show_time=True):
                DriverService.delete_driver(driver_id)
            st.success("Motorista eliminado com sucesso!")
            time.sleep(1.5)
            st.page_switch("drivers")
