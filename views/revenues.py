import streamlit as st
import pandas as pd
from services.revenue_service import RevenueService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_data_view():
    """Display and handle the revenue data view section with enhanced UI."""
    st.title("Revenue Management")
    st.subheader("Revenue Records")
    
    # Filter section
    with st.form('search_revenue_form'):
        col1, col2 = st.columns(2)
        
        with col1:
           
            date_range = st.date_input(
                "Date Range",
                value=[],
                help="Filter by date range"
            )

            driver_filter = st.text_input(
                "Filter by Driver",
                help="Filter by driver name"
            )
            
        with col2:
            
            platform_filter = st.selectbox(
                "Platform",
                options=["All", "Uber", "Bolt", "Transfer"],
                index=0,
                help="Filter by service platform"
            )

            plate_filter = st.text_input(
                "Filter by License Plate",
                help="Filter by vehicle license plate"
            )
        
        submit_button = st.form_submit_button("Search", use_container_width=True)
    
    if submit_button:
        # Load data
        with st.spinner("Loading data...", show_time=True):
            try:
                df = RevenueService.load_data()
                
                if df.empty:
                    st.info("No revenue records found in the system.")
                    # Show add button and exit
                    st.page_link("views/revenue/__init__.py", label="Add New Revenue", icon="➕", tab="Manual Entry")
                    return
                    
                # Convert date columns to pandas datetime
                for col in ['start_date', 'end_date']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            except Exception as e:
                st.error(f"Error loading revenue data: {str(e)}")
                return
        
        # Apply filters
        filtered_df = df.copy()
        
        if driver_filter:
            driver_filter = driver_filter.lower()
            filtered_df = filtered_df[
                filtered_df['driver_name'].str.lower().str.contains(driver_filter)
            ]
            
        if plate_filter:
            plate_filter = plate_filter.lower()
            filtered_df = filtered_df[
                filtered_df['license_plate'].str.lower().str.contains(plate_filter)
            ]
            
        if platform_filter != "All":
            filtered_df = filtered_df[filtered_df['platform'] == platform_filter]
            
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['start_date'] >= pd.to_datetime(date_range[0])) &
                (filtered_df['end_date'] <= pd.to_datetime(date_range[1]))
            ]
        
        # Display records
        st.subheader(f"Revenue Records ({len(filtered_df)} found)")
        
        # Selection for deletion functionality 
        selection = st.checkbox("Select for Deletion")
        
        if selection:
            # Add selection column to dataframe
            filtered_df['select'] = False
            
            # Create column configuration for display
            column_config = {
                "select": st.column_config.CheckboxColumn("Select"),
                "start_date": st.column_config.DateColumn(
                    "Start Date", 
                    format="DD/MM/YYYY",
                    width="small"
                ),
                "end_date": st.column_config.DateColumn(
                    "End Date", 
                    format="DD/MM/YYYY",
                    width="small"
                ),
                "driver_name": st.column_config.TextColumn(
                    "Driver", 
                    width="medium"
                ),
                "license_plate": st.column_config.TextColumn(
                    "License Plate", 
                    width="small"
                ),
                "platform": st.column_config.TextColumn(
                    "Platform", 
                    width="small"
                ),
                "gross_revenue": st.column_config.NumberColumn(
                    "Gross Revenue", 
                    format="%.2f €",
                    width="medium"
                ),
                "commission_percentage": st.column_config.NumberColumn(
                    "Commission", 
                    format="%.2f%%",
                    width="small"
                ),
                "tip": st.column_config.NumberColumn(
                    "Tip", 
                    format="%.2f €",
                    width="small"
                ),
                "num_travels": st.column_config.NumberColumn(
                    "Trips",
                    width="small"
                ),
                "num_kilometers": st.column_config.NumberColumn(
                    "Distance", 
                    format="%.1f km",
                    width="medium"
                )
            }
            
            # Show interactive dataframe with selection
            edited_df = st.data_editor(
                filtered_df,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                disabled=filtered_df.columns.tolist() if filtered_df.empty else 
                        [col for col in filtered_df.columns if col != 'select']
            )
            
            # Get selected rows
            selected_rows = edited_df[edited_df['select']].copy()
            
            if not selected_rows.empty:
                st.warning(f"{len(selected_rows)} records selected for deletion.")
                
                if st.button("Delete Selected", type="primary"):
                    selected_ids = selected_rows['id'].tolist()
                    
                    with st.spinner("Deleting records..."):
                        if RevenueService.delete_records(selected_ids):
                            st.success(f"{len(selected_ids)} records successfully deleted.")
                            st.rerun()  # Refresh the page
                        else:
                            st.error("An error occurred while deleting records.")
        else:
            # Regular display with formatted data
            st.dataframe(
                filtered_df,
                column_config={
                    "start_date": st.column_config.DateColumn(
                        "Start Date", 
                        format="DD/MM/YYYY",
                        width="small"
                    ),
                    "end_date": st.column_config.DateColumn(
                        "End Date", 
                        format="DD/MM/YYYY",
                        width="small"
                    ),
                    "driver_name": st.column_config.TextColumn(
                        "Driver", 
                        width="medium"
                    ),
                    "license_plate": st.column_config.TextColumn(
                        "License Plate", 
                        width="small"
                    ),
                    "platform": st.column_config.TextColumn(
                        "Platform", 
                        width="small"
                    ),
                    "gross_revenue": st.column_config.NumberColumn(
                        "Gross Revenue", 
                        format="%.2f €",
                        width="medium"
                    ),
                    "commission_percentage": st.column_config.NumberColumn(
                        "Commission", 
                        format="%.2f%%",
                        width="small"
                    ),
                    "tip": st.column_config.NumberColumn(
                        "Tip", 
                        format="%.2f €",
                        width="small"
                    ),
                    "num_travels": st.column_config.NumberColumn(
                        "Trips",
                        width="small"
                    ),
                    "num_kilometers": st.column_config.NumberColumn(
                        "Distance", 
                        format="%.1f km",
                        width="medium"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

    # Button to add new revenue entry
    st.page_link("views/revenue.py", label="Add New Revenue", icon="➕")

show_data_view()
