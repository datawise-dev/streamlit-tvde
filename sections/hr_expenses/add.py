import streamlit as st
import time
from datetime import date
from services.hr_expense_service import HRExpenseService
from sections.hr_expenses.form import hr_expense_form
from utils.error_handlers import handle_streamlit_error
from utils.entity_import import entity_bulk_import_tab

def manual_entry_tab():
    """Display the manual entry form for adding a single HR expense."""
    submit_button, expense_data = hr_expense_form()

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = [
            "driver_id",
            "start_date",
            "end_date",
            "payment_date",
            "base_salary",
            "working_days",
            "meal_allowance_per_day",
        ]

        # Map fields to Portuguese for error messages
        field_names_pt = {
            "driver_id": "Motorista",
            "start_date": "Data de Início",
            "end_date": "Data de Fim",
            "payment_date": "Data de Pagamento",
            "base_salary": "Salário Base",
            "working_days": "Dias Úteis Trabalhados",
            "meal_allowance_per_day": "Subsídio de Alimentação / Dia",
        }

        # Convert dates to strings
        for field in ["start_date", "end_date", "payment_date"]:
            if isinstance(expense_data.get(field), date):
                expense_data[field] = expense_data[field].strftime("%Y-%m-%d")

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not expense_data.get(field):
                missing_fields.append(field_names_pt.get(field, field))

        if missing_fields:
            st.error(f"Campos obrigatórios em falta: {', '.join(missing_fields)}")
            st.stop()

        # Validate dates
        if expense_data["end_date"] < expense_data["start_date"]:
            st.error("A data de fim não pode ser anterior à data de início")
            st.stop()

        # Try to insert the data
        try:
            with st.spinner("A adicionar dados..."):
                HRExpenseService.insert_expense(expense_data)
            st.success("Despesa RH adicionada com sucesso!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao guardar dados: {str(e)}")

def bulk_entry_tab():
    """Display the bulk import interface for adding multiple HR expenses."""
    # Define fields configuration for HR expenses
    fields_config = [
        {
            "key": "driver_id",
            "display_name": "ID do Motorista",
            "required": True,
            "validators": ["numeric"]
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
            "required": True,
            "validators": ["date_format"]
        },
        {
            "key": "payment_date",
            "display_name": "Data de Pagamento",
            "required": True,
            "validators": ["date_format"]
        },
        {
            "key": "base_salary",
            "display_name": "Salário Base (€)",
            "required": True,
            "validators": ["numeric"],
            "constraints": {"min_value": 0}
        },
        {
            "key": "working_days",
            "display_name": "Dias Úteis Trabalhados",
            "required": True,
            "validators": ["numeric"],
            "constraints": {"min_value": 0}
        },
        {
            "key": "meal_allowance_per_day",
            "display_name": "Subsídio de Alimentação / Dia (€)",
            "required": True,
            "validators": ["numeric"],
            "constraints": {"min_value": 0}
        },
        {
            "key": "other_benefits",
            "display_name": "Outros Benefícios (€)",
            "validators": ["numeric"],
            "constraints": {"min_value": 0},
            "default_value": 0.0
        },
        {
            "key": "notes",
            "display_name": "Notas",
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
        - O ID do Motorista deve corresponder a um motorista existente no sistema
        - Os valores monetários devem usar o ponto como separador decimal
        """,
        "Campos Obrigatórios": """
        Os campos obrigatórios são:
        - ID do Motorista
        - Data de Início
        - Data de Fim
        - Data de Pagamento
        - Salário Base
        - Dias Úteis Trabalhados
        - Subsídio de Alimentação / Dia
        """
    }
    
    # Use the generic bulk import tab
    entity_bulk_import_tab(
        entity_name="despesas RH",
        service_class=HRExpenseService,
        fields_config=fields_config,
        insert_method_name="insert_expense",
        help_content=help_content
    )

@handle_streamlit_error()
def main():
    """Main function to display the add HR expense page with tabs."""
    st.title("Adicionar Nova Despesa RH")
    
    # Create tabs for manual entry and bulk import
    tab1, tab2 = st.tabs(["Manual", "Ficheiro"])
    
    with tab1:
        manual_entry_tab()
    
    with tab2:
        bulk_entry_tab()

    # Link to return to list
    st.page_link(
        "sections/hr_expenses/page.py", label="Voltar à lista de Despesas RH", icon="⬅️"
    )

# Execute the main function
main()
