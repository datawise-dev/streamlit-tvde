import streamlit as st
import time
from services.car_service import CarService
from views.cars.form import car_form
from utils.error_handlers import handle_streamlit_error
from utils.bulk_import import bulk_import_component

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
    
    # Define the validation function for a single record
    def validate_car_record(record):
        # Add is_active field if not present
        if "is_active" not in record:
            record["is_active"] = True
            
        # Ensure category is valid
        valid_categories = ["Economy", "Standard", "Premium", "Luxury"]
        if "category" in record and record["category"] not in valid_categories:
            return False, [f"Categoria inválida. Deve ser uma das seguintes: {', '.join(valid_categories)}"]
        
        return CarService.validate(record)
    
    # Define the upload function for the processed records
    def upload_car_records(records):
        # Process each record individually since we need to check for unique constraints
        success_count = 0
        errors = []
        
        for record in records:
            try:
                CarService.insert_car(record)
                success_count += 1
            except Exception as e:
                errors.append(str(e))
        
        if errors:
            if len(errors) == len(records):
                raise Exception(f"Falha ao importar todos os registos. Primeiro erro: {errors[0]}")
            else:
                raise Exception(f"Importados {success_count} de {len(records)} registos. Erro: {errors[0]}")
        
        return True
    
    # Use the bulk import component
    with st.container(border=1):
        bulk_import_component(
            entity_name="veículos",
            standard_fields=standard_fields,
            validation_function=validate_car_record,
            upload_function=upload_car_records,
            field_display_names=field_display_names
        )
    
    # Display additional help information
    with st.expander("Informação sobre Categorias"):
        st.info("""
        As categorias válidas para veículos são:
        - Economy
        - Standard
        - Premium
        - Luxury
        
        Certifique-se de que os valores na coluna 'Categoria' correspondem exatamente a uma destas opções.
        """)


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
