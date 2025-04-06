import streamlit as st
from typing import List
from sections.car_expenses.service import CarExpenseService
from utils.delete_helpers import generic_record_delete, generic_bulk_delete


def delete_car_expense(expense_id):
    """Dialog to confirm deletion of a car expense record."""
    generic_record_delete(
        entity_id=expense_id,
        entity_name="despesa de veículo",
        service_class=CarExpenseService,
        redirect_path="sections/car_expenses/page.py"
    )

def bulk_delete_car_expenses(expense_ids: List[int]):
    """Dialog to confirm deletion of multiple car expenses."""
    generic_bulk_delete(
        record_ids=expense_ids,
        service_class=CarExpenseService,
        entity_name="despesa de veículo",
        session_key="car_expenses_data_loaded"
    )
