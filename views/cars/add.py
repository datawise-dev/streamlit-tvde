import streamlit as st
import time
from services.car_service import CarService
from views.cars.form import car_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab

def manual_entry_tab():
    # Existing manual entry form
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

def bulk_entry_tab():
    # Define standard fields for cars
    standard_fields = [
        "license_plate", "brand", "model", "acquisition_cost", 
        "acquisition_date", "category"
    ]
    
    # Map field names to friendly display names
    field_display_names = {
        "license_plate": "Matrícula",
        "brand": "Marca",
        "model": "Modelo",
        "acquisition_cost": "Custo de Aquisição (€)",
        "acquisition_date": "Data de Aquisição",
        "category": "Categoria",
    }
    
    # Set field constraints
    field_constraints = {
        "category": {
            "valid_values": ["Economy", "Standard", "Premium", "Luxury"]
        },
        "is_active": {
            "default": True
        }
    }
    
    # Create help content
    help_content = {
        "Informação sobre Categorias": """
        As categorias válidas para veículos são:
        - Economy
        - Standard
        - Premium
        - Luxury
        
        Certifique-se de que os valores na coluna 'Categoria' correspondem exatamente a uma destas opções.
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="veículos",
        service_class=CarService,
        standard_fields=standard_fields,
        field_display_names=field_display_names,
        field_constraints=field_constraints,
        insert_method_name="insert_car",
        help_content=help_content
    )


@handle_streamlit_error()
def main():
    st.title("Adicionar Veículo")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    st.page_link("views/cars/page.py", label="Voltar à lista de Veículos", icon="⬅️")


# Execute the main function
main()
