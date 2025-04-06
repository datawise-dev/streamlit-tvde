import streamlit as st
from typing import List
from sections.ga_expenses.service import GAExpenseService
from utils.delete_helpers import generic_delete_page, generic_bulk_delete


@st.dialog("Eliminar Despesa G&A")
def ga_expense_delete(expense_id):
    """Dialog to confirm deletion of a G&A expense record."""
    generic_delete_page(
        entity_id=expense_id,
        entity_name="despesa G&A",
        service_class=GAExpenseService,
        redirect_path="sections/ga_expenses/page.py"
    )

def delete_all_ga_expenses(expense_ids: List[int]):
    """Dialog to confirm deletion of multiple G&A expenses."""
    generic_bulk_delete(
        record_ids=expense_ids,
        service_class=GAExpenseService,
        entity_name="despesa G&A",
        session_key="ga_expenses_data_loaded"
    )
