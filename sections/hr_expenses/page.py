import streamlit as st
import pandas as pd
from sections.hr_expenses.service import HRExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from sections.hr_expenses.delete import delete_hr_expense, bulk_delete_hr_expenses


def hr_expense_row(expense):
    """Display an HR expense as a compact row."""
    with st.container():
        # Calculate meal allowance total
        meal_allowance_total = (
            expense["working_days"] * expense["meal_allowance_per_day"]
        )

        # Calculate total expense
        total_expense = (
            expense["base_salary"] + meal_allowance_total + expense["other_benefits"]
        )

        # Format dates
        start_date = pd.to_datetime(expense["start_date"]).strftime("%d/%m/%Y")
        end_date = pd.to_datetime(expense["end_date"]).strftime("%d/%m/%Y")
        payment_date = pd.to_datetime(expense["payment_date"]).strftime("%d/%m/%Y")

        # Create a single row with all information
        cols = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])

        with cols[0]:
            st.write(f"**{expense['driver_name']}**")

        with cols[1]:
            st.caption(f"{expense['base_salary']:.2f} €")

        with cols[2]:
            st.caption(f"{total_expense:.2f} €")

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
                help="Editar esta despesa",
            ):
                switch_page(f"sections/hr_expenses/edit.py?id={expense['id']}")

        with cols[7]:
            st.button(
                "🗑️",
                key=f"delete_{expense['id']}",
                on_click=delete_hr_expense,
                type="tertiary",
                args=(expense["id"], ),
                help="Eliminar esta despesa",
            )


@handle_streamlit_error()
def show_hr_expenses_view():
    """Display the HR expenses management view with custom rows layout."""
    st.title("Gestão de Despesas RH")

    # Search form
    with st.form("search_hr_expenses_form"):
        col1, col2 = st.columns(2)

        with col1:
            driver_filter = st.text_input(
                "Filtrar por Motorista", help="Filtrar despesas por nome do motorista"
            )

        with col2:
            date_range = st.date_input(
                "Intervalo de Datas de Pagamento",
                value=[],
                help="Filtrar por data de pagamento",
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New HR Expense button at the top
    st.page_link(
        "sections/hr_expenses/add.py",
        label="Adicionar Nova Despesa RH",
        icon="➕",
        use_container_width=True,
    )

    if submit_button or "hr_expenses_data_loaded" in st.session_state:
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = HRExpenseService.get_many()
                # Store the loaded data in session state to persist between reruns
                st.session_state.hr_expenses_data_loaded = True

                if df.empty:
                    st.info("Não existem despesas RH registadas no sistema.")
                    return

            except Exception as e:
                st.error(f"Erro ao carregar despesas RH: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        if driver_filter:
            driver_filter = driver_filter.lower()
            filtered_df = filtered_df[
                filtered_df["driver_name"].str.lower().str.contains(driver_filter)
            ]

        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["payment_date"] >= pd.to_datetime(date_range[0]))
                & (filtered_df["payment_date"] <= pd.to_datetime(date_range[1]))
            ]

        # Store filtered IDs for bulk delete
        filtered_ids = filtered_df["id"].tolist() if not filtered_df.empty else []
        
        # Add New HR Expense and Delete All buttons side by side
        col1, col2 = st.columns(2)
        with col1:
            st.page_link(
                "sections/hr_expenses/add.py",
                label="Adicionar Nova Despesa RH",
                icon="➕",
                use_container_width=True,
            )
            
        # The delete all button will only be displayed if there are filtered expenses
        with col2:
            if filtered_ids:
                st.button(
                    "🗑️ Eliminar Todas",
                    key="delete_all_button",
                    on_click=bulk_delete_hr_expenses,
                    type="tertiary",
                    args=(filtered_ids,),
                    help=f"Eliminar todas as {len(filtered_ids)} despesas RH filtradas",
                    use_container_width=True,
                )

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} despesas encontradas")

        # Table header
        header_cols = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
        header_cols[0].markdown("**Motorista**")
        header_cols[1].markdown("**Salário Base**")
        header_cols[2].markdown("**Total**")
        header_cols[3].markdown("**Data Início**")
        header_cols[4].markdown("**Data Fim**")
        header_cols[5].markdown("**Data Pagamento**")
        header_cols[6].markdown("**Editar**")
        header_cols[7].markdown("**Eliminar**")

        st.divider()

        # Display each HR expense as a compact row
        for i, (_, expense) in enumerate(filtered_df.iterrows()):
            hr_expense_row(expense)
            # if i < len(filtered_df) - 1:
            #     st.divider()


# Execute the function if this file is run directly
show_hr_expenses_view()
