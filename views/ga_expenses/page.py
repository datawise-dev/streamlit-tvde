import streamlit as st
import pandas as pd
from services.ga_expense_service import GAExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from views.ga_expenses.delete import ga_expense_delete


def ga_expense_row(expense):
    """Display a G&A expense as a compact row."""
    with st.container():
        # Calculate total amount with VAT
        vat_amount = 0
        if not pd.isna(expense["vat"]):
            vat_amount = expense["amount"] * (expense["vat"] / 100)
        total_amount = expense["amount"] + vat_amount

        # Format dates
        start_date = pd.to_datetime(expense["start_date"]).strftime("%d/%m/%Y")
        end_date = (
            pd.to_datetime(expense["end_date"]).strftime("%d/%m/%Y")
            if not pd.isna(expense["end_date"])
            else ""
        )
        payment_date = (
            pd.to_datetime(expense["payment_date"]).strftime("%d/%m/%Y")
            if not pd.isna(expense["payment_date"])
            else ""
        )

        # Truncate description if too long
        description = (
            expense["description"] if not pd.isna(expense["description"]) else ""
        )
        if len(description) > 50:
            description = description[:47] + "..."

        # Create a single row with all information
        cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])

        with cols[0]:
            st.write(f"**{expense['expense_type']}**")

        with cols[1]:
            st.caption(f"{expense['amount']:.2f} €")

        with cols[2]:
            st.caption(f"{total_amount:.2f} €")

        with cols[3]:
            st.caption(start_date)

        with cols[4]:
            st.caption(end_date)

        with cols[5]:
            st.caption(payment_date)

        with cols[6]:
            if st.button(
                "✏️",
                key=f"edit_{expense['id']}",
                type="tertiary",
                help="Edit this expense",
            ):
                switch_page(f"views/ga_expenses/edit.py?id={expense['id']}")

        with cols[7]:
            st.button(
                "🗑️",
                key=f"delete_{expense['id']}",
                on_click=ga_expense_delete,
                type="tertiary",
                args=(expense["id"],),
                help="Delete this expense",
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
                options=[
                    "All",
                    "Rental",
                    "Licences - RNAVT",
                    "Insurance",
                    "Electricity",
                    "Water",
                    "Other",
                ],
                index=0,
                help="Filter expenses by type",
            )

            description_filter = st.text_input(
                "Filter by Description", help="Filter expenses by description text"
            )

        with col2:
            date_filter_type = st.selectbox(
                "Date Filter Type",
                options=["Start/End Dates", "Payment Date"],
                index=0,
                help="Select which dates to filter by",
            )

            date_range = st.date_input(
                f"Filter by {date_filter_type}",
                value=[],
                help=f"Filter expenses by {date_filter_type.lower()}",
            )

        submit_button = st.form_submit_button("Search", use_container_width=True)

    # Add New G&A Expense button at the top
    st.page_link(
        "views/ga_expenses/add.py",
        label="Add New G&A Expense",
        icon="➕",
        use_container_width=True,
    )

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
            filtered_df = filtered_df[
                filtered_df["expense_type"] == expense_type_filter
            ]

        if description_filter:
            description_filter = description_filter.lower()
            filtered_df = filtered_df[
                filtered_df["description"]
                .str.lower()
                .str.contains(description_filter, na=False)
            ]

        if len(date_range) == 2:
            if date_filter_type == "Start/End Dates":
                filtered_df = filtered_df[
                    (filtered_df["start_date"] >= pd.to_datetime(date_range[0]))
                    & (
                        (filtered_df["end_date"].isna())
                        | (filtered_df["end_date"] <= pd.to_datetime(date_range[1]))
                    )
                ]
            else:  # Payment Date
                filtered_df = filtered_df[
                    (filtered_df["payment_date"] >= pd.to_datetime(date_range[0]))
                    & (filtered_df["payment_date"] <= pd.to_datetime(date_range[1]))
                ]

        # Display results summary
        st.subheader(f"Results: {len(filtered_df)} G&A expenses found")

        # Table header
        header_cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
        header_cols[0].markdown("**Type/Description**")
        header_cols[1].markdown("**Amount**")
        header_cols[2].markdown("**Total w/VAT**")
        header_cols[3].markdown("**Start Date**")
        header_cols[4].markdown("**End Date**")
        header_cols[5].markdown("**Payment Date**")
        header_cols[6].markdown("**Edit**")
        header_cols[7].markdown("**Delete**")

        st.divider()

        # Display each G&A expense as a compact row
        for i, (_, expense) in enumerate(filtered_df.iterrows()):
            ga_expense_row(expense)


# Execute the function if this file is run directly
show_ga_expenses_view()
