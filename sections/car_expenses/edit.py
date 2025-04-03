import streamlit as st
from sections.car_expenses.service import CarExpenseService
from sections.car_expenses.form import car_expense_form
from sections.car_expenses.delete import car_expense_delete
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error
from datetime import date


@handle_streamlit_error()
def main():
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID da despesa de veículo em falta")
        st.stop()

    try:
        expense_id = int(st.query_params["id"])
        # Get expense data
        existing_data = CarExpenseService.get(expense_id)
        if not existing_data:
            st.error("Despesa de veículo não encontrada.")
            st.stop()

        st.title(f"Editar Despesa de Veículo")

    except (ValueError, TypeError):
        st.error("ID de despesa de veículo inválido.")
        st.stop()

    submit_button, expense_data = car_expense_form(existing_data)

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

        # Try to update the data
        try:
            with st.spinner("A atualizar dados..."):
                CarExpenseService.update(expense_id, expense_data)
            st.success("Despesa de veículo atualizada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar dados: {str(e)}")

    # Navigation and action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "sections/car_expenses/page.py",
            label="Voltar à lista de Despesas de Veículos",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "Eliminar Despesa", type="tertiary", icon="🗑️", use_container_width=True
        ):
            car_expense_delete(expense_id)


# Execute the main function
main()
