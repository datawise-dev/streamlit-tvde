import streamlit as st
from typing import List
from sections.hr_expenses.service import HRExpenseService
from utils.delete_helpers import generic_record_delete, generic_bulk_delete


def delete_hr_expense(expense_id):
    """Dialog to confirm deletion of an HR expense record."""
    generic_record_delete(
        entity_id=expense_id,
        entity_name="despesa RH",
        service_class=HRExpenseService,
        redirect_path="sections/hr_expenses/page.py"
    )

def bulk_delete_hr_expenses(expense_ids: List[int]):
    """Dialog to confirm deletion of multiple HR expenses."""
    generic_bulk_delete(
        record_ids=expense_ids,
        service_class=HRExpenseService,
        entity_name="despesa RH",
        session_key="hr_expenses_data_loaded"
    )
