import streamlit as st
import time
from sections.cars.service import CarService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page


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
        btn_delete = st.button("Confirmar", type="primary", use_container_width=True)

    if btn_delete:
        with st.spinner("A eliminar veículo...", show_time=True):
            CarService.delete_car(car_id)
        st.success("Veículo eliminado com sucesso!")
        time.sleep(1.5)
        switch_page("sections/cars/page.py")
