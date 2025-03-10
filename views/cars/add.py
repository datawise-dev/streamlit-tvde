import streamlit as st
import time
from services.car_service import CarService
from views.cars.form import car_form
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    st.title("Adicionar Veículo")

    submit_button, car_data = car_form()

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
            with st.spinner("A adicionar dados...", show_time=True):
                CarService.insert_car(car_data)
            st.success("Veículo adicionado com sucesso!")
            time.sleep(2)
            # Clear form after successful insert
            st.rerun()
        except Exception as e:
            st.error(
                "Não foi possível adicionar o veículo. Verifique os dados e tente novamente."
            )
            st.error(str(e))

    st.page_link("views/cars/page.py", label="Voltar à lista de Veículos", icon="⬅️")


# Execute the main function
main()
