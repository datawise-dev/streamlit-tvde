import streamlit as st
import time
from services.revenue_service import RevenueService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page


@st.dialog("Eliminar Receita")
@handle_streamlit_error()
def delete_revenue_records(revenue_id):
    """Dialog to confirm deletion of a revenue record."""
    st.write("Tem a certeza que deseja eliminar este registo de receita?")
    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        btn_delete = st.button("Confirmar", type="primary", use_container_width=True)

    if btn_delete:
        with st.spinner("A eliminar registo...", show_time=True):
            try:
                # Se o RevenueService não tiver um método "delete" específico,
                # pode-se usar delete_records com um único ID numa lista
                RevenueService.delete_records([revenue_id])
                st.success("Registo eliminado com sucesso!")
                time.sleep(1.5)
                switch_page("views/revenues/page.py")
            except Exception as e:
                st.error(f"Erro ao eliminar registo: {str(e)}")
                time.sleep(3)
                st.rerun()
