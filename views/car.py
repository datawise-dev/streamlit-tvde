import streamlit as st
import time
from services.car_service import CarService
from utils.error_handlers import handle_streamlit_error

@st.dialog("Delete Car")
@handle_streamlit_error()
def delete_car(car_id):
    st.write("Please confirm below that you want to delete this car")
    if st.button("Confirm"):
        with st.spinner("Deleting Car...", show_time=True):
            CarService.delete_car(car_id)
        st.success("Car deleted")
        time.sleep(5)
        st.page_link("views/cars.py")

@handle_streamlit_error()
def car_form(existing_data=None):
    """Display form for adding or editing a car with more modern UI."""
    if existing_data is None:
        existing_data = dict()

    data = dict()

    # Create form for car data
    with st.form("car_form", clear_on_submit=True):
        st.subheader("Car Information")

        # Basic car information
        data["license_plate"] = st.text_input(
            "License Plate *",
            value=existing_data.get("license_plate", ""),
            help="Unique identifier for the vehicle"
        )

        col1, col2 = st.columns(2)

        with col1:
            data["brand"] = st.text_input(
                "Brand *",
                value=existing_data.get("brand", "")
            )

        with col2:
            data["model"] = st.text_input(
                "Model *",
                value=existing_data.get("model", "")
            )

        # Cost and date information
        col1, col2 = st.columns(2)

        with col1:
            data["acquisition_cost"] = st.number_input(
                "Acquisition Cost (€) *",
                min_value=0.0,
                value=float(existing_data.get("acquisition_cost", 0)),
                step=100.0,
                format="%.2f"
            )

        with col2:
            data["acquisition_date"] = st.date_input(
                "Acquisition Date *",
                value=existing_data.get("acquisition_date")
            )

        # Category information
        data["category"] = st.selectbox(
            "Category *",
            options=["Economy", "Standard", "Premium", "Luxury"],
            index=["Economy", "Standard", "Premium", "Luxury"].index(
                existing_data.get("category", "Standard")
            ) if existing_data and existing_data.get("category") in ["Economy", "Standard", "Premium", "Luxury"] else 1
        )

        # Status information for existing cars
        if existing_data:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Status")

            with col2:
                data["is_active"] = st.checkbox(
                    "Is Active",
                    value=existing_data.get("is_active", True),
                    help="Indicate if this car is currently active"
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
    """Main car form view with error handling."""
    # Set page title based on mode
    existing_data = None
    if "id" in st.query_params:
        try:
            car_id = int(st.query_params["id"])
            # Get car data
            existing_data = CarService.get_car(car_id)
            if not existing_data:
                st.error("Carro não encontrado.")
                st.stop()

            col1, col2 = st.columns(2)

            with col1:
                st.title(f"Editar Carro: {existing_data.get('license_plate', '')}")

            with col2:
                if st.button("Delete"):
                    delete_car(car_id)
        except (ValueError, TypeError):
            st.title("Adicionar Carro")
            st.error("ID de carro inválido.")
    else:
        st.title("Adicionar Carro")

    submit_button, car_data = car_form(existing_data)

    required_fields = ["license_plate", "brand", "model", "acquisition_cost", "acquisition_date", "category"]

    if submit_button:
        # Ensure acquisition_date is formatted as string
        if isinstance(car_data.get("acquisition_date"), object):
            car_data["acquisition_date"] = car_data["acquisition_date"].strftime('%Y-%m-%d')

        # Validate required fields
        for k in required_fields:
            if not car_data.get(k, ""):
                st.error("Todos os campos obrigatórios devem ser preenchidos")
                st.stop()

        if existing_data:
            try:
                with st.spinner("A atualizar dados...", show_time=True):
                    CarService.update_car(car_id, car_data)
                st.success("Carro atualizado com sucesso!")
            except Exception as e:
                st.error("Não foi possível atualizar o carro. Verifique os dados e tente novamente.")
                st.error(str(e))
        else:
            try:
                with st.spinner("A adicionar dados...", show_time=True):
                    CarService.insert_car(car_data)
                st.success("Carro adicionado com sucesso!")
                time.sleep(5)
                # Clear form after successful insert
                st.rerun()
            except Exception as e:
                st.error("Não foi possível adicionar o carro. Verifique os dados e tente novamente.")
                st.error(str(e))

    st.page_link("views/cars.py", label="Voltar à lista de Carros", icon="⬅️")

# Execute the main function
main()
