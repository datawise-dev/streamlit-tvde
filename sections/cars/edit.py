import streamlit as st
from sections.cars.service import CarService
from sections.cars.delete import car_delete
from sections.cars.form import car_form
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID do veículo em falta")
        st.stop()

    try:
        car_id = int(st.query_params["id"])
        # Get car data
        existing_data = CarService.get(car_id)
        if not existing_data:
            st.error("Veículo não encontrado.")
            st.stop()

        st.title(f"Editar Veículo: {existing_data.get('license_plate', '')}")

    except (ValueError, TypeError):
        st.error("ID de veículo inválido.")
        st.stop()

    form = car_form()
    submit_button = form.render(existing_data)
    data = form.data

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
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "sections/cars/page.py",
            label="Voltar à lista de Veículos",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "Eliminar Veículo", type="tertiary", icon="🗑️", use_container_width=True
        ):
            car_delete(car_id, existing_data.get("license_plate", ""))


# Execute the main function
main()
