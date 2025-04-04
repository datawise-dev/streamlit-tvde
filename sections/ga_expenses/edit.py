import streamlit as st
from sections.ga_expenses.service import GAExpenseService
from sections.ga_expenses.form import ga_expense_form
from sections.ga_expenses.delete import ga_expense_delete
from utils.page_generators import generate_edit_page
from utils.error_handlers import handle_streamlit_error

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="despesa G&A",
    entity_name_plural="despesas G&A",
    list_page_path="sections/ga_expenses/page.py",
    form_class=ga_expense_form,
    service_class=GAExpenseService,
    delete_dialog=ga_expense_delete,
    success_message="Despesa G&A atualizada com sucesso!"
)
