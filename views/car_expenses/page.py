import streamlit as st
import pandas as pd
from services.car_expense_service import CarExpenseService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from views.car_expenses.delete import car_expense_delete


def car_expense_row(expense):
    """Display a car expense as a compact row."""
    with st.container():
        # Calculate total amount
        total_amount = expense["amount"]

        # Format dates
        start_date = pd.to_datetime(expense["start_date"]).strftime("%d/%m/%Y")
        end_date = (
            pd.to_datetime(expense["end_date"]).strftime("%d/%m/%Y")
            if not pd.isna(expense["end_date"])
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
            st.caption(expense['license_plate'])

        with cols[2]:
            st.caption(f"{total_amount:.2f} €")

        with cols[3]:
            st.caption(start_date)

        with cols[4]:
            st.caption(end_date)

        with cols[5]:
            st.caption(description)

        with cols[6]:
            if st.button(
                "✏️",
                key=f"edit_{expense['id']}",
                type="tertiary",
                help="Editar esta despesa",
            ):
                switch_page(f"views/car_expenses/edit.py?id={expense['id']}")

        with cols[7]:
            st.button(
                "🗑️",
                key=f"delete_{expense['id']}",
                on_click=car_expense_delete,
                type="tertiary",
                args=(expense["id"],),
                help="Eliminar esta despesa",
            )


@handle_streamlit_error()
def show_car_expenses_view():
    """Display the car expenses management view with custom row layout."""
    st.title("Gestão de Despesas de Veículos")

    # Search form
    with st.form("search_car_expenses_form"):
        col1, col2 = st.columns(2)

        with col1:
            expense_type_filter = st.selectbox(
                "Filtrar por Tipo de Despesa",
                options=[
                    "Todos",
                    "Crédito",
                    "Combustível",
                    "Portagens",
                    "Reparações",
                    "Lavagem",
                ],
                index=0,
                help="Filtrar despesas por tipo",
            )

            license_plate_filter = st.text_input(
                "Filtrar por Matrícula",
                help="Filtrar despesas por matrícula do veículo",
            )

        with col2:
            date_filter_type = st.selectbox(
                "Tipo de Filtro de Data",
                options=["Datas de Início/Fim", "Data de Registo"],
                index=0,
                help="Selecione quais datas filtrar",
            )

            date_range = st.date_input(
                f"Filtrar por {date_filter_type}",
                value=[],
                help=f"Filtrar despesas por {date_filter_type.lower()}",
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New Car Expense button at the top
    st.page_link(
        "views/car_expenses/add.py",
        label="Adicionar Nova Despesa de Veículo",
        icon="➕",
        use_container_width=True,
    )

    if submit_button or "car_expenses_data_loaded" in st.session_state:
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = CarExpenseService.load_car_expenses()
                # Store the loaded data in session state to persist between reruns
                st.session_state.car_expenses_data_loaded = True

                if df.empty:
                    st.info("Não existem despesas de veículos registadas no sistema.")
                    return

            except Exception as e:
                st.error(f"Erro ao carregar despesas de veículos: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        # Map UI options to database values
        expense_type_map = {
            "Todos": "All",
            "Crédito": "Credit",
            "Combustível": "Gasoline",
            "Portagens": "Tolls",
            "Reparações": "Repairs",
            "Lavagem": "Washing",
        }

        if expense_type_filter != "Todos":
            english_filter = expense_type_map.get(
                expense_type_filter, expense_type_filter
            )
            filtered_df = filtered_df[filtered_df["expense_type"] == english_filter]

        if license_plate_filter:
            license_plate_filter = license_plate_filter.lower()
            filtered_df = filtered_df[
                filtered_df["license_plate"]
                .str.lower()
                .str.contains(license_plate_filter, na=False)
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
            else:  # Data de Registo
                filtered_df = filtered_df[
                    (filtered_df["created_at"] >= pd.to_datetime(date_range[0]))
                    & (filtered_df["created_at"] <= pd.to_datetime(date_range[1]))
                ]

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} despesas de veículos encontradas")

        # Map expense types to Portuguese for display
        type_map = {
            "Credit": "Crédito",
            "Gasoline": "Combustível",
            "Tolls": "Portagens",
            "Repairs": "Reparações",
            "Washing": "Lavagem",
        }

        # Table header
        header_cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
        header_cols[0].markdown("**Tipo**")
        header_cols[1].markdown("**Matrícula**")
        header_cols[2].markdown("**Montante**")
        header_cols[3].markdown("**Data de Início**")
        header_cols[4].markdown("**Data de Fim**")
        header_cols[5].markdown("**Descrição**")
        header_cols[6].markdown("**Editar**")
        header_cols[7].markdown("**Eliminar**")

        st.divider()

        # Display each car expense as a compact row
        for i, (_, expense) in enumerate(filtered_df.iterrows()):
            # Translate expense type for display if needed
            if expense["expense_type"] in type_map:
                expense_pt = expense.copy()
                expense_pt["expense_type"] = type_map[expense["expense_type"]]
                car_expense_row(expense_pt)
            else:
                car_expense_row(expense)


# Execute the function if this file is run directly
show_car_expenses_view()
