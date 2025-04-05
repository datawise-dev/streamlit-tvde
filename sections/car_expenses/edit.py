import streamlit as st
from sections.car_expenses.service import CarExpenseService
from sections.car_expenses.form import car_expense_form
from sections.car_expenses.delete import car_expense_delete
from utils.page_generators import generate_edit_page

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="despesa de veículo",
    entity_name_plural="despesas de veículos",
    list_page_path="sections/car_expenses/page.py",
    form_class=car_expense_form,
    service_class=CarExpenseService,
    delete_dialog=car_expense_delete,
    success_message="Despesa de veículo atualizada com sucesso!"
)
