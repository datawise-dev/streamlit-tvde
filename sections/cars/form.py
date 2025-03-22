import streamlit as st
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def car_form(existing_data=None):
    """Display form for car data with error handling."""

    if existing_data is None:
        existing_data = dict()
        clear_form = True
    else:
        clear_form = False  # Don't clear when in edit mode

    data = dict()

    # Create form for car data
    with st.form("car_form", clear_on_submit=clear_form):
        st.subheader("Informação do Veículo")

        # Basic car information
        data["license_plate"] = st.text_input(
            "Matrícula *",
            value=existing_data.get("license_plate", ""),
            help="Identificador único do veículo",
        )

        col1, col2 = st.columns(2)

        with col1:
            data["brand"] = st.text_input(
                "Marca *", value=existing_data.get("brand", "")
            )

        with col2:
            data["model"] = st.text_input(
                "Modelo *", value=existing_data.get("model", "")
            )

        # Cost and date information
        col1, col2 = st.columns(2)

        with col1:
            data["acquisition_cost"] = st.number_input(
                "Custo de Aquisição (€) *",
                min_value=0.0,
                value=float(existing_data.get("acquisition_cost", 0)),
                step=100.0,
                format="%.2f",
            )

        with col2:
            data["acquisition_date"] = st.date_input(
                "Data de Aquisição *", value=existing_data.get("acquisition_date")
            )

        # Category information
        data["category"] = st.selectbox(
            "Categoria *",
            options=["Economy", "Standard", "Premium", "Luxury"],
            index=(
                ["Economy", "Standard", "Premium", "Luxury"].index(
                    existing_data.get("category", "Standard")
                )
                if existing_data
                and existing_data.get("category")
                in ["Economy", "Standard", "Premium", "Luxury"]
                else 1
            ),
        )

        # Status information for existing cars
        if existing_data:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Estado")

            with col2:
                data["is_active"] = st.checkbox(
                    "Ativo",
                    value=existing_data.get("is_active", True),
                    help="Indica se este veículo está atualmente ativo",
                )
        else:
            data["is_active"] = True

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data
