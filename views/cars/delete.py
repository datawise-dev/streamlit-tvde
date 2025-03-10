import streamlit as st
import time
from services.car_service import CarService
from utils.error_handlers import handle_streamlit_error


@st.dialog("Eliminar Veículo")
@handle_streamlit_error()
def car_delete(car_id, license_plate):
    """Dialog to confirm car deletion."""
    st.write(
        f"Tem a certeza que deseja eliminar o veículo com matrícula **{license_plate}**?"
    )
    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            with st.spinner("A eliminar veículo...", show_time=True):
                CarService.delete_car(car_id)
            st.success("Veículo eliminado com sucesso!")
            time.sleep(1.5)
            st.page_switch("views/cars/page.py")
