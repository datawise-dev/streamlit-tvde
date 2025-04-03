import streamlit as st
from sections.cars.service import CarService
from sections.cars.delete import car_delete
from sections.cars.form import car_form
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error
from utils.edit_helpers import check_edit_entity, edit_form_bottom

@handle_streamlit_error()
def main():
    check_query_params()
    car_id, existing_data = check_edit_entity("veículo", CarService)
    st.title(f"Editar Veículo: {existing_data.get('license_plate', '')}")

    form = car_form()
    submit_button, data = form.render(existing_data)

    if submit_button:
        # Ensure acquisition_date is formatted as string
        if isinstance(data.get("acquisition_date"), object):
            data["acquisition_date"] = data["acquisition_date"].strftime("%Y-%m-%d")
        try:
            with st.spinner("A atualizar dados...", show_time=True):
                CarService.update(car_id, data)
            st.success("Veículo atualizado com sucesso!")
        except Exception as e:
            st.error(
                "Não foi possível atualizar o veículo. Verifique os dados e tente novamente."
            )
            st.error(str(e))

    # Botões de navegação e ações adicionais
    edit_form_bottom(car_id, "veículo", "sections/cars/page.py", car_delete)

# Execute the main function
main()
