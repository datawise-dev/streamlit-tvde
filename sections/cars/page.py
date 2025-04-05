import streamlit as st
import pandas as pd
from sections.cars.service import CarService
from utils.error_handlers import handle_streamlit_error
from utils.navigation import switch_page
from sections.cars.delete import car_delete


def car_card(car):
    """Display a card with car information."""
    with st.container(border=True):
        col1, col2 = st.columns([8, 2])

        with col1:
            # Main car info
            st.markdown(
                f"<h3 style='margin-bottom:0.5rem'>{car['license_plate']}</h3>",
                unsafe_allow_html=True,
            )

            details_col1, details_col2, details_col3 = st.columns(3)
            with details_col1:
                st.markdown(
                    f"<strong>Marca/Modelo:</strong> {car['brand']} {car['model']}",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<strong>Categoria:</strong> {car['category']}",
                    unsafe_allow_html=True,
                )

            with details_col2:
                st.markdown(
                    f"<strong>Data de Aquisição:</strong> {car['acquisition_date'].strftime('%d/%m/%Y') if pd.notna(car['acquisition_date']) else 'N/A'}",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<strong>Custo:</strong> {car['acquisition_cost']:,.2f}€",
                    unsafe_allow_html=True,
                )

            with details_col3:
                # Status information
                if "is_active" in car:
                    status_color = "#2E7D32" if car["is_active"] else "#757575"
                    status_text = "Ativo" if car["is_active"] else "Inativo"
                    status_icon = "✅" if car["is_active"] else "❌"
                    st.markdown(
                        f"<strong>Estado:</strong> <span style='color:{status_color};font-weight:bold'>{status_icon} {status_text}</span>",
                        unsafe_allow_html=True,
                    )

        with col2:
            # Action buttons
            if st.button(
                "Editar",
                key=f"edit_{car['id']}",
                type="secondary",
                icon="✏️",
                use_container_width=True,
            ):
                switch_page(f"sections/cars/edit.py?id={car['id']}")

            st.button(
                "Eliminar",
                key=f"delete_{car['id']}",
                on_click=car_delete,
                args=(car["id"], ),
                type="secondary",
                icon="🗑️",
                use_container_width=True,
            )


@handle_streamlit_error()
def show_cars_view():
    """Display the car management view with custom cards layout."""
    st.title("Gestão de Veículos")

    # Search form
    with st.form("search_cars_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            brand_filter = st.text_input(
                "Filtrar por Marca", help="Filtrar veículos por marca"
            )

        with col2:
            category_filter = st.selectbox(
                "Filtrar por Categoria",
                options=["Todas", "Economy", "Standard", "Premium", "Luxury"],
                index=0,
                help="Filtrar veículos por categoria",
            )

        with col3:
            is_active_filter = st.checkbox(
                "Apenas Veículos Ativos",
                value=True,
                help="Mostrar apenas veículos ativos",
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New Car button at the top
    st.page_link(
        "sections/cars/add.py",
        label="Adicionar Novo Veículo",
        icon="➕",
        use_container_width=True,
    )

    if submit_button or "cars_data_loaded" in st.session_state:
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = CarService.get_many()
                # Store the loaded data in session state to persist between reruns
                st.session_state.cars_data_loaded = True

                # Add 'is_active' column if it doesn't exist in the returned DataFrame
                if "is_active" not in df.columns:
                    df["is_active"] = True

                if df.empty:
                    st.info("Não existem veículos registados no sistema.")
                    return

            except Exception as e:
                st.error(f"Erro ao carregar veículos: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        if brand_filter:
            brand_filter = brand_filter.lower()
            filtered_df = filtered_df[
                filtered_df["brand"].str.lower().str.contains(brand_filter)
            ]

        if category_filter != "Todas":
            filtered_df = filtered_df[filtered_df["category"] == category_filter]

        if is_active_filter and "is_active" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["is_active"]]

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} veículos encontrados")

        # Display custom card layout for each car
        for i, (_, car) in enumerate(filtered_df.iterrows()):
            car_card(car)


# Execute the function
show_cars_view()
