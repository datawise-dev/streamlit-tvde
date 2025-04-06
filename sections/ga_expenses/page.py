import streamlit as st
import pandas as pd
from sections.ga_expenses.service import GAExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from sections.ga_expenses.delete import delete_ga_expense, bulk_delete_ga_expenses
from sections.ga_expenses.form import expense_type_options


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
                help="Editar esta despesa",
            ):
                switch_page(f"sections/ga_expenses/edit.py?id={expense['id']}")

        with cols[7]:
            st.button(
                "🗑️",
                key=f"delete_{expense['id']}",
                on_click=delete_ga_expense,
                type="tertiary",
                args=(expense["id"], ),
                help="Eliminar esta despesa",
            )


@handle_streamlit_error()
def show_ga_expenses_view():
    """Display the G&A expenses management view with custom cards layout."""
    st.title("Gestão de Despesas G&A")
    
    # Armazenar os IDs filtrados para o botão eliminar
    filtered_ids = []

    # Search form
    with st.form("search_ga_expenses_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Adicionando "Todos" à lista de opções
            all_expense_types = ["Todos"] + expense_type_options
            expense_type_filter = st.selectbox(
                "Filtrar por Tipo de Despesa",
                options=all_expense_types,
                index=0,
                help="Filtrar despesas por tipo",
            )

            description_filter = st.text_input(
                "Filtrar por Descrição", help="Filtrar despesas por texto da descrição"
            )

        with col2:
            date_filter_type = st.selectbox(
                "Tipo de Filtro de Data",
                options=["Datas de Início/Fim", "Data de Pagamento"],
                index=0,
                help="Selecione quais datas filtrar",
            )

            date_range = st.date_input(
                f"Filtrar por {date_filter_type}",
                value=[],
                help=f"Filtrar despesas por {date_filter_type.lower()}",
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New G&A Expense and Delete All buttons side by side
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "sections/ga_expenses/add.py",
            label="Adicionar Nova Despesa G&A",
            icon="➕",
            use_container_width=True,
        )

    if submit_button or "ga_expenses_data_loaded" in st.session_state:
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = GAExpenseService.get_many()
                # Store the loaded data in session state to persist between reruns
                st.session_state.ga_expenses_data_loaded = True

                if df.empty:
                    st.info("Não existem despesas G&A registadas no sistema.")
                    return

            except Exception as e:
                st.error(f"Erro ao carregar despesas G&A: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        if expense_type_filter != "Todos":
            filt = filtered_df["expense_type"] == expense_type_filter
            filtered_df = filtered_df[filt]

        if description_filter:
            description_filter = description_filter.lower()
            filtered_df = filtered_df[
                filtered_df["description"]
                .str.lower()
                .str.contains(description_filter, na=False)
            ]

        if len(date_range) == 2:
            if date_filter_type == "Datas de Início/Fim":
                filtered_df = filtered_df[
                    (filtered_df["start_date"] >= pd.to_datetime(date_range[0]))
                    & (
                        (filtered_df["end_date"].isna())
                        | (filtered_df["end_date"] <= pd.to_datetime(date_range[1]))
                    )
                ]
            else:  # Data de Pagamento
                filtered_df = filtered_df[
                    (filtered_df["payment_date"] >= pd.to_datetime(date_range[0]))
                    & (filtered_df["payment_date"] <= pd.to_datetime(date_range[1]))
                ]
        
        # Armazenar os IDs filtrados
        filtered_ids = filtered_df["id"].tolist() if not filtered_df.empty else []
    

        # O botão de eliminar todas será exibido apenas se houver despesas filtradas
        with col2:
            if filtered_ids:
                st.button(
                    "🗑️ Eliminar Todas",
                    key="delete_all_button",
                    on_click=bulk_delete_ga_expenses,
                    type="tertiary",
                    args=(filtered_ids,),
                    help=f"Eliminar todas as {len(filtered_ids)} despesas G&A filtradas",
                    use_container_width=True,
                )

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} despesas G&A encontradas")

        # Table header
        header_cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
        header_cols[0].markdown("**Tipo/Descrição**")
        header_cols[1].markdown("**Montante**")
        header_cols[2].markdown("**Total c/IVA**")
        header_cols[3].markdown("**Data de Início**")
        header_cols[4].markdown("**Data de Fim**")
        header_cols[5].markdown("**Data de Pagamento**")
        header_cols[6].markdown("**Editar**")
        header_cols[7].markdown("**Eliminar**")

        st.divider()

        for i, (_, expense) in enumerate(filtered_df.iterrows()):
            ga_expense_row(expense)


# Execute the function if this file is run directly
show_ga_expenses_view()
