import streamlit as st
from datetime import date
from services.hr_expense_service import HRExpenseService
from sections.hr_expenses.form import hr_expense_form
from sections.hr_expenses.delete import hr_expense_delete
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    """Main function to display the edit HR expense page."""
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID da despesa RH em falta")
        st.stop()

    try:
        expense_id = int(st.query_params["id"])
        # Get expense data
        existing_data = HRExpenseService.get_expense(expense_id)
        if not existing_data:
            st.error("Despesa RH não encontrada.")
            st.stop()

        st.title(f"Editar Despesa RH: {existing_data.get('driver_name', '')}")

    except (ValueError, TypeError):
        st.error("ID de despesa RH inválido.")
        st.stop()

    submit_button, expense_data = hr_expense_form(existing_data)

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

        # Try to update the data
        try:
            with st.spinner("A atualizar dados..."):
                HRExpenseService.update_expense(expense_id, expense_data)
            st.success("Despesa RH atualizada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar dados: {str(e)}")

    # Navigation and action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "sections/hr_expenses/page.py",
            label="Voltar à lista de Despesas RH",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "Eliminar Despesa", type="tertiary", icon="🗑️", use_container_width=True
        ):
            hr_expense_delete(expense_id, existing_data.get("driver_name", ""))


# Execute the main function
main()
