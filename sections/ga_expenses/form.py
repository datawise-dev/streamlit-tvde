import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder
from datetime import date

# Dicionário para mapear entre português e inglês os tipos de despesa
expense_type_options = [
    "Renda",
    "Licenças - RNAVT",
    "Seguro",
    "Eletricidade",
    "Água",
    "Outros"
]


@handle_streamlit_error()
def ga_expense_form(existing_data=None):
    """Display form for G&A expense data with error handling using FormBuilder."""

    form = FormBuilder("ga_expense_form")

    # --- Basic Expense Information ---
    form.create_section("Informação da Despesa G&A")

    # Map back to English for storage
    form.create_field(
        key="expense_type",
        label="Tipo de Despesa",
        type="select",
        required=True,
        options=expense_type_options,
        help="Tipo de despesa G&A"
    )

    # Date information
    form.create_columns(2)
    form.create_field(
        key="start_date",
        label="Data de Início",
        type="date",
        required=True,
        help="Quando a despesa ocorreu ou começou"
    )
    
    form.create_field(
        key="end_date",
        label="Data de Fim",
        type="date",
        help="Data de fim (se aplicável, por exemplo, para despesas baseadas em períodos)"
    )
    form.end_columns()
    
    # Payment date
    form.create_field(
        key="payment_date",
        label="Data de Pagamento",
        type="date",
        help="Data em que a despesa foi paga"
    )

    # Amount and VAT
    form.create_columns(2)
    form.create_field(
        key="amount",
        label="Montante (€)",
        type="number",
        required=True,
        min_value=0.0,
        step=0.01,
        format="%.2f",
        help="Valor da despesa em euros"
    )
    
    form.create_field(
        key="vat",
        label="IVA (%)",
        type="number",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        default=23.0,
        help="Percentagem de IVA aplicada a esta despesa"
    )
    form.end_columns()
    
    # Description
    form.create_field(
        key="description",
        label="Descrição / Comentários",
        type="textarea",
        help="Detalhes adicionais sobre a despesa"
    )
    
    if existing_data:
        for key, value in existing_data.items():
            form.data[key] = value

    # Required fields notice
    form.create_section(None, "**Campos obrigatórios*")

    return form
