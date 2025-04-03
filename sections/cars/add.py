import streamlit as st
import time
from sections.cars.service import CarService
from sections.cars.form import car_form
from utils.error_handlers import handle_streamlit_error
from utils.bulk_import import entity_bulk_import_tab
from utils.validators import validate_license_plate

def manual_entry_tab():
    # Existing manual entry form
    form = car_form()

     # Change button text based on mode
    submit_button, data = form.render()

    if submit_button:
        # Ensure acquisition_date is formatted as string
        if isinstance(data.get("acquisition_date"), object):
            data["acquisition_date"] = data["acquisition_date"].strftime("%Y-%m-%d")

        try:
            with st.spinner("A adicionar dados...", show_time=True):
                CarService.insert(data)
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
    # Define fields configuration for cars
    fields_config = [
        {
            "key": "license_plate",
            "label": "Matrícula",
            "required": True,
            "validator": validate_license_plate
        },
        {
            "key": "brand",
            "label": "Marca",
            "required": True
        },
        {
            "key": "model",
            "label": "Modelo",
            "required": True
        },
        {
            "key": "acquisition_cost",
            "label": "Custo de Aquisição (€)",
            "type": "number", #
            "min_value": 0, #
            "required": True,
        },
        {
            "key": "acquisition_date",
            "label": "Data de Aquisição",
            "required": True,
            "type": "date" #
        },
        {
            "key": "category",
            "label": "Categoria",
            "required": True,
            "options": ["Economy", "Standard", "Premium", "Luxury"],
            "default": "Standard"
        },
        {
            "key": "is_active",
            "label": "Ativo",
            "type": "checkbox",
            "default": True
        }
    ]
    
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
        fields_config=fields_config,
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

    st.page_link("sections/cars/page.py", label="Voltar à lista de Veículos", icon="⬅️")


# Execute the main function
main()