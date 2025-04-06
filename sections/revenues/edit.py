import streamlit as st
from sections.revenues.service import RevenueService
from sections.revenues.form import revenue_form
from sections.ga_expenses.delete import delete_revenue
from utils.edit_helpers import generate_edit_page

generate_edit_page(
    entity_name="receita",
    entity_name_plural="receitas",
    list_page_path="sections/revenues/page.py",
    form_class=revenue_form,
    service_class=RevenueService,
    delete_dialog=delete_revenue,
    success_message="Despesa G&A atualizada com sucesso!"
)
