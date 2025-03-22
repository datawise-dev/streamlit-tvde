import streamlit as st
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def driver_form(existing_data=None):
    """Display form for driver data with error handling."""

    if existing_data is None:
        existing_data = dict()
        clear_form = True
    else:
        clear_form = False  # Não limpar quando estiver em modo de edição

    data = dict()

    # Create form for driver data
    with st.form("driver_form", clear_on_submit=clear_form):

        st.subheader("Informação Pessoal")

        data["display_name"] = st.text_input(
            "Nome de Exibição *",
            value=existing_data.get("display_name", ""),
            help="Nome único para identificação do motorista",
        )

        col1, col2 = st.columns(2)

        with col1:
            data["first_name"] = st.text_input(
                "Nome *", value=existing_data.get("first_name", "")
            )

        with col2:
            data["last_name"] = st.text_input(
                "Apelido *", value=existing_data.get("last_name", "")
            )

        col1, col2 = st.columns(2)

        with col1:
            data["nif"] = st.text_input(
                "NIF *",
                value=existing_data.get("nif", ""),
                help="Número de Identificação Fiscal",
            )

        with col2:
            data["niss"] = st.text_input(
                "NISS",
                value=existing_data.get("niss", ""),
                help="Número de Identificação de Segurança Social",
            )

        # Address information
        st.subheader("Morada")
        data["address_line1"] = st.text_input(
            "Linha de Endereço 1", value=existing_data.get("address_line1", "")
        )

        data["address_line2"] = st.text_input(
            "Linha de Endereço 2", value=existing_data.get("address_line2", "")
        )

        col1, col2 = st.columns(2)

        with col1:
            data["postal_code"] = st.text_input(
                "Código Postal",
                value=existing_data.get("postal_code", ""),
                placeholder="XXXX-XXX",
            )

        with col2:
            data["location"] = st.text_input(
                "Localidade", value=existing_data.get("location", "")
            )

        if existing_data:
            # Status information
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Status")

            with col2:
                data["is_active"] = st.checkbox(
                    "Ativo",
                    value=existing_data.get("is_active", True),
                    help="Indica se este motorista está atualmente ativo",
                )
        else:
            data["is_active"] = True

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data
