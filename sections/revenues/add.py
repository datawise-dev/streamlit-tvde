import streamlit as st
from sections.revenues.service import RevenueService
from sections.revenues.form import revenue_form
from utils.page_generators import generate_add_page


generate_add_page(
    entity_name="receita",
    entity_name_plural="receitas",
    list_page_path="sections/revenues/page.py",
    form_class=revenue_form,
    service_class=RevenueService,
    success_message="Receita adicionada com sucesso!"
)

