import streamlit as st
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def driver_form(existing_data=None):
    """Display form for driver data with error handling."""

    if existing_data is None:
        existing_data = dict()

    data = dict()

    # Create form for driver data
    with st.form("driver_form", clear_on_submit=True):

        st.subheader("Informação Pessoal")

        data["display_name"] = st.text_input(
            "Display Name *",
            value=existing_data.get("display_name", ""),
            help="Nome único para identificação do motorista",
        )

        col1, col2 = st.columns(2)

        with col1:
            data["first_name"] = st.text_input(
                "First Name *", value=existing_data.get("first_name", "")
            )

        with col2:
            data["last_name"] = st.text_input(
                "Last Name *", value=existing_data.get("last_name", "")
            )

        col1, col2 = st.columns(2)

        with col1:
            data["nif"] = st.text_input(
                "NIF *",
                value=existing_data.get("nif", ""),
                help="Tax identification number",
            )

        with col2:
            data["niss"] = st.text_input(
                "NISS",
                value=existing_data.get("niss", ""),
                help="Social security number",
            )

        # Address information
        st.subheader("Morada")
        data["address_line1"] = st.text_input(
            "Address Line 1", value=existing_data.get("address_line1", "")
        )

        data["address_line2"] = st.text_input(
            "Address Line 2", value=existing_data.get("address_line2", "")
        )

        col1, col2 = st.columns(2)

        with col1:
            data["postal_code"] = st.text_input(
                "Postal Code",
                value=existing_data.get("postal_code", ""),
                placeholder="XXXX-XXX",
            )

        with col2:
            data["location"] = st.text_input(
                "Location", value=existing_data.get("location", "")
            )

        if existing_data:
            # Status information
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Status")

            with col2:
                data["is_active"] = st.checkbox(
                    "Is Active",
                    value=existing_data.get("is_active", True),
                    help="Indicate if this driver is currently active",
                )
        else:
            data["is_active"] = True

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data