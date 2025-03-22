import streamlit as st
from utils.error_handlers import handle_streamlit_error
from datetime import date
from services.car_service import CarService

# Dictionary to map between Portuguese and English expense types
EXPENSE_TYPE_MAP_PT_TO_EN = {
    "Crédito": "Credit",
    "Combustível": "Gasoline",
    "Portagens": "Tolls",
    "Reparações": "Repairs",
    "Lavagem": "Washing",
}

EXPENSE_TYPE_MAP_EN_TO_PT = {v: k for k, v in EXPENSE_TYPE_MAP_PT_TO_EN.items()}


@handle_streamlit_error()
def car_expense_form(existing_data=None):
    """Display form for car expense data with error handling."""

    if existing_data is None:
        existing_data = dict()
        clear_form = True
    else:
        clear_form = False  # Don't clear when in edit mode

    data = dict()

    # Create form for car expense data
    with st.form("car_expense_form", clear_on_submit=clear_form):
        st.subheader("Informação da Despesa de Veículo")

        col1, col2 = st.columns(2)

        with col1:
            # Car selection
            try:
                cars = CarService.get_all_license_plates()
                if not cars:
                    st.warning("Não existem veículos disponíveis no sistema")
                    car_options = {}
                else:
                    # Create a dictionary for car selection
                    car_options = {
                        car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars
                    }

                default_index = 0
                if existing_data.get("car_id") in car_options:
                    default_index = list(car_options.keys()).index(
                        existing_data.get("car_id")
                    )

                car_id = st.selectbox(
                    "Veículo *",
                    options=list(car_options.keys()) if car_options else [],
                    format_func=lambda x: car_options.get(x, "Selecione um veículo"),
                    index=default_index if car_options else 0,
                    help="Selecione o veículo para esta despesa",
                )
                data["car_id"] = car_id

            except Exception as e:
                st.error(f"Erro ao carregar veículos: {str(e)}")

            # Date information
            data["start_date"] = st.date_input(
                "Data de Início *",
                value=existing_data.get("start_date", date.today()),
                help="Quando a despesa ocorreu ou começou",
            )

        with col2:

            # Expense type selection - translated options
            expense_type_options_en = [
                "Credit",
                "Gasoline",
                "Tolls",
                "Repairs",
                "Washing",
            ]
            expense_type_options_pt = [
                EXPENSE_TYPE_MAP_EN_TO_PT.get(opt, opt)
                for opt in expense_type_options_en
            ]

            default_type_index = 0
            if existing_data.get("expense_type") in expense_type_options_en:
                default_type_index = expense_type_options_en.index(
                    existing_data.get("expense_type")
                )

            # Display Portuguese options, but store English values
            selected_type_pt = st.selectbox(
                "Tipo de Despesa *",
                options=expense_type_options_pt,
                index=default_type_index,
                help="Tipo de despesa de veículo",
            )

            # Map back to English for storage
            data["expense_type"] = EXPENSE_TYPE_MAP_PT_TO_EN.get(
                selected_type_pt, selected_type_pt
            )

            data["end_date"] = st.date_input(
                "Data de Fim *",
                value=existing_data.get("end_date", None),
                help="Data de fim (obrigatória para despesas de crédito)",
            )

        # Amount
        col1, col2 = st.columns(2)

        with col1:
            data["amount"] = st.number_input(
                "Montante (€) *",
                min_value=0.0,
                value=float(existing_data.get("amount", 0)),
                step=0.01,
                format="%.2f",
                help="Valor da despesa em euros",
            )

        with col2:
            data["vat"] = st.number_input(
                "IVA (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(existing_data.get("vat", 23.0)),
                step=0.1,
                format="%.1f",
                help="Percentagem de IVA aplicada a esta despesa",
            )

        # Description
        data["description"] = st.text_area(
            "Descrição / Comentários",
            value=existing_data.get("description", ""),
            help="Detalhes adicionais sobre a despesa",
        )

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data.get("id") else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data
