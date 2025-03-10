import streamlit as st
import time
from services.ga_expense_service import GAExpenseService
from utils.error_handlers import handle_streamlit_error

@st.dialog("Delete G&A Expense")
@handle_streamlit_error()
def ga_expense_delete(expense_id):
    """Dialog to confirm deletion of a G&A expense record."""
    st.write("Are you sure you want to delete this G&A expense?")
    st.warning("This action cannot be undone.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirm", type="primary", use_container_width=True):
            with st.spinner("Deleting expense...", show_time=True):
                GAExpenseService.delete_ga_expense(expense_id)
            st.success("G&A expense deleted successfully!")
            time.sleep(1.5)
            st.switch_page("ga_expenses")
