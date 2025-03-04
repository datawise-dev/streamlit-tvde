import streamlit as st
import pandas as pd
from services.driver_service import DriverService


st.title("Drivers Management")

# Initialize session state for editing
if 'edit_driver_id' not in st.session_state:
    st.session_state.edit_driver_id = None
    
try:
    df = DriverService.load_drivers()
    if not df.empty:
        # Add filters
        st.subheader("Filtros")
        col1, col2 = st.columns(2)
        
        with col1:
            display_name_filter = st.text_input(
                "Filter by Display Name",
                help="Filter drivers by display name"
            )
            
        with col2:
            is_active_filter = st.toggle(
                "Only Active Drivers",
                value=True,
                help="Show only active drivers"
            )
        
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
        filtered_df = filtered_df.copy()  # Create copy to avoid pandas warnings
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
                "edit_link": st.column_config.LinkColumn(
                    "Edit",
                    width="small",
                    help="Click to edit",
                    display_text="✏️",
                    pinned=True,
                ),
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
                )
            },
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.info("Não existem motoristas registados no sistema.")

except Exception as e:
    st.error(f"Erro ao carregar motoristas: {str(e)}")

