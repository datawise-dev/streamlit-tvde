import streamlit as st
import time
from datetime import date
from services.hr_expense_service import HRExpenseService
from views.hr_expenses.form import hr_expense_form
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    """Main function to display the add HR expense page."""
    st.title("Adicionar Nova Despesa RH")

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
        except Exception as e:
            st.error(f"Erro ao guardar dados: {str(e)}")

    # Link to return to list
    st.page_link(
        "views/hr_expenses/page.py", label="Voltar à lista de Despesas RH", icon="⬅️"
    )


# Execute the main function
main()
