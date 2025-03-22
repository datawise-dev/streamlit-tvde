import streamlit as st
import time
from services.driver_service import DriverService
from views.drivers.form import driver_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab

def manual_entry_tab():
    """Display the manual entry form for adding a single driver."""
    submit_button, driver_data = driver_form()

    required_fields = ["display_name", "first_name", "last_name", "nif"]

    if submit_button:
        # Validate required fields
        for k in required_fields:
            if not driver_data.get(k, ""):
                st.error("Todos os campos obrigatórios devem ser preenchidos")
                st.stop()

        try:
            with st.spinner("A adicionar dados...", show_time=True):
                DriverService.insert_driver(driver_data)
            st.success("Motorista adicionado com sucesso!")
            time.sleep(2)
            # Clear form after successful insert
            st.rerun()
        except Exception as e:
            st.error("Não foi possível adicionar o motorista.")
            st.error(str(e))

def bulk_entry_tab():
    """Display the bulk import interface for adding multiple drivers."""
    # Define standard fields for drivers
    standard_fields = [
        "display_name", "first_name", "last_name", "nif", 
        "address_line1", "address_line2", "postal_code", "location"
    ]
    
    # Map field names to friendly display names
    field_display_names = {
        "display_name": "Nome de Exibição",
        "first_name": "Nome",
        "last_name": "Apelido",
        "nif": "NIF",
        "address_line1": "Morada (Linha 1)",
        "address_line2": "Morada (Linha 2)",
        "postal_code": "Código Postal",
        "location": "Localidade",
    }
    
    # Set field constraints and defaults
    field_constraints = {
        "is_active": {
            "default": True
        }
    }
    
    # Create help content
    help_content = {
        "Formato dos Dados": """
        Certifique-se de que:
        - O NIF tem exatamente 9 dígitos numéricos
        - O código postal segue o formato XXXX-XXX
        - O "Nome de Exibição" é único para cada motorista
        """,
        "Campos Obrigatórios": """
        Os campos obrigatórios são:
        - Nome de Exibição
        - Nome
        - Apelido
        - NIF
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="motoristas",
        service_class=DriverService,
        standard_fields=standard_fields,
        field_display_names=field_display_names,
        field_constraints=field_constraints,
        insert_method_name="insert_driver",
        help_content=help_content
    )

@handle_streamlit_error()
def main():
    """Main function to display the add driver page with tabs."""
    st.title("Adicionar Motorista")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    st.page_link("views/drivers/page.py", label="Voltar à lista de Motoristas", icon="⬅️")

# Execute the main function
main()
