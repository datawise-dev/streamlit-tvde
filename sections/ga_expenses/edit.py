import streamlit as st
from sections.ga_expenses.service import GAExpenseService
from sections.ga_expenses.form import ga_expense_form
from sections.ga_expenses.delete import delete_ga_expense
from utils.page_generators import generate_edit_page

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="despesa G&A",
    entity_name_plural="despesas G&A",
    list_page_path="sections/ga_expenses/page.py",
    form_class=ga_expense_form,
    service_class=GAExpenseService,
    delete_dialog=delete_ga_expense,
    success_message="Despesa G&A atualizada com sucesso!"
)
