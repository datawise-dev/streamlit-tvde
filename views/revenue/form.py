import streamlit as st
from services.revenue_service import RevenueService
from services.driver_service import DriverService
from services.car_service import CarService
from utils.data_processing import validate_revenue_data
from datetime import datetime

def show_revenue_form():
    """Display and handle the manual entry form."""
    
    # Create a form for data entry
    with st.form("revenue_entry_form"):
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                help="The starting date of the revenue period"
            )
            
            end_date = st.date_input(
                "End Date",
                help="The ending date of the revenue period"
            )

            # Fetch active drivers for the selected date range
            try:
                active_drivers = DriverService.get_active_drivers(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                if not active_drivers:
                    st.warning("No active drivers found for the selected date range")
                    driver_options = []
                else:
                    # Create a dictionary for driver selection with a meaningful display format
                    driver_options = {
                        driver[0]: f"{driver[1]}" for driver in active_drivers
                    }
                
                driver_id = st.selectbox(
                    "Driver",
                    options=list(driver_options.keys()) if driver_options else [],
                    format_func=lambda x: driver_options.get(x, "Select a driver"),
                    help="Select the driver for this revenue entry"
                )
                driver_name = driver_options.get(driver_id, "") if driver_id else ""
                
            except Exception as e:
                st.error(f"Error loading drivers: {str(e)}")
                driver_name = ""
            
            platform = st.selectbox(
                "Platform",
                options=["Uber", "Bolt", "Transfer"],
                help="Select the platform where the service was provided"
            )
            
            commission = st.number_input(
                "Commission (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                help="Platform commission percentage"
            )
        
        with col2:
            # Fetch available cars
            try:
                cars = CarService.get_all_license_plates()
                if not cars:
                    st.warning("No cars available in the system")
                    car_options = []
                else:
                    # Create a dictionary for car selection with a meaningful display format
                    car_options = {
                        car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars
                    }
                
                car_id = st.selectbox(
                    "Vehicle",
                    options=list(car_options.keys()) if car_options else [],
                    format_func=lambda x: car_options.get(x, "Select a vehicle"),
                    help="Select the vehicle used for these services"
                )
                license_plate = next((car[1] for car in cars if car[0] == car_id), "") if car_id else ""
                
            except Exception as e:
                st.error(f"Error loading vehicles: {str(e)}")
                license_plate = ""
            
            gross_revenue = st.number_input(
                "Gross Revenue",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Total revenue before commission"
            )
            
            num_travels = st.number_input(
                "Number of Travels",
                min_value=0,
                step=1,
                help="Total number of trips completed"
            )
            
            tip = st.number_input(
                "Tip",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Total tips received"
            )
            
            num_kms = st.number_input(
                "Number of Kilometers",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                help="Total distance traveled"
            )

        # Add a submit button to the form
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            # Basic validation
            if not driver_name or not license_plate:
                st.error("Driver name and license plate are required fields")
                return
            
            if end_date < start_date:
                st.error("End date cannot be before start date")
                return
            
            # Prepare data dictionary
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
            
            # Additional validation through utility function
            is_valid, error_message = validate_revenue_data(data)
            if not is_valid:
                st.error(error_message)
                return
            
            # Attempt to insert data
            try:
                if RevenueService.insert_revenue_data(data):
                    st.success("Revenue data successfully inserted!")
                    
                    # Display a summary of the entered data
                    st.subheader("Entry Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Gross Revenue", f"${gross_revenue:,.2f}")
                    with col2:
                        commission_amount = gross_revenue * (commission / 100)
                        st.metric("Commission Amount", f"${commission_amount:,.2f}")
                    with col3:
                        net_revenue = gross_revenue - commission_amount + tip
                        st.metric("Net Revenue", f"${net_revenue:,.2f}")
                    
            except Exception as e:
                st.error(f"Error inserting data: {str(e)}")