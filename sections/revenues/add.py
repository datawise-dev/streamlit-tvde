import streamlit as st
from sections.revenues.service import RevenueService
from sections.revenues.form import revenue_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab

def manual_entry_tab():
    """Display the manual entry form for adding a single revenue entry."""
    st.subheader("Inserção Manual")
    
    submit_button, revenue_data = revenue_form()

    # Handle form submission
    if submit_button and revenue_data:
        # Validate using the enhanced validation system
        is_valid, errors = RevenueService.validate(revenue_data)
        if not is_valid:
            # Display all validation errors at once
            for error in errors:
                st.error(error)
            st.stop()

        # Attempt to insert data
        try:
            with st.spinner("A inserir dados..."):
                if RevenueService.insert_revenue_data(revenue_data):
                    st.success("Dados de receita inseridos com sucesso!")

                    # Display a summary of the entered data
                    st.subheader("Resumo da Entrada")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Receita Bruta", f"{revenue_data['gross_revenue']:,.2f} €"
                        )
                    with col2:
                        commission_amount = revenue_data["gross_revenue"] * (
                            revenue_data["commission_percentage"] / 100
                        )
                        st.metric("Valor da Comissão", f"{commission_amount:,.2f} €")
                    with col3:
                        net_revenue = (
                            revenue_data["gross_revenue"]
                            - commission_amount
                            + revenue_data["tip"]
                        )
                        st.metric("Receita Líquida", f"{net_revenue:,.2f} €")

                    # Botão para adicionar outra receita
                    st.page_link(
                        "sections/revenues/add.py",
                        label="Adicionar Outra Receita",
                        icon="➕",
                    )
        except Exception as e:
            st.error(f"Erro ao inserir dados: {str(e)}")

def bulk_entry_tab():
    """Display the bulk import interface for adding multiple revenue entries."""
    # Define fields configuration for revenues
    fields_config = [
        {
            "key": "start_date",
            "display_name": "Data Início",
            "required": True,
            "validators": ["date_format"]
        },
        {
            "key": "end_date",
            "display_name": "Data Fim",
            "required": True,
            "validators": ["date_format"]
        },
        {
            "key": "driver_name",
            "display_name": "Nome do Motorista",
            "required": True
        },
        {
            "key": "license_plate",
            "display_name": "Matrícula", 
            "required": True,
            "validators": ["license_plate"]
        },
        {
            "key": "platform",
            "display_name": "Plataforma",
            "required": True,
            "constraints": {"valid_values": ["Uber", "Bolt", "Transfer"]}
        },
        {
            "key": "gross_revenue",
            "display_name": "Receita Bruta",
            "required": True,
            "validators": ["numeric"],
            "constraints": {"min_value": 0}
        },
        {
            "key": "commission_percentage",
            "display_name": "Comissão (%)",
            "validators": ["numeric"],
            "constraints": {"min_value": 0, "max_value": 100},
            "default_value": 0.0
        },
        {
            "key": "tip",
            "display_name": "Gorjeta",
            "validators": ["numeric"],
            "constraints": {"min_value": 0},
            "default_value": 0.0
        },
        {
            "key": "num_travels",
            "display_name": "Número de Viagens",
            "validators": ["numeric"],
            "constraints": {"min_value": 0},
            "default_value": 0
        },
        {
            "key": "num_kilometers",
            "display_name": "Número de Quilómetros",
            "validators": ["numeric"],
            "constraints": {"min_value": 0},
            "default_value": 0.0
        }
    ]
    
    # Create help content
    help_content = {
        "Formato dos Dados": """
        Certifique-se de que:
        - As datas estão no formato YYYY-MM-DD
        - A Data Início não pode ser posterior à Data Fim
        - A Plataforma deve ser uma de: Uber, Bolt, Transfer
        - A Comissão deve estar entre 0 e 100 (%)
        - A Matrícula deve seguir o formato XX-XX-XX
        """,
        "Campos Obrigatórios": """
        Os campos obrigatórios são:
        - Data Início
        - Data Fim
        - Nome do Motorista
        - Matrícula
        - Plataforma
        - Receita Bruta
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="receitas",
        service_class=RevenueService,
        fields_config=fields_config,
        insert_method_name="insert_revenue_data",
        help_content=help_content
    )

@handle_streamlit_error()
def main():
    """Main function to display the add revenue page with tabs."""
    st.title("Adicionar Nova Receita")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    # Navigation button
    st.page_link("sections/revenues/page.py", label="Voltar à lista de Receitas", icon="⬅️")

# Execute the main function
main()
