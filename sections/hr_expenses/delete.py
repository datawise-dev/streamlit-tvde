import streamlit as st
import time
from sections.hr_expenses.service import HRExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page


@st.dialog("Eliminar Despesa RH")
@handle_streamlit_error()
def hr_expense_delete(expense_id, driver_name=None):
    """Dialog to confirm deletion of an HR expense record."""
    if driver_name:
        st.write(f"Tem a certeza que deseja eliminar a despesa de **{driver_name}**?")
    else:
        st.write("Tem a certeza que deseja eliminar esta despesa RH?")

    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        btn_delete = st.button("Confirmar", type="primary", use_container_width=True)
    
    if btn_delete:
        with st.spinner("A eliminar despesa...", show_time=True):
            HRExpenseService.delete_expense(expense_id)
        st.success("Despesa RH eliminada com sucesso!")
        time.sleep(1.5)
        switch_page("sections/hr_expenses/page.py")
