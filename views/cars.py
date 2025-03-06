import streamlit as st
import pandas as pd
from services.car_service import CarService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_cars_view():
    """Display the car management view."""
    st.title("Car Management")

    with st.form('search_cars_form'):
        col1, col2, col3 = st.columns(3)

        with col1:
            brand_filter = st.text_input(
                "Filter by Brand",
                help="Filter cars by brand name"
            )
            
        with col2:
            category_filter = st.selectbox(
                "Filter by Category",
                options=["All", "Economy", "Standard", "Premium", "Luxury"],
                index=0,
                help="Filter cars by category"
            )
            
        with col3:
            is_active_filter = st.checkbox(
                "Only Active Cars",
                value=True,
                help="Show only active cars"
            )

        submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

    with st.spinner("Loading data...", show_time=True):
        # Fetch all cars from the database
        df = CarService.load_cars()
            
        # Add 'is_active' column if it doesn't exist in the returned DataFrame
        if 'is_active' not in df.columns:
            df['is_active'] = True

        if df.empty:
            st.info("Não existem carros registados no sistema.")
            # Show add button and exit
            st.page_link("views/car.py", label="Adicionar Novo Carro", icon="➕")
            return

    # Apply filters
    filtered_df = df.copy()

    if brand_filter:
        brand_filter = brand_filter.lower()
        filtered_df = filtered_df[
            filtered_df['brand'].str.lower().str.contains(brand_filter)
        ]
        
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
        
    if is_active_filter and 'is_active' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['is_active']]

    # Add edit column with link to edit page
    filtered_df["edit_link"] = filtered_df["id"].apply(lambda x: f"/car?id={x}")

    # Define display columns
    display_cols = [
        "edit_link", "license_plate", "brand", "model", 
        "category", "acquisition_cost", "acquisition_date"
    ]

    if 'is_active' in filtered_df.columns:
        display_cols.append('is_active')

    # Show dataframe with clickable edit column
    st.dataframe(
        filtered_df[display_cols],
        column_config={
            "license_plate": st.column_config.TextColumn(
                "License Plate", 
                width="medium"
            ),
            "brand": st.column_config.TextColumn(
                "Brand", 
                width="medium"
            ),
            "model": st.column_config.TextColumn(
                "Model", 
                width="medium"
            ),
            "category": st.column_config.TextColumn(
                "Category", 
                width="medium"
            ),
            "acquisition_cost": st.column_config.NumberColumn(
                "Acquisition Cost",
                format="€%.2f",
                width="medium"
            ),
            "acquisition_date": st.column_config.DateColumn(
                "Acquisition Date",
                format="DD/MM/YYYY",
                width="medium"
            ),
            "is_active": st.column_config.CheckboxColumn(
                "Active",
                help="Car status"
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

    # Button to add a new car
    st.page_link("views/car.py", label="Adicionar Novo Carro", icon="➕")

# Execute the function
show_cars_view()