import streamlit as st
import time
import pandas as pd
from services.driver_service import DriverService
from utils.error_handlers import handle_streamlit_error


@st.dialog("Eliminar Motorista")
@handle_streamlit_error()
def delete_driver(driver_id, driver_name):
    """Dialog to confirm driver deletion."""
    st.write(f"Tem a certeza que deseja eliminar o motorista **{driver_name}**?")
    st.warning("Esta ação não pode ser revertida.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.dismiss()
    with col2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            with st.spinner("A eliminar motorista...", show_time=True):
                DriverService.delete_driver(driver_id)
            st.success("Motorista eliminado com sucesso!")
            time.sleep(1.5)
            st.rerun()


def display_driver_card(driver):

    with st.container(border=True):
        col1, col2 = st.columns([8, 2])

        with col1:
            # Main driver info
            details_col1, details_col2, details_col3 = st.columns(3)
            st.markdown(f"### {driver['display_name']}")

            details_col1, details_col2, details_col3 = st.columns(3)
            with details_col1:
                st.markdown(
                    f"**Nome:** {driver['first_name']} {driver['last_name']}"
                )
                st.markdown(
                    f"**NIF:** {driver['nif'] if not pd.isna(driver['nif']) else 'N/A'}"
                )

            with details_col2:
                location_info = []
                if not pd.isna(driver["location"]) and driver["location"]:
                    location_info.append(driver["location"])
                if not pd.isna(driver["postal_code"]) and driver["postal_code"]:
                    location_info.append(driver["postal_code"])

                location_text = (
                    ", ".join(location_info) if location_info else "N/A"
                )
                st.markdown(f"**Localização:** {location_text}")

                status_color = "green" if driver["is_active"] else "gray"
                status_text = "Ativo" if driver["is_active"] else "Inativo"
                st.markdown(
                    f"**Estado:** <span style='color:{status_color};font-weight:bold'>{status_text}</span>",
                    unsafe_allow_html=True,
                )

            with details_col3:
                # Additional contact info
                if not pd.isna(driver.get("address_line1")) and driver.get(
                    "address_line1"
                ):
                    address = driver.get("address_line1", "")
                    if not pd.isna(driver.get("address_line2")) and driver.get(
                        "address_line2"
                    ):
                        address += f", {driver.get('address_line2', '')}"
                    st.markdown(f"**Morada:**\n{address}")

        with col2:
            # Action buttons
            st.link_button(
                label="Editar",
                url=f"views/driver.py?id={driver['id']}",
                icon="✏️",
                use_container_width=True,
            )
            st.button(
                "Eliminar",
                key=f"delete_{driver['id']}",
                on_click=delete_driver,
                args=(driver["id"], driver["display_name"]),
                type="secondary",
                icon="🗑️",
                use_container_width=True,
            )


@handle_streamlit_error()
def show_drivers_view():
    """Display the drivers management view with custom cards layout."""
    st.title("Gestão de Motoristas")

    # Search form
    with st.form("search_drivers_form"):
        col1, col2 = st.columns(2)

        with col1:
            display_name_filter = st.text_input(
                "Filtrar por Nome", help="Filtra motoristas pelo nome"
            )

        with col2:
            is_active_filter = st.checkbox(
                "Apenas Motoristas Ativos",
                value=True,
                help="Mostrar apenas motoristas ativos",
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    # Add New Driver button at the top
    st.page_link(
        "views/driver.py",
        label="Adicionar Novo Motorista",
        icon="➕",
        use_container_width=True,
    )

    if submit_button or "drivers_data_loaded" in st.session_state:
        with st.spinner("A carregar dados...", show_time=True):
            try:
                df = DriverService.load_drivers()
                # Store the loaded data in session state to persist between reruns
                st.session_state.drivers_data_loaded = True

                if df.empty:
                    st.info("Não existem motoristas registados no sistema.")
                    return

            except Exception as e:
                st.error(f"Erro ao carregar motoristas: {str(e)}")
                return

        # Apply filters
        filtered_df = df.copy()

        if display_name_filter:
            display_name_filter = display_name_filter.lower()
            filtered_df = filtered_df[
                filtered_df["display_name"]
                .str.lower()
                .str.contains(display_name_filter)
            ]

        if is_active_filter:
            filtered_df = filtered_df[filtered_df["is_active"]]

        # Display results summary
        st.subheader(f"Resultados: {len(filtered_df)} motoristas encontrados")

        # Display custom card layout for each driver
        for i, (_, driver) in enumerate(filtered_df.iterrows()):
            display_driver_card(driver)


# Execute the function
show_drivers_view()
