# sections/drivers/calendar.py
import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from streamlit_calendar import calendar
from sections.drivers.service import DriverService
from sections.revenues.service import RevenueService
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error
from utils.type_helpers import date_to_iso8601

@handle_streamlit_error()
def get_selected_driver():
    """
    Get selected driver from query parameters or selection form.
    
    Returns:
        Tuple of (driver_id, driver_data) or (None, None) if no driver selected
    """
    # Check for query parameter
    check_query_params()
    
    if "id" in st.query_params:
        try:
            driver_id = int(st.query_params["id"])
            driver_data = DriverService.get(driver_id)
            if driver_data:
                return driver_id, driver_data
        except (ValueError, TypeError):
            st.error("ID de motorista inválido.")
    
    # If no valid query parameter, show selection form
    st.subheader("Selecionar Motorista")
    
    # Get all active drivers
    try:
        drivers_df = DriverService.get_many(conditions={'is_active': True})
        
        if drivers_df.empty:
            st.warning("Não existem motoristas ativos no sistema.")
            return None, None
            
        # Create selection list
        driver_options = {row['id']: row['display_name'] for _, row in drivers_df.iterrows()}
        
        # Selection widget
        selected_id = st.selectbox(
            "Escolha um motorista:",
            options=list(driver_options.keys()),
            format_func=lambda x: driver_options.get(x, ""),
            key="driver_selector"
        )
        
        if st.button("Ver Calendário", use_container_width=True):
            driver_data = DriverService.get(selected_id)
            if driver_data:
                # Update URL with query param
                st.query_params["id"] = str(selected_id)
                return selected_id, driver_data
    
    except Exception as e:
        st.error(f"Erro ao carregar motoristas: {str(e)}")
    
    return None, None

@handle_streamlit_error()
def create_calendar_events(revenues_df):
    """
    Convert revenue entries to calendar events format compatible with FullCalendar.
    
    Args:
        revenues_df: DataFrame with revenue entries
        
    Returns:
        List of calendar events
    """
    events = []
    
    for _, revenue in revenues_df.iterrows():
        # Converter datas para string em formato ISO8601
        start_date = date_to_iso8601(revenue['start_date'])
        end_date = date_to_iso8601(revenue['end_date'])
        license_plate = revenue.get('license_plate', 'N/A')
        
        event = {
            # "id": str(revenue['id']),
            "title": license_plate,
            "start": start_date,
            "end": end_date,
        }
        
        events.append(event)
    
    return events

@handle_streamlit_error()
def show_driver_calendar():
    """
    Main function to display the driver calendar page using streamlit-calendar.
    """
    st.title("Calendário de Disponibilidade de Motoristas")
    
    # Get selected driver
    driver_id, driver_data = get_selected_driver()
    
    if not driver_id or not driver_data:
        return
    
    # Display driver info
    st.header(f"Calendário de {driver_data['display_name']}")
    
    # Get month and year from query params or use current date
    now = datetime.now()
    
    # Check for month parameter in format YYYYMM
    month_param = st.query_params.get("month", None)
    if month_param and len(month_param) == 6:
        try:
            year = int(month_param[:4])
            month = int(month_param[4:])
            if month < 1 or month > 12:
                month = now.month
                year = now.year
        except (ValueError, TypeError):
            month = now.month
            year = now.year
    else:
        month = now.month
        year = now.year

    month_start = f"{year:04d}-{month:02d}-01"
    # month_end = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    
    # Get revenue data for the driver
    conditions = {
        'driver_id': driver_id,
    }
    revenues_df = RevenueService.get_many(conditions=conditions)
    revenues_df = revenues_df.groupby(['start_date', 'end_date', 'license_plate'], as_index=False)[['gross_revenue', 'num_kilometers', 'num_travels']].sum()
    
    if revenues_df.empty:
        st.info(f"Não existem registos de receitas para {driver_data['display_name']}.")
        # Return to list button
        st.page_link(
            "sections/drivers/page.py",
            label="Voltar à lista de Motoristas",
            icon="⬅️",
            use_container_width=True
        )
        return
    
    options = {
        "initialDate": month_start,
        # Outras opções podem ser adicionadas aqui
        "headerToolbar": {
            "left": "",
            "center": "",
            "right": ""
        },
    }

    
    # Convert revenue data to calendar events format
    calendar_events = create_calendar_events(revenues_df)
    
    # Create and display the calendar using streamlit-calendar
    calendar_result = calendar(
        events=calendar_events,
        options=options,
        key=f"driver_calendar_{driver_id}_{year}{month:02d}"  # Include month in key to force refresh
    )
 
    
    # Return to list button
    st.page_link(
        "sections/drivers/page.py",
        label="Voltar à lista de Motoristas",
        icon="⬅️",
        use_container_width=True
    )

# Execute the main function
show_driver_calendar()