import streamlit as st
from services.revenue_service import RevenueService
from utils.data_processing import validate_revenue_data

def show_manual_entry_view():
    """Display and handle the manual entry form."""
    st.header("Manual Data Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date")
        driver_name = st.text_input("Driver Name")
        platform = st.selectbox("Platform", ["Uber", "Bolt", "Transfer"])
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=100.0, step=0.1)
        num_travels = st.number_input("Number of Travels", min_value=0, step=1)
        
    with col2:
        end_date = st.date_input("End Date")
        license_plate = st.text_input("License Plate")
        gross_revenue = st.number_input("Gross Revenue", min_value=0.0, step=0.01)
        tip = st.number_input("Tip", min_value=0.0, step=0.01)
        num_kms = st.number_input("Number of Kilometers", min_value=0.0, step=0.1)
    
    if st.button("Submit Entry"):
        data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'driver_name': driver_name,
            'license_plate': license_plate,
            'platform': platform,
            'gross_revenue': gross_revenue,
            'commission_percentage': commission,
            'tip': tip,
            'num_travels': num_travels,
            'num_kilometers': num_kms
        }
        
        is_valid, error_message = validate_revenue_data(data)
        if not is_valid:
            st.error(error_message)
        else:
            try:
                if RevenueService.insert_revenue_data(data):
                    st.success("Data successfully inserted!")
            except Exception as e:
                st.error(str(e))