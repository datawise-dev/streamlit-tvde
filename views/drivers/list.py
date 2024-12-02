import streamlit as st
import pandas as pd
from services.driver_service import DriverService
from .form import show_driver_form

def show_driver_list():
    """Display list of drivers with edit and delete options."""
    try:
        df = DriverService.load_drivers()
        if not df.empty:
            # Add filters
            st.subheader("Filters")
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.multiselect(
                    "Status",
                    options=["Active", "Inactive"],
                    default=["Active"]
                )
            
            with col2:
                date_range = st.date_input(
                    "Start Date Range",
                    value=[df['start_date'].min(), df['start_date'].max()]
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if status_filter:
                if "Active" in status_filter and "Inactive" not in status_filter:
                    filtered_df = filtered_df[filtered_df['end_date'].isna()]
                elif "Inactive" in status_filter and "Active" not in status_filter:
                    filtered_df = filtered_df[~filtered_df['end_date'].isna()]
            
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['start_date'] >= date_range[0]) &
                    (filtered_df['start_date'] <= date_range[1])
                ]

            # Display data
            st.dataframe(
                filtered_df.style.format({
                    'base_salary': '${:,.2f}',
                    'start_date': lambda x: x.strftime('%Y-%m-%d'),
                    'end_date': lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
                }),
                use_container_width=True
            )

            # Management options
            st.subheader("Manage Drivers")
            col1, col2 = st.columns(2)
            
            with col1:
                driver_to_edit = st.selectbox(
                    "Select driver to edit",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: filtered_df[filtered_df['id'] == x]['name'].iloc[0]
                )
                if st.button("Edit Selected"):
                    driver_data = DriverService.get_driver(driver_to_edit)
                    if show_driver_form(driver_data):
                        st.rerun()

            with col2:
                driver_to_delete = st.selectbox(
                    "Select driver to delete",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: filtered_df[filtered_df['id'] == x]['name'].iloc[0],
                    key="delete_driver"
                )
                if st.button("Delete Selected", key="delete_button"):
                    if st.checkbox("Confirm deletion", key="confirm_delete"):
                        try:
                            if DriverService.delete_driver(driver_to_delete):
                                st.success("Driver deleted successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting driver: {str(e)}")

            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_drivers = len(filtered_df)
                active_drivers = len(filtered_df[filtered_df['end_date'].isna()])
                st.metric("Total Drivers", f"{total_drivers}")
                st.metric("Active Drivers", f"{active_drivers}")
            
            with col2:
                total_salary = filtered_df['base_salary'].sum()
                avg_salary = filtered_df['base_salary'].mean()
                st.metric("Total Base Salary", f"${total_salary:,.2f}")
                st.metric("Average Salary", f"${avg_salary:,.2f}")
            
            with col3:
                avg_tenure = (
                    pd.to_datetime('today') - 
                    pd.to_datetime(filtered_df['start_date'])
                ).mean()
                st.metric(
                    "Average Tenure",
                    f"{avg_tenure.days / 365.25:.1f} years"
                )
        
        else:
            st.info("No drivers currently registered in the system.")
    
    except Exception as e:
        st.error(f"Error loading drivers: {str(e)}")