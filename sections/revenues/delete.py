import streamlit as st
from sections.revenues.service import RevenueService
from utils.delete_helpers import generic_record_delete

def delete_revenue(record_id):
    """Página para eliminar um registo de receita usando a função genérica."""
    generic_record_delete(
        record_id,
        "Eliminar Receita",
        service=RevenueService,
        entity_name="receita",
        return_page="sections/revenues/page.py"
    )
