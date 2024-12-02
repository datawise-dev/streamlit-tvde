import streamlit as st
import pandas as pd
from datetime import datetime
from services.car_service import CarService
from .form import show_car_form

def show_car_list():
    """Display list of cars with edit and delete options."""
    try:
        df = CarService.load_cars()
        if not df.empty:
            # Add filters
            st.subheader("Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                brand_filter = st.multiselect(
                    "Filter by Brand",
                    options=sorted(df['brand'].unique())
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Filter by Category",
                    options=sorted(df['category'].unique())
                )
            
            with col3:
                date_range = st.date_input(
                    "Acquisition Date Range",
                    value=[df['acquisition_date'].min(), df['acquisition_date'].max()]
                )

            # Apply filters
            filtered_df = df.copy()
            if brand_filter:
                filtered_df = filtered_df[filtered_df['brand'].isin(brand_filter)]
            if category_filter:
                filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['acquisition_date'] >= date_range[0]) &
                    (filtered_df['acquisition_date'] <= date_range[1])
                ]

            # Display filtered data
            st.dataframe(
                filtered_df.style.format({
                    'acquisition_cost': '${:,.2f}',
                    'acquisition_date': lambda x: x.strftime('%Y-%m-%d')
                }),
                use_container_width=True
            )

            # Management options
            st.subheader("Manage Cars")
            col1, col2 = st.columns(2)
            
            with col1:
                car_to_edit = st.selectbox(
                    "Select car to edit",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: (
                        f"{filtered_df[filtered_df['id'] == x]['license_plate'].iloc[0]} - "
                        f"{filtered_df[filtered_df['id'] == x]['brand'].iloc[0]} "
                        f"{filtered_df[filtered_df['id'] == x]['model'].iloc[0]}"
                    )
                )
                if st.button("Edit Selected"):
                    car_data = CarService.get_car(car_to_edit)
                    if show_car_form(car_data):
                        st.rerun()

            with col2:
                car_to_delete = st.selectbox(
                    "Select car to delete",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: (
                        f"{filtered_df[filtered_df['id'] == x]['license_plate'].iloc[0]} - "
                        f"{filtered_df[filtered_df['id'] == x]['brand'].iloc[0]} "
                        f"{filtered_df[filtered_df['id'] == x]['model'].iloc[0]}"
                    ),
                    key="delete_car"
                )
                if st.button("Delete Selected", key="delete_button"):
                    if st.checkbox("Confirm deletion", key="confirm_delete"):
                        try:
                            if CarService.delete_car(car_to_delete):
                                st.success("Car deleted successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting car: {str(e)}")

            # Display summary statistics
            st.subheader("Fleet Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_value = filtered_df['acquisition_cost'].sum()
                avg_value = filtered_df['acquisition_cost'].mean()
                st.metric("Total Fleet Value", f"${total_value:,.2f}")
                st.metric("Average Vehicle Value", f"${avg_value:,.2f}")
            
            with col2:
                total_vehicles = len(filtered_df)
                vehicles_by_category = filtered_df['category'].value_counts()
                st.metric("Total Vehicles", f"{total_vehicles}")
                for category in sorted(vehicles_by_category.index):
                    st.metric(f"{category} Vehicles", f"{vehicles_by_category[category]}")
            
            with col3:
                avg_age = (
                    datetime.now().date() - 
                    pd.to_datetime(filtered_df['acquisition_date']).dt.date
                ).mean().days / 365.25
                oldest_car = (
                    datetime.now().date() - 
                    pd.to_datetime(filtered_df['acquisition_date']).dt.date
                ).max().days / 365.25
                st.metric("Average Fleet Age", f"{avg_age:.1f} years")
                st.metric("Oldest Vehicle Age", f"{oldest_car:.1f} years")
                
        else:
            st.info("No cars currently registered in the system.")
    
    except Exception as e:
        st.error(f"Error loading cars: {str(e)}")