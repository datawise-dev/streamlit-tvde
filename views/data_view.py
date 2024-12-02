import streamlit as st
from services.revenue_service import RevenueService

def show_data_view():
    """Display and handle the data view."""
    st.header("View Stored Data")
    
    try:
        df = RevenueService.load_data()
        if not df.empty:
            # Add filters
            st.subheader("Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_platform = st.multiselect(
                    "Platform",
                    options=sorted(df['platform'].unique())
                )
            
            with col2:
                selected_driver = st.multiselect(
                    "Driver",
                    options=sorted(df['driver_name'].unique())
                )
            
            with col3:
                date_range = st.date_input(
                    "Date Range",
                    value=[df['start_date'].min(), df['end_date'].max()]
                )
            
            # Apply filters
            filtered_df = df.copy()
            if selected_platform:
                filtered_df = filtered_df[filtered_df['platform'].isin(selected_platform)]
            if selected_driver:
                filtered_df = filtered_df[filtered_df['driver_name'].isin(selected_driver)]
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['start_date'] >= start_date) &
                    (filtered_df['end_date'] <= end_date)
                ]
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            total_revenue = filtered_df['gross_revenue'].sum()
            total_trips = filtered_df['num_travels'].sum()
            total_km = filtered_df['num_kilometers'].sum()
            avg_commission = filtered_df['commission_percentage'].mean()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Revenue", f"${total_revenue:,.2f}")
            col2.metric("Total Trips", f"{total_trips:,}")
            col3.metric("Total KM", f"{total_km:,.1f}")
            col4.metric("Avg Commission", f"{avg_commission:.1f}%")
            
            # Display data table
            st.subheader("Detailed Data")
            st.dataframe(
                filtered_df.style.format({
                    'gross_revenue': '${:,.2f}',
                    'tip': '${:,.2f}',
                    'commission_percentage': '{:.1f}%',
                    'num_kilometers': '{:,.1f}'
                }),
                use_container_width=True
            )
            
            # Delete options
            st.subheader("Data Management")
            delete_option = st.radio(
                "Delete Options",
                ["Select Rows", "Delete All Data"]
            )
            
            if delete_option == "Select Rows":
                selected_rows = st.multiselect(
                    "Select rows to delete",
                    filtered_df.index,
                    format_func=lambda x: (
                        f"Row {x+1}: {filtered_df.iloc[x]['driver_name']} - "
                        f"{filtered_df.iloc[x]['start_date'].strftime('%Y-%m-%d')}"
                    )
                )
                
                if st.button("Delete Selected"):
                    try:
                        if RevenueService.delete_records([filtered_df.iloc[i]['id'] for i in selected_rows]):
                            st.success("Selected records deleted successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))
            
            else:  # Delete All Data
                if st.button("Delete All Filtered Data"):
                    try:
                        if st.checkbox("I understand this action cannot be undone"):
                            if RevenueService.delete_records(filtered_df['id'].tolist()):
                                st.success("All filtered data deleted successfully!")
                                st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("No data currently stored in the database.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")