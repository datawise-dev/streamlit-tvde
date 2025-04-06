import streamlit as st
from sections.hr_expenses.service import HRExpenseService
from sections.hr_expenses.form import hr_expense_form
from sections.hr_expenses.delete import delete_hr_expense
from utils.page_generators import generate_edit_page
from utils.error_handlers import handle_streamlit_error

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="despesa RH",
    entity_name_plural="despesas RH",
    list_page_path="sections/hr_expenses/page.py",
    form_class=hr_expense_form,
    service_class=HRExpenseService,
    delete_dialog=delete_hr_expense,
    success_message="Despesa RH atualizada com sucesso!"
)
