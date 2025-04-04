import streamlit as st
from sections.ga_expenses.service import GAExpenseService
from utils.delete_helpers import generic_delete_page


@st.dialog("Eliminar Despesa G&A")
def ga_expense_delete(expense_id):
    """Dialog to confirm deletion of a G&A expense record."""
    generic_delete_page(
        entity_id=expense_id,
        entity_name="despesa G&A",
        service_class=GAExpenseService,
        redirect_path="sections/ga_expenses/page.py"
    )
