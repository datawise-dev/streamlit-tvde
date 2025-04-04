import streamlit as st
from sections.car_expenses.service import CarExpenseService
from utils.delete_helpers import generic_delete_page


@st.dialog("Eliminar Despesa de Veículo")
def car_expense_delete(expense_id):
    """Dialog to confirm deletion of a car expense record."""
    generic_delete_page(
        entity_id=expense_id,
        entity_name="despesa de veículo",
        service_class=CarExpenseService,
        redirect_path="sections/car_expenses/page.py"
    )
