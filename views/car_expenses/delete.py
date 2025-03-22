import streamlit as st
import time
from services.car_expense_service import CarExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page


@st.dialog("Eliminar Despesa de Veículo")
@handle_streamlit_error()
def car_expense_delete(expense_id):
    """Dialog to confirm deletion of a car expense record."""
    st.write("Tem a certeza que deseja eliminar esta despesa de veículo?")
    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            with st.spinner("A eliminar despesa...", show_time=True):
                CarExpenseService.delete_car_expense(expense_id)
            st.success("Despesa de veículo eliminada com sucesso!")
            time.sleep(1.5)
            switch_page("views/car_expenses/page.py")
