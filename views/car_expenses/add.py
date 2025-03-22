import streamlit as st
import time
from services.car_expense_service import CarExpenseService
from views.car_expenses.form import car_expense_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab
from datetime import date

def manual_entry_tab():
    """Display the manual entry form for adding a single car expense."""
    submit_button, expense_data = car_expense_form()

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = ["car_id", "expense_type", "start_date", "amount"]

        # If expense type is Credit, end_date is required
        if expense_data.get("expense_type") == "Credit":
            required_fields.append("end_date")

        # Map fields to Portuguese for error messages
        field_names_pt = {
            "car_id": "Veículo",
            "expense_type": "Tipo de Despesa",
            "start_date": "Data de Início",
            "end_date": "Data de Fim",
            "amount": "Montante",
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
        if isinstance(expense_data.get("start_date"), date):
            expense_data["start_date"] = expense_data["start_date"].strftime("%Y-%m-%d")

        if expense_data.get("end_date") and isinstance(
            expense_data.get("end_date"), date
        ):
            expense_data["end_date"] = expense_data["end_date"].strftime("%Y-%m-%d")

        # Validate dates if end_date is provided
        if (
            expense_data.get("end_date")
            and expense_data["end_date"] < expense_data["start_date"]
        ):
            st.error("A data de fim não pode ser anterior à data de início")
            st.stop()

        # Try to insert the data
        try:
            with st.spinner("A adicionar dados..."):
                CarExpenseService.insert_car_expense(expense_data)
            st.success("Despesa de veículo adicionada com sucesso!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao guardar dados: {str(e)}")

def bulk_entry_tab():
    """Display the bulk import interface for adding multiple car expenses."""
    # Define standard fields for car expenses
    standard_fields = [
        "car_id", "expense_type", "start_date", "end_date", 
        "amount", "vat", "description"
    ]
    
    # Map field names to friendly display names
    field_display_names = {
        "car_id": "ID do Veículo",
        "expense_type": "Tipo de Despesa",
        "start_date": "Data de Início",
        "end_date": "Data de Fim",
        "amount": "Montante (€)",
        "vat": "IVA (%)",
        "description": "Descrição"
    }
    
    # Set field constraints
    field_constraints = {
        "expense_type": {
            "valid_values": ["Credit", "Gasoline", "Tolls", "Repairs", "Washing"]
        }
    }
    
    # Create help content
    help_content = {
        "Formato dos Dados": """
        Certifique-se de que:
        - As datas estão no formato YYYY-MM-DD
        - A Data de Início não pode ser posterior à Data de Fim
        - O ID do Veículo deve corresponder a um veículo existente no sistema
        - O Tipo de Despesa deve ser um de: Credit, Gasoline, Tolls, Repairs, Washing
        - Para despesas do tipo 'Credit', a Data de Fim é obrigatória
        - Os valores monetários devem usar o ponto como separador decimal
        """,
        "Tipos de Despesa": """
        Os tipos de despesa disponíveis são:
        - Credit (Crédito)
        - Gasoline (Combustível)
        - Tolls (Portagens)
        - Repairs (Reparações)
        - Washing (Lavagem)
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="despesas de veículos",
        service_class=CarExpenseService,
        standard_fields=standard_fields,
        field_display_names=field_display_names,
        field_constraints=field_constraints,
        insert_method_name="insert_car_expense",
        help_content=help_content
    )

@handle_streamlit_error()
def main():
    """Main function to display the add car expense page with tabs."""
    st.title("Adicionar Nova Despesa de Veículo")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    # Link to return to list
    st.page_link(
        "views/car_expenses/page.py",
        label="Voltar à lista de Despesas de Veículos",
        icon="⬅️",
    )

# Execute the main function
main()
