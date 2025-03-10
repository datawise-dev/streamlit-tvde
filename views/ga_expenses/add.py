import streamlit as st
import time
from services.ga_expense_service import GAExpenseService
from views.ga_expenses.form import ga_expense_form
from utils.error_handlers import handle_streamlit_error
from datetime import date

@handle_streamlit_error()
def main():
    st.title("Add New G&A Expense")

    submit_button, expense_data = ga_expense_form()

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
        
        # Try to insert the data
        try:
            with st.spinner("Adding data..."):
                GAExpenseService.insert_ga_expense(expense_data)
            st.success("G&A expense added successfully!")
            time.sleep(5)
            st.rerun()
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")

    # Link to return to list
    st.page_link("views/ga_expenses/page.py", label="Back to G&A Expenses List", icon="⬅️")

# Execute the main function
main()
