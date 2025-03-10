import streamlit as st
from services.ga_expense_service import GAExpenseService
from views.ga_expenses.form import ga_expense_form
from views.ga_expenses.delete import ga_expense_delete
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error
from datetime import date

@handle_streamlit_error()
def main():
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID da despesa G&A em falta")
        st.stop()

    try:
        expense_id = int(st.query_params["id"])
        # Get expense data
        existing_data = GAExpenseService.get_ga_expense(expense_id)
        if not existing_data:
            st.error("Despesa G&A não encontrada.")
            st.stop()
        
        st.title(f"Editar Despesa G&A")
        
    except (ValueError, TypeError):
        st.error("ID de despesa G&A inválido.")
        st.stop()

    submit_button, expense_data = ga_expense_form(existing_data)

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
        
        # Try to update the data
        try:
            with st.spinner("A atualizar dados..."):
                GAExpenseService.update_ga_expense(expense_id, expense_data)
            st.success("Despesa G&A atualizada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar dados: {str(e)}")

    # Navigation and action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("views/ga_expenses/page.py", label="Voltar à lista de Despesas G&A", icon="⬅️", use_container_width=True)
    with col2:
        if st.button("Eliminar Despesa", type="tertiary", icon="🗑️", use_container_width=True):
            ga_expense_delete(expense_id)

# Execute the main function
main()
