import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder


@handle_streamlit_error()
def car_form(existing_data=None):
    """Display form for car data with error handling."""

    form = FormBuilder("car_form")

    # --- Basic Car Information ---
    form.create_section("Informação do Veículo")
    form.create_field(
        key="license_plate",
        label="Matrícula",
        type="text",
        required=True,
        # Add validator
    )

    # --- Brand and Model ---
    form.create_columns(2)
    form.create_field(
        key="brand",
        label="Marca",
        type="text",
        required=True,
    )
    form.next_column()
    form.create_field(
        key="model",
        label="Modelo",
        type="text",
        required=True,
    )
    form.end_columns()

    # --- Acquisition Cost and Date ---
    form.create_columns(2)
    form.create_field(
        key="acquisition_cost",
        label="Custo de Aquisição (€)",
        type="number",
        required=True,
        min_value=0.0,
        step=100.0,
        format="%.2f",
    )
    form.next_column()
    form.create_field(
        key="acquisition_date",
        label="Data de Aquisição",
        type="date",
        required=True,
    )
    form.end_columns()

    # --- Category Information ---
    form.create_field(
        key="category",
        label="Categoria",
        type="select",
        required=True,
        options=["Economy", "Standard", "Premium", "Luxury"]
    )

    if existing_data:
        form.create_section("status", "Estado")
        form.create_field(
            key="is_active",
            label="Ativo",
            type="checkbox",
            required=False,
        )

    # Form submission
    form.create_section(None, "**Campos obrigatórios*")

    return form
