import streamlit as st
from sections.car_expenses.service import CarExpenseService
from utils.delete_helpers import generic_record_delete


def delete_car_expense(expense_id):
    """Dialog to confirm deletion of a car expense record."""
    generic_record_delete(
        entity_id=expense_id,
        entity_name="despesa de veículo",
        service_class=CarExpenseService,
        redirect_path="sections/car_expenses/page.py"
    )
