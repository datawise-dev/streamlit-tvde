import streamlit as st
from sections.hr_expenses.service import HRExpenseService
from utils.delete_helpers import generic_record_delete


def delete_hr_expense(expense_id):
    """Dialog to confirm deletion of an HR expense record."""
    generic_record_delete(
        entity_id=expense_id,
        entity_name="despesa RH",
        service_class=HRExpenseService,
        redirect_path="sections/hr_expenses/page.py"
    )
