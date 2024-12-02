import streamlit as st
from datetime import datetime
from services.driver_service import DriverService

def show_driver_form(existing_data: dict = None):
    """Display form for adding or editing a driver."""
    with st.form("driver_form"):
        name = st.text_input(
            "Name", 
            value=existing_data.get('name', '') if existing_data else ''
        )
        
        nif = st.text_input(
            "NIF", 
            value=existing_data.get('nif', '') if existing_data else '',
            help="Tax identification number"
        )
        
        base_salary = st.number_input(
            "Base Salary",
            min_value=0.0,
            value=float(existing_data.get('base_salary', 0)) if existing_data else 0.0,
            step=50.0,
            format="%.2f"
        )
        
        start_date = st.date_input(
            "Start Date",
            value=existing_data.get('start_date') if existing_data else datetime.now().date()
        )
        
        # End date is optional
        has_end_date = st.checkbox(
            "Set End Date", 
            value=True if existing_data and existing_data.get('end_date') else False
        )
        
        end_date = None
        if has_end_date:
            end_date = st.date_input(
                "End Date",
                value=existing_data.get('end_date') if existing_data else datetime.now().date()
            )

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not name or not nif:
                st.error("Name and NIF are required fields")
                return False
                
            if has_end_date and end_date < start_date:
                st.error("End date cannot be before start date")
                return False

            driver_data = {
                'name': name,
                'nif': nif,
                'base_salary': base_salary,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            }

            try:
                if existing_data:
                    if DriverService.update_driver(existing_data['id'], driver_data):
                        st.success("Driver updated successfully!")
                        return True
                else:
                    if DriverService.insert_driver(driver_data):
                        st.success("Driver added successfully!")
                        return True
            except Exception as e:
                st.error(str(e))
                return False

    return False