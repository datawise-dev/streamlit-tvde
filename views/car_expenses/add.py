import streamlit as st
import time
from services.car_expense_service import CarExpenseService
from views.car_expenses.form import car_expense_form
from utils.error_handlers import handle_streamlit_error
from datetime import date


@handle_streamlit_error()
def main():
    st.title("Adicionar Nova Despesa de Veículo")

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

    # Link to return to list
    st.page_link(
        "views/car_expenses/page.py",
        label="Voltar à lista de Despesas de Veículos",
        icon="⬅️",
    )


# Execute the main function
main()
