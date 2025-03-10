import streamlit as st
from utils.error_handlers import handle_streamlit_error
from datetime import date

@handle_streamlit_error()
def ga_expense_form(existing_data=None):
    """Display form for G&A expense data with error handling."""
    
    if existing_data is None:
        existing_data = dict()
        clear_form = True
    else:
        clear_form = False  # Don't clear when in edit mode
        
    data = dict()
    
    # Create form for G&A expense data
    with st.form("ga_expense_form", clear_on_submit=clear_form):
        st.subheader("G&A Expense Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense type selection
            expense_type_options = ["Rental", "Licences - RNAVT", "Insurance", "Electricity", "Water", "Other"]
            default_type_index = 0
            if existing_data.get('expense_type') in expense_type_options:
                default_type_index = expense_type_options.index(existing_data.get('expense_type'))
            
            data["expense_type"] = st.selectbox(
                "Expense Type *",
                options=expense_type_options,
                index=default_type_index,
                help="Type of G&A expense"
            )
            
        with col2:
            data["payment_date"] = st.date_input(
                "Payment Date",
                value=existing_data.get('payment_date', None),
                help="Date when the expense was paid"
            )
            
        # Date information
        col1, col2 = st.columns(2)
        
        with col1:
            data["start_date"] = st.date_input(
                "Start Date *",
                value=existing_data.get('start_date', date.today()),
                help="When the expense occurred or started"
            )
            
        with col2:
            data["end_date"] = st.date_input(
                "End Date",
                value=existing_data.get('end_date', None),
                help="End date (if applicable, e.g., for period-based expenses)"
            )
            
        # Amount and VAT
        col1, col2 = st.columns(2)
        
        with col1:
            data["amount"] = st.number_input(
                "Amount (€) *",
                min_value=0.0,
                value=float(existing_data.get('amount', 0)),
                step=0.01,
                format="%.2f",
                help="Cost amount in euros"
            )
            
        with col2:
            data["vat"] = st.number_input(
                "VAT (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(existing_data.get('vat', 23.0)),
                step=0.1,
                format="%.1f",
                help="VAT percentage applied to this expense"
            )
            
        # Description
        data["description"] = st.text_area(
            "Description / Comments",
            value=existing_data.get('description', ''),
            help="Additional details about the expense"
        )
        
        # Form submission
        st.markdown("**Required fields*")
        
        # Change button text based on mode
        button_text = "Update" if existing_data.get('id') else "Add"
        submit_button = st.form_submit_button(button_text, use_container_width=True)
        
        return submit_button, data