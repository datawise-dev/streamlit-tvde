import streamlit as st
from sections.drivers.service import DriverService
from sections.drivers.delete import driver_delete
from sections.drivers.form import driver_form
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error
from utils.edit_helpers import check_edit_entity, edit_form_bottom

@handle_streamlit_error()
def main():
    check_query_params()
    driver_id, existing_data = check_edit_entity("veículo", DriverService)
    st.title(f"Editar Motorista: {existing_data.get('display_name', '')}")

    form = driver_form()
    submit_button, data = form.render(existing_data)

    if submit_button:
        try:
            with st.spinner("A atualizar dados...", show_time=True):
                DriverService.update(driver_id, data)
            st.success("Motorista atualizado com sucesso!")
            # Adicionar botão para voltar à lista
            # st.link_button("Voltar à Lista", "/drivers")

        except Exception as e:
            st.error("Não foi possível atualizar o motorista.")
            st.error(str(e))

    # Botões de navegação e ações adicionais
    edit_form_bottom(driver_id, "veículo", "sections/driver/page.py", driver_delete)

# Execute the main function
main()
