import streamlit as st
from typing import List
from sections.revenues.service import RevenueService
from utils.delete_helpers import generic_record_delete, generic_bulk_delete

def delete_revenue(record_id):
    """Página para eliminar um registo de receita usando a função genérica."""
    generic_record_delete(
        record_id,
        "Eliminar Receita",
        service=RevenueService,
        entity_name="receita",
        return_page="sections/revenues/page.py"
    )

def bulk_delete_revenues(record_ids: List[int]):
    """Dialog to confirm deletion of multiple Revenue records."""
    generic_bulk_delete(
        record_ids=record_ids,
        service_class=RevenueService,
        entity_name="receita",
        session_key="revenues_data_loaded"
    )
