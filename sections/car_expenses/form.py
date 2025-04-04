import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder
from datetime import date
from sections.cars.service import CarService

# Dictionary to map between Portuguese and English expense types
car_expense_types = [
    "Crédito",
    "Combustível",
    "Portagens",
    "Reparações",
    "Lavagem",
]


@handle_streamlit_error()
def car_expense_form(existing_data=None):
    """Display form for car expense data with error handling using FormBuilder."""

    form = FormBuilder("car_expense_form")

    # --- Basic Expense Information ---
    form.create_section("Informação da Despesa de Veículo")

    # Car selection
    try:
        cars = CarService.get_all_license_plates()
        if not cars:
            car_options = {}
            st.warning("Não existem veículos disponíveis no sistema")
        else:
            # Create a dictionary for car selection
            car_options = {
                car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars
            }

        form.create_field(
            key="car_id",
            label="Veículo",
            type="select",
            required=True,
            options=list(car_options.keys()) if car_options else [],
            format_func=lambda x: car_options.get(x, "Selecione um veículo"),
            help="Selecione o veículo para esta despesa"
        )
    except Exception as e:
        st.error(f"Erro ao carregar veículos: {str(e)}")

    # Expense type and dates
    form.create_columns(2)
    
    form.create_field(
        key="expense_type",
        label="Tipo de Despesa",
        type="select",
        required=True,
        options=car_expense_types,
        help="Tipo de despesa de veículo"
    )
    
    form.create_field(
        key="start_date",
        label="Data de Início",
        type="date",
        required=True,
        help="Quando a despesa ocorreu ou começou"
    )
    form.end_columns()
    
    form.create_columns(2)
    form.create_field(
        key="end_date",
        label="Data de Fim",
        type="date",
        help="Data de fim (obrigatória para despesas de crédito)"
    )
    
    # Amount and VAT
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
    form.end_columns()
    
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
    
    # Description
    form.create_field(
        key="description",
        label="Descrição / Comentários",
        type="textarea",
        help="Detalhes adicionais sobre a despesa"
    )
    
    if existing_data:
        for key, value in existing_data.items():
            if key in form.data and key != "expense_type":
                form.data[key] = value
        
        # Handle expense_type separately to use the English value
        if "expense_type" in existing_data:
            form.data["expense_type"] = existing_data["expense_type"]
    else:
        # Default values for new expenses
        form.data["start_date"] = date.today()
        form.data["vat"] = 23.0

    # Required fields notice
    form.create_section(None, "**Campos obrigatórios*")

    return form
