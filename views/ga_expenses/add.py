import streamlit as st
import time
from services.ga_expense_service import GAExpenseService
from views.ga_expenses.form import ga_expense_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab
from datetime import date
from views.ga_expenses.form import EXPENSE_TYPE_MAP_PT_TO_EN, EXPENSE_TYPE_MAP_EN_TO_PT

def manual_entry_tab():
    """Display the manual entry form for adding a single G&A expense."""
    submit_button, expense_data = ga_expense_form()

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = ["expense_type", "start_date", "amount"]
        
        # Map fields to Portuguese for error messages
        field_names_pt = {
            "expense_type": "Tipo de Despesa",
            "start_date": "Data de Início",
            "amount": "Montante"
        }
        
        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not expense_data.get(field):
                missing_fields.append(field_names_pt.get(field, field))
                
        if missing_fields:
            st.error(f"Campos obrigatórios em falta: {', '.join(missing_fields)}")
            st.stop()
        
        # Convert dates to strings
        if isinstance(expense_data.get('start_date'), date):
            expense_data['start_date'] = expense_data['start_date'].strftime('%Y-%m-%d')
            
        if expense_data.get('end_date') and isinstance(expense_data.get('end_date'), date):
            expense_data['end_date'] = expense_data['end_date'].strftime('%Y-%m-%d')
            
        if expense_data.get('payment_date') and isinstance(expense_data.get('payment_date'), date):
            expense_data['payment_date'] = expense_data['payment_date'].strftime('%Y-%m-%d')
        
        # Validate dates if end_date is provided
        if expense_data.get('end_date') and expense_data['end_date'] < expense_data['start_date']:
            st.error("A data de fim não pode ser anterior à data de início")
            st.stop()
        
        # Try to insert the data
        try:
            with st.spinner("A adicionar dados..."):
                GAExpenseService.insert_ga_expense(expense_data)
            st.success("Despesa G&A adicionada com sucesso!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao guardar dados: {str(e)}")

def bulk_entry_tab():
    """Display the bulk import interface for adding multiple G&A expenses."""
    # Define fields configuration for G&A expenses
    fields_config = [
        {
            "key": "expense_type",
            "display_name": "Tipo de Despesa",
            "required": True,
            "constraints": {"valid_values": list(EXPENSE_TYPE_MAP_PT_TO_EN.values())}
        },
        {
            "key": "start_date",
            "display_name": "Data de Início",
            "required": True,
            "validators": ["date_format"]
        },
        {
            "key": "end_date",
            "display_name": "Data de Fim",
            "validators": ["date_format"]
        },
        {
            "key": "payment_date",
            "display_name": "Data de Pagamento",
            "validators": ["date_format"]
        },
        {
            "key": "amount",
            "display_name": "Montante (€)",
            "required": True,
            "validators": ["numeric"],
            "constraints": {"min_value": 0}
        },
        {
            "key": "vat",
            "display_name": "IVA (%)",
            "validators": ["numeric"],
            "constraints": {"min_value": 0, "max_value": 100},
            "default_value": 23.0
        },
        {
            "key": "description",
            "display_name": "Descrição",
            "validators": ["max_length"],
            "constraints": {"max_length": 500}
        }
    ]
    
    # Create help content
    help_content = {
        "Formato dos Dados": """
        Certifique-se de que:
        - As datas estão no formato YYYY-MM-DD
        - A Data de Início não pode ser posterior à Data de Fim
        - O Tipo de Despesa deve ser um dos valores válidos
        - Os valores monetários devem usar o ponto como separador decimal
        """,
        "Tipos de Despesa": f"""
        Os tipos de despesa disponíveis são:
        {', '.join([f"- {en} ({pt})" for pt, en in EXPENSE_TYPE_MAP_PT_TO_EN.items()])}
        
        Nota: Use os valores em inglês (após o parêntesis) na coluna do tipo de despesa.
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="despesas G&A",
        service_class=GAExpenseService,
        fields_config=fields_config,
        insert_method_name="insert_ga_expense",
        help_content=help_content
    )

@handle_streamlit_error()
def main():
    """Main function to display the add G&A expense page with tabs."""
    st.title("Adicionar Nova Despesa G&A")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    # Link to return to list
    st.page_link("views/ga_expenses/page.py", label="Voltar à lista de Despesas G&A", icon="⬅️")

# Execute the main function
main()
