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

    submit_button, car_data = car_form(existing_data)

    required_fields = [
        "license_plate",
        "brand",
        "model",
        "acquisition_cost",
        "acquisition_date",
        "category",
    ]

    if submit_button:
        # Ensure acquisition_date is formatted as string
        if isinstance(car_data.get("acquisition_date"), object):
            car_data["acquisition_date"] = car_data["acquisition_date"].strftime(
                "%Y-%m-%d"
            )

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not car_data.get(field, ""):
                missing_fields.append(field)

        if missing_fields:
            st.error("Todos os campos obrigatórios devem ser preenchidos")
            st.stop()

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
