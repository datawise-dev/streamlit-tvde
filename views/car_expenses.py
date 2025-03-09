import streamlit as st
import pandas as pd
from services.car_expense_service import CarExpenseService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_car_expenses_view():
    """Display the car expenses management view."""
    st.title("Car Expenses Management")

    with st.form('search_car_expenses_form'):
        col1, col2, col3 = st.columns(3)

        with col1:
            license_plate_filter = st.text_input(
                "Filter by License Plate",
                help="Filter expenses by car license plate"
            )
            
        with col2:
            expense_type_filter = st.selectbox(
                "Filter by Expense Type",
                options=["All", "Credit", "Gasoline", "Tolls", "Repairs", "Washing"],
                index=0,
                help="Filter expenses by type"
            )
            
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=[],
                help="Filter expenses by date range"
            )

        submit_button = st.form_submit_button("Search", use_container_width=True)

    if submit_button:
        with st.spinner("Loading data...", show_time=True):
            try:
                # Fetch all car expenses from the database
                df = CarExpenseService.load_car_expenses()
                    
                if df.empty:
                    st.info("No car expenses registered in the system.")
                    # Show add button and exit
                    st.page_link("views/car_expense.py", label="Add New Car Expense", icon="➕")
                    return

            except Exception as e:
                st.error(f"Error loading car expenses: {str(e)}")
                st.page_link("views/car_expense.py", label="Add New Car Expense", icon="➕")
                return

        # Apply filters
        filtered_df = df.copy()

        if license_plate_filter:
            license_plate_filter = license_plate_filter.lower()
            filtered_df = filtered_df[
                filtered_df['license_plate'].str.lower().str.contains(license_plate_filter)
            ]
            
        if expense_type_filter != "All":
            filtered_df = filtered_df[filtered_df['expense_type'] == expense_type_filter]
            
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['start_date'] >= date_range[0]) &
                (
                    (filtered_df['end_date'].isna()) |
                    (filtered_df['end_date'] <= date_range[1])
                )
            ]

        # Add edit column with link to edit page
        filtered_df["edit_link"] = filtered_df["id"].apply(lambda x: f"/car_expense?id={x}")

        # Define display columns
        display_cols = [
            "edit_link", "license_plate", "brand", "model", "expense_type", 
            "start_date", "end_date", "amount", "description"
        ]

        # Show dataframe with clickable edit column
        st.subheader("Car Expenses List")
        st.dataframe(
            filtered_df[display_cols],
            column_config={
                "license_plate": st.column_config.TextColumn(
                    "License Plate", 
                    width="medium"
                ),
                "brand": st.column_config.TextColumn(
                    "Brand", 
                    width="small"
                ),
                "model": st.column_config.TextColumn(
                    "Model", 
                    width="small"
                ),
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
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="€%.2f",
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

    # Button to add a new car expense
    st.page_link("views/car_expense.py", label="Add New Car Expense", icon="➕")

# Execute the function if this file is run directly
show_car_expenses_view()
