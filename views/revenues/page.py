import streamlit as st
import pandas as pd
from services.revenue_service import RevenueService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from views.revenues.delete import delete_revenue_records


def revenue_row(revenue):
    """Display a revenue entry as a compact row."""
    with st.container():
        # Calculate commission amount
        commission_amount = revenue["gross_revenue"] * (
            revenue["commission_percentage"] / 100
        )

        # Calculate net revenue
        net_revenue = revenue["gross_revenue"] - commission_amount + revenue["tip"]

        # Format dates
        start_date = pd.to_datetime(revenue["start_date"]).strftime("%d/%m/%Y")
        end_date = pd.to_datetime(revenue["end_date"]).strftime("%d/%m/%Y")

        # Create a single row with all information
        cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])

        with cols[0]:
            st.write(f"**{revenue['driver_name']}** • {revenue['platform']}")
            if "license_plate" in revenue and revenue["license_plate"]:
                st.caption(f"Matrícula: {revenue['license_plate']}")

        with cols[1]:
            st.caption(f"{revenue['gross_revenue']:.2f} €")

        with cols[2]:
            st.caption(f"{revenue['commission_percentage']:.1f}%")
            st.caption(f"({commission_amount:.2f} €)")

        with cols[3]:
            st.caption(f"{net_revenue:.2f} €")

        with cols[4]:
            st.caption(start_date)
            st.caption(f"até {end_date}")

        with cols[5]:
            st.caption(f"{revenue['num_travels']} viagens")
            st.caption(f"{revenue['num_kilometers']:.1f} km")

        with cols[6]:
            if st.button(
                "✏️",
                key=f"edit_{revenue['id']}",
                type="tertiary",
                help="Editar este registo",
            ):
                switch_page(f"views/revenues/edit.py?id={revenue['id']}")

        with cols[7]:
            st.button(
                "🗑️",
                key=f"delete_{revenue['id']}",
                on_click=delete_revenue_records,
                type="tertiary",
                args=(revenue["id"],),
                help="Eliminar este registo",
            )


@handle_streamlit_error()
def show_revenues_view():
    """Display the revenue management view with custom rows layout."""
    st.title("Gestão de Receitas")

    # Filter section
    with st.form("search_revenue_form"):
        col1, col2 = st.columns(2)

        with col1:

            date_range = st.date_input(
                "Intervalo de Datas", value=[], help="Filtrar por intervalo de datas"
            )

            driver_filter = st.text_input(
                "Filtrar por Motorista", help="Filtrar por nome do motorista"
            )

        with col2:

            platform_filter = st.selectbox(
                "Plataforma",
                options=["Todas", "Uber", "Bolt", "Transfer"],
                index=0,
                help="Filtrar por plataforma de serviço",
            )

            plate_filter = st.text_input(
                "Filtrar por Matrícula", help="Filtrar por matrícula do veículo"
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New Revenue button at the top
    st.page_link(
        "views/revenues/add.py",
        label="Adicionar Nova Receita",
        icon="➕",
        use_container_width=True,
    )

    if submit_button or "revenues_data_loaded" in st.session_state:
        # Load data
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = RevenueService.load_data()
                # Store the loaded data in session state to persist between reruns
                st.session_state.revenues_data_loaded = True

                if df.empty:
                    st.info("Não foram encontrados registos de receitas no sistema.")
                    return

                # Convert date columns to pandas datetime
                for col in ["start_date", "end_date"]:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            except Exception as e:
                st.error(f"Erro ao carregar dados de receitas: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        if driver_filter:
            driver_filter = driver_filter.lower()
            filtered_df = filtered_df[
                filtered_df["driver_name"].str.lower().str.contains(driver_filter)
            ]

        if plate_filter:
            plate_filter = plate_filter.lower()
            filtered_df = filtered_df[
                filtered_df["license_plate"].str.lower().str.contains(plate_filter)
            ]

        if platform_filter != "Todas":
            filtered_df = filtered_df[filtered_df["platform"] == platform_filter]

        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["start_date"] >= pd.to_datetime(date_range[0]))
                & (filtered_df["end_date"] <= pd.to_datetime(date_range[1]))
            ]

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} registos encontrados")

        # Table header
        header_cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
        header_cols[0].markdown("**Motorista/Plataforma**")
        header_cols[1].markdown("**Receita Bruta**")
        header_cols[2].markdown("**Comissão**")
        header_cols[3].markdown("**Receita Líquida**")
        header_cols[4].markdown("**Período**")
        header_cols[5].markdown("**Viagens/Km**")
        header_cols[6].markdown("**Editar**")
        header_cols[7].markdown("**Eliminar**")

        st.divider()

        # Display each revenue as a compact row
        for i, (_, revenue) in enumerate(filtered_df.iterrows()):
            revenue_row(revenue)


# Execute the function if this file is run directly
show_revenues_view()
