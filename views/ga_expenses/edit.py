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
        st.warning("G&A expense ID is missing")
        st.stop()

    try:
        expense_id = int(st.query_params["id"])
        # Get expense data
        existing_data = GAExpenseService.get_ga_expense(expense_id)
        if not existing_data:
            st.error("G&A expense not found.")
            st.stop()
        
        st.title(f"Edit G&A Expense")
        
    except (ValueError, TypeError):
        st.error("Invalid G&A expense ID.")
        st.stop()

    submit_button, expense_data = ga_expense_form(existing_data)

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = ["expense_type", "start_date", "amount"]
        
        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not expense_data.get(field):
                missing_fields.append(field)
                
        if missing_fields:
            st.error(f"Missing required fields: {', '.join(missing_fields)}")
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
            st.error("End date cannot be before start date")
            st.stop()
        
        # Try to update the data
        try:
            with st.spinner("Updating data..."):
                GAExpenseService.update_ga_expense(expense_id, expense_data)
            st.success("G&A expense updated successfully!")
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")

    # Navigation and action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("ga_expenses", label="Back to G&A Expenses List", icon="⬅️", use_container_width=True)
    with col2:
        if st.button("Delete Expense", type="tertiary", icon="🗑️", use_container_width=True):
            ga_expense_delete(expense_id)

# Execute the main function
main()
