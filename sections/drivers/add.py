import streamlit as st
import time
from sections.drivers.service import DriverService
from sections.drivers.form import driver_form
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
    # Define fields configuration for drivers
    fields_config = [
        {
            "key": "display_name",
            "display_name": "Nome de Exibição",
            "required": True
        },
        {
            "key": "first_name",
            "display_name": "Nome",
            "required": True
        },
        {
            "key": "last_name",
            "display_name": "Apelido",
            "required": True
        },
        {
            "key": "nif",
            "display_name": "NIF",
            "required": True,
            "validators": ["nif"]
        },
        {
            "key": "address_line1",
            "display_name": "Morada (Linha 1)"
        },
        {
            "key": "address_line2",
            "display_name": "Morada (Linha 2)"
        },
        {
            "key": "postal_code",
            "display_name": "Código Postal",
            "validators": ["postal_code"]
        },
        {
            "key": "location",
            "display_name": "Localidade"
        },
        {
            "key": "is_active",
            "display_name": "Ativo",
            "default_value": True
        }
    ]
    
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
        fields_config=fields_config,
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

    st.page_link("sections/drivers/page.py", label="Voltar à lista de Motoristas", icon="⬅️")

# Execute the main function
main()
