import streamlit as st
import pandas as pd
from services.ga_expense_service import GAExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from views.ga_expenses.delete import ga_expense_delete

def ga_expense_card(expense):
    """Display a card for a G&A expense."""
    with st.container(border=True):
        col1, col2 = st.columns([8, 2])
        
        with col1:
            # Main expense info
            st.markdown(
                f"<h3 style='margin-bottom:0.5rem'>{expense['expense_type']}</h3>",
                unsafe_allow_html=True,
            )
            
            # Date information
            details_col1, details_col2, details_col3 = st.columns(3)
            
            with details_col1:
                # Amount and VAT
                st.markdown(
                    f"<strong>Amount:</strong> {expense['amount']:.2f} €",
                    unsafe_allow_html=True,
                )
                if not pd.isna(expense['vat']):
                    vat_amount = expense['amount'] * (expense['vat'] / 100)
                    st.markdown(
                        f"<strong>VAT ({expense['vat']:.1f}%):</strong> {vat_amount:.2f} €",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<strong>Total:</strong> {(expense['amount'] + vat_amount):.2f} €",
                        unsafe_allow_html=True,
                    )
            
            with details_col2:
                # Date information
                st.markdown(
                    f"<strong>Start Date:</strong> {pd.to_datetime(expense['start_date']).strftime('%d/%m/%Y')}",
                    unsafe_allow_html=True,
                )
                
                if not pd.isna(expense['end_date']):
                    st.markdown(
                        f"<strong>End Date:</strong> {pd.to_datetime(expense['end_date']).strftime('%d/%m/%Y')}",
                        unsafe_allow_html=True,
                    )
                
                if not pd.isna(expense['payment_date']):
                    st.markdown(
                        f"<strong>Payment Date:</strong> {pd.to_datetime(expense['payment_date']).strftime('%d/%m/%Y')}",
                        unsafe_allow_html=True,
                    )
            
            with details_col3:
                # Description
                if not pd.isna(expense['description']) and expense['description']:
                    st.markdown(
                        f"<strong>Description:</strong><br>{expense['description']}",
                        unsafe_allow_html=True,
                    )
        
        with col2:
            # Action buttons
            if st.button(
                "Edit",
                key=f"edit_{expense['id']}",
                type="secondary",
                icon="✏️",
                use_container_width=True,
            ):
                switch_page(f"views/ga_expenses/edit.py?id={expense['id']}")
            
            st.button(
                "Delete",
                key=f"delete_{expense['id']}",
                on_click=ga_expense_delete,
                args=(expense["id"],),
                type="secondary",
                icon="🗑️",
                use_container_width=True,
            )

@handle_streamlit_error()
def show_ga_expenses_view():
    """Display the G&A expenses management view with custom cards layout."""
    st.title("G&A Expenses Management")
    
    # Search form
    with st.form("search_ga_expenses_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_type_filter = st.selectbox(
                "Filter by Expense Type",
                options=["All", "Rental", "Licences - RNAVT", "Insurance", "Electricity", "Water", "Other"],
                index=0,
                help="Filter expenses by type"
            )
            
            description_filter = st.text_input(
                "Filter by Description",
                help="Filter expenses by description text"
            )
            
        with col2:
            date_filter_type = st.selectbox(
                "Date Filter Type",
                options=["Start/End Dates", "Payment Date"],
                index=0,
                help="Select which dates to filter by"
            )
            
            date_range = st.date_input(
                f"Filter by {date_filter_type}",
                value=[],
                help=f"Filter expenses by {date_filter_type.lower()}"
            )
        
        submit_button = st.form_submit_button("Search", use_container_width=True)
    
    # Add New G&A Expense button at the top
    st.page_link("views/ga_expenses/add.py", label="Add New G&A Expense", icon="➕", use_container_width=True)
    
    if submit_button or "ga_expenses_data_loaded" in st.session_state:
        with st.spinner("Loading data...", show_time=True):
            try:
                df = GAExpenseService.load_ga_expenses()
                # Store the loaded data in session state to persist between reruns
                st.session_state.ga_expenses_data_loaded = True
                
                if df.empty:
                    st.info("No G&A expenses registered in the system.")
                    return
                
            except Exception as e:
                st.error(f"Error loading G&A expenses: {str(e)}")
                return
        
        # Apply filters
        filtered_df = df.copy()
        
        if expense_type_filter != "All":
            filtered_df = filtered_df[filtered_df['expense_type'] == expense_type_filter]
            
        if description_filter:
            description_filter = description_filter.lower()
            filtered_df = filtered_df[
                filtered_df['description'].str.lower().str.contains(description_filter, na=False)
            ]
            
        if len(date_range) == 2:
            if date_filter_type == "Start/End Dates":
                filtered_df = filtered_df[
                    (filtered_df['start_date'] >= pd.to_datetime(date_range[0])) &
                    (
                        (filtered_df['end_date'].isna()) |
                        (filtered_df['end_date'] <= pd.to_datetime(date_range[1]))
                    )
                ]
            else:  # Payment Date
                filtered_df = filtered_df[
                    (filtered_df['payment_date'] >= pd.to_datetime(date_range[0])) &
                    (filtered_df['payment_date'] <= pd.to_datetime(date_range[1]))
                ]
        
        # Display results summary
        st.subheader(f"Results: {len(filtered_df)} G&A expenses found")
        
        # Display custom card layout for each G&A expense
        for i, (_, expense) in enumerate(filtered_df.iterrows()):
            ga_expense_card(expense)

show_ga_expenses_view()