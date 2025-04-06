import streamlit as st
from sections.hr_expenses.service import HRExpenseService
from utils.delete_helpers import generic_delete_page


@st.dialog("Eliminar Despesa RH")
def hr_expense_delete(expense_id):
    """Dialog to confirm deletion of an HR expense record."""
    generic_delete_page(
        entity_id=expense_id,
        entity_name="despesa RH",
        service_class=HRExpenseService,
        redirect_path="sections/hr_expenses/page.py"
    )
