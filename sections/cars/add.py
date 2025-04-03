import streamlit as st
from sections.cars.service import CarService
from sections.cars.form import car_form
from utils.error_handlers import handle_streamlit_error
from utils.bulk_import import entity_bulk_import_tab

def process_data(data):
    # Ensure acquisition_date is formatted as string
    if isinstance(data.get("acquisition_date"), object):
        data["acquisition_date"] = data["acquisition_date"].strftime("%Y-%m-%d")
    return data



@handle_streamlit_error()
def main():
    st.title("Adicionar Veículo")

    # Existing manual entry form
    form = car_form()
    form.add_post_submit_callback
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:

        # Change button text based on mode
        submit_button, data = form.render()

        if submit_button:
            # Ensure acquisition_date is formatted as string
            if isinstance(data.get("acquisition_date"), object):
                data["acquisition_date"] = data["acquisition_date"].strftime("%Y-%m-%d")

            upload_data(data, "veículo", CarService)
    
    with tab2:
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
            fields_config=form.get_field_configs(),
            help_content=help_content
        )

    st.page_link("sections/cars/page.py", label="Voltar à lista de Veículos", icon="⬅️")


# Execute the main function
main()