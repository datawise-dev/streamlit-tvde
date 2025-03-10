import streamlit as st
from services.driver_service import DriverService
from views.drivers.delete import driver_delete
from views.drivers.form import driver_form
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def main():
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID do motorista em falta")
        st.stop()

    try:
        driver_id = int(st.query_params["id"])
        # Get driver data
        existing_data = DriverService.get_driver(driver_id)
        if not existing_data:
            # st.title("Adicionar Motorista")
            st.error("Motorista não encontrado.")
            st.stop()

        st.title(f"Editar Motorista: {existing_data.get('display_name', '')}")

    except (ValueError, TypeError):
        st.error("ID de motorista inválido.")

    submit_button, driver_data = driver_form(existing_data)

    required_fields = ["display_name", "first_name", "last_name", "nif"]

    if submit_button:
        for k in required_fields:
            if driver_data.get(k, ""):
                continue
            st.error("Todos os campos obrigatórios devem ser preenchidos")
            st.stop()

        try:
            with st.spinner("A atualizar dados...", show_time=True):
                DriverService.update_driver(driver_id, driver_data)
            st.success("Motorista atualizado com sucesso!")
            # Adicionar botão para voltar à lista
            # st.link_button("Voltar à Lista", "/drivers")

        except Exception as e:
            st.error("Não foi possível atualizar o motorista.")
            st.error(str(e))

    # Botões de navegação e ações adicionais
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "views/drivers/page.py",
            label="Voltar à lista de Motoristas",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "Eliminar Motorista", type="tertiary", icon="🗑️", use_container_width=True
        ):
            driver_delete(driver_id, existing_data.get("display_name", ""))

# Execute the main function
main()
