import streamlit as st
import time
from services.driver_service import DriverService
from utils.error_handlers import handle_streamlit_error


@st.dialog("Delete Driver")
@handle_streamlit_error()
def delete_driver(driver_id):
    """Dialog to confirm driver deletion with error handling."""
    st.write("Please confirm below that you want to delete this driver")
    if st.button("Confirm"):
        with st.spinner("Deleting Driver...", show_time=True):
            DriverService.delete_driver(driver_id)
        st.success("Driver deleted")
        time.sleep(5)
        st.page_link("views/drivers.py")


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
                "First Name", value=existing_data.get("first_name", "")
            )

        with col2:
            data["last_name"] = st.text_input(
                "Last Name *", value=existing_data.get("last_name", "")
            )

        col1, col2 = st.columns(2)

        with col1:
            data["nif"] = st.text_input(
                "NIF",
                value=existing_data.get("nif", ""),
                help="Tax identification number *",
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


# Main view function with error handling
@handle_streamlit_error()
def main():
    """Main driver form view with error handling."""
    # Set page title based on mode
    existing_data = None
    
    if "id" in st.query_params:
        try:
            driver_id = int(st.query_params["id"])
            # Get driver data
            existing_data = DriverService.get_driver(driver_id)
            if not existing_data:
                # st.title("Adicionar Motorista")
                st.error("Motorista não encontrado.")
                st.stop()

            col1, col2 = st.columns(2)

            with col1:
                st.title(f"Editar Motorista: {existing_data.get('display_name', '')}")

            with col2:
                if st.button("Delete"):
                    delete_driver(driver_id)
        except (ValueError, TypeError):
            st.title("Adicionar Motorista")
            st.error("ID de motorista inválido.")
    else:
        st.title("Adicionar Motorista")

    submit_button, driver_data = driver_form(existing_data)

    required_fields = ["display_name", "first_name", "last_name", "nif"]

    if submit_button:
        for k in required_fields:
            if driver_data.get(k, ""):
                continue
            st.error("Todos os campos obrigatórios devem ser preenchidos")
            st.stop()

        if existing_data:
            try:
                with st.spinner("A atualizar dados...", show_time=True):
                    DriverService.update_driver(driver_id, driver_data)
                st.success("Motorista atualizado com sucesso!")
                # Adicionar botão para voltar à lista
                # st.link_button("Voltar à Lista", "/drivers")
                st.page_link("views/drivers.py", label="Voltar à lista de Motoristas")
            except Exception as e:
                st.error("Não foi possível atualizar o motorista.")
                st.error(str(e))
        else:
            try:
                with st.spinner("A adicionar dados...", show_time=True):
                    DriverService.insert_driver(driver_data)
                st.success("Motorista adicionado com sucesso!")
                time.sleep(5)
                # Clear form after successful insert
                st.rerun()
            except Exception as e:
                st.error("Não foi possível adicionar o motorista.")
                st.error(str(e))

# Execute the main function
main()
