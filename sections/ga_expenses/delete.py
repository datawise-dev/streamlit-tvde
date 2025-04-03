import streamlit as st
import time
from sections.ga_expenses.service import GAExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page


@st.dialog("Eliminar Despesa G&A")
@handle_streamlit_error()
def ga_expense_delete(expense_id):
    """Dialog to confirm deletion of a G&A expense record."""
    st.write("Tem a certeza que deseja eliminar esta despesa G&A?")
    st.warning("Esta ação não pode ser revertida.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        btn_delete = st.button("Confirmar", type="primary", use_container_width=True)
    
    if btn_delete:
        with st.spinner("A eliminar despesa...", show_time=True):
            GAExpenseService.delete(expense_id)
        st.success("Despesa G&A eliminada com sucesso!")
        time.sleep(1.5)
        switch_page("sections/ga_expenses/page.py")
