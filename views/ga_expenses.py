import streamlit as st
import pandas as pd
from services.ga_expense_service import GAExpenseService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_ga_expenses_view():
    """Display the G&A expenses management view."""
    st.title("G&A Expenses Management")

    with st.form('search_ga_expenses_form'):
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

    with st.spinner("Loading data...", show_time=True):
        try:
            # Fetch all G&A expenses from the database
            df = GAExpenseService.load_ga_expenses()
                
            if df.empty:
                st.info("No G&A expenses registered in the system.")
                # Show add button and exit
                st.page_link("views/ga_expense.py", label="Add New G&A Expense", icon="➕")
                return

        except Exception as e:
            st.error(f"Error loading G&A expenses: {str(e)}")
            st.page_link("views/ga_expense.py", label="Add New G&A Expense", icon="➕")
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
                (filtered_df['start_date'] >= date_range[0]) &
                (
                    (filtered_df['end_date'].isna()) |
                    (filtered_df['end_date'] <= date_range[1])
                )
            ]
        else:  # Payment Date
            filtered_df = filtered_df[
                (filtered_df['payment_date'] >= date_range[0]) &
                (filtered_df['payment_date'] <= date_range[1])
            ]

    # Add edit column with link to edit page
    filtered_df["edit_link"] = filtered_df["id"].apply(lambda x: f"/ga_expense?id={x}")

    # Define display columns
    display_cols = [
        "edit_link", "expense_type", "start_date", "end_date", "payment_date", "amount", "vat", "description"
    ]

    # Show dataframe with clickable edit column
    # st.subheader("G&A Expenses List")
    st.dataframe(
        filtered_df[display_cols],
        column_config={
            "expense_type": st.column_config.TextColumn(
                "Expense Type", 
                width="medium"
            ),
            "start_date": st.column_config.DateColumn(
                "Start Date",
                format="DD/MM/YYYY",
                width="small"
            ),
            "end_date": st.column_config.DateColumn(
                "End Date",
                format="DD/MM/YYYY",
                width="small"
            ),
            "payment_date": st.column_config.DateColumn(
                "Payment Date",
                format="DD/MM/YYYY",
                width="small"
            ),
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="€%.2f",
                width="small"
            ),
            "vat": st.column_config.NumberColumn(
                "VAT",
                format="%.1f%%",
                width="small"
            ),
            "description": st.column_config.TextColumn(
                "Description", 
                width="large"
            ),
            "edit_link": st.column_config.LinkColumn(
                "Edit",
                width="small",
                help="Click to edit",
                display_text="✏️",
                pinned=True
            )
        },
        use_container_width=True,
        hide_index=True
    )

    # Button to add a new G&A expense
    st.page_link("views/ga_expense.py", label="Add New G&A Expense", icon="➕")

# Execute the function if this file is run directly
show_ga_expenses_view()