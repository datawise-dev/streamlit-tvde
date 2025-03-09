import streamlit as st
from services.driver_service import DriverService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_drivers_view():
    st.title("Drivers Management")

    with st.form('search_drivers_form'):
        col1, col2 = st.columns(2)

        with col1:

            display_name_filter = st.text_input(
                "Filter by Display Name",
                help="Filter drivers by display name"
            )
            
        with col2:

            is_active_filter = st.checkbox(
                "Only Active Drivers",
                value=True,
                help="Show only active drivers"
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    if submit_button:
        with st.spinner("Loading data...", show_time=True):
            try:
                df = DriverService.load_drivers()
            except Exception as e:
                st.error(f"Erro ao carregar motoristas: {str(e)}")

            if df.empty:
                st.info("Não existem motoristas registados no sistema.")
                st.stop()


        # Apply filters
        filtered_df = df.copy()

        if display_name_filter:
            display_name_filter = display_name_filter.lower()
            filtered_df = filtered_df[
                filtered_df['display_name'].str.lower().str.contains(display_name_filter)
            ]
            
        if is_active_filter:
            filtered_df = filtered_df[filtered_df['is_active']]

        # Add edit column with emoji buttons
        filtered_df["edit"] = "✏️"

        # Prepare display columns
        display_cols = [
            "edit_link", "display_name", "first_name", "last_name", "nif", 
            "location", "postal_code", "is_active"
        ]

        filtered_df["edit_link"] = filtered_df["id"].apply(lambda x: f"/driver?id={x}")

        # Show dataframe with clickable edit column
        st.dataframe(
            filtered_df[display_cols],
            column_config={
                "is_active": st.column_config.CheckboxColumn(
                    "Active",
                    help="Driver status"
                ),
                "display_name": st.column_config.TextColumn(
                    "Display Name", 
                    width="medium"
                ),
                "first_name": st.column_config.TextColumn(
                    "First Name", 
                    width="medium"
                ),
                "last_name": st.column_config.TextColumn(
                    "Last Name", 
                    width="medium"
                ),
                "nif": st.column_config.TextColumn(
                    "NIF", 
                    width="small"
                ),
                "location": st.column_config.TextColumn(
                    "Location", 
                    width="medium"
                ),
                "postal_code": st.column_config.TextColumn(
                    "Postal Code", 
                    width="small"
                ),
                "edit_link": st.column_config.LinkColumn(
                    "Edit",
                    width="small",
                    help="Click to edit",
                    display_text="✏️",
                    pinned=True,
                )
            },
            use_container_width=True,
            hide_index=True
        )

    # Button to add a new car
    st.page_link("views/driver.py", label="Adicionar Novo Motorista", icon="➕")

show_drivers_view()