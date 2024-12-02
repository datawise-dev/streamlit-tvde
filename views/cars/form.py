import streamlit as st
from datetime import datetime
from services.car_service import CarService

def show_car_form(existing_data: dict = None):
    """Display form for adding or editing a car."""
    with st.form("car_form"):
        license_plate = st.text_input(
            "License Plate",
            value=existing_data.get('license_plate', '') if existing_data else ''
        )
        
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input(
                "Brand",
                value=existing_data.get('brand', '') if existing_data else ''
            )
        with col2:
            model = st.text_input(
                "Model",
                value=existing_data.get('model', '') if existing_data else ''
            )
        
        acquisition_cost = st.number_input(
            "Acquisition Cost",
            min_value=0.0,
            value=float(existing_data.get('acquisition_cost', 0)) if existing_data else 0.0,
            step=100.0,
            format="%.2f"
        )
        
        acquisition_date = st.date_input(
            "Acquisition Date",
            value=existing_data.get('acquisition_date') if existing_data else datetime.now().date()
        )
        
        category = st.selectbox(
            "Category",
            options=["Economy", "Standard", "Premium", "Luxury"],
            index=["Economy", "Standard", "Premium", "Luxury"].index(
                existing_data.get('category', 'Standard')
            ) if existing_data else 1
        )

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not license_plate or not brand or not model:
                st.error("License plate, brand, and model are required fields")
                return False

            car_data = {
                'license_plate': license_plate,
                'brand': brand,
                'model': model,
                'acquisition_cost': acquisition_cost,
                'acquisition_date': acquisition_date.strftime('%Y-%m-%d'),
                'category': category
            }

            try:
                if existing_data:
                    if CarService.update_car(existing_data['id'], car_data):
                        st.success("Car updated successfully!")
                        return True
                else:
                    if CarService.insert_car(car_data):
                        st.success("Car added successfully!")
                        return True
            except Exception as e:
                st.error(str(e))
                return False

    return False