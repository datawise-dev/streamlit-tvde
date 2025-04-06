import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder
from datetime import date
from sections.drivers.service import DriverService
from sections.cars.service import CarService

@handle_streamlit_error()
def revenue_form(existing_data=None):
    """Display form for revenue data with error handling using FormBuilder."""

    form = FormBuilder("revenue_form")

    # Period information
    form.create_section("Período e Plataforma")
    
    form.create_columns(2)
    form.create_field(
        key="start_date",
        label="Data Início",
        type="date",
        required=True,
        help="Data de início do período de receita"
    )
    
    form.create_field(
        key="end_date",
        label="Data Fim",
        type="date",
        required=True,
        help="Data de fim do período de receita"
    )
    form.end_columns()
    
    # Platform selection
    form.create_field(
        key="platform",
        label="Plataforma",
        type="select",
        required=True,
        options=["Uber", "Bolt", "Transfer"],
        help="Selecione a plataforma onde o serviço foi prestado"
    )

    # Driver and Car section
    form.create_section("Motorista e Veículo")
    
    # Load drivers
    try:
        # If we have existing dates, use them to filter active drivers
        if existing_data and "start_date" in existing_data and "end_date" in existing_data:
            start_date_str = existing_data["start_date"]
            end_date_str = existing_data["end_date"]
            
            if isinstance(start_date_str, str) and isinstance(end_date_str, str):
                active_drivers = DriverService.get_active_drivers(
                    start_date_str, end_date_str
                )
            else:
                active_drivers = DriverService.get_active_drivers(
                    start_date_str.strftime("%Y-%m-%d"),
                    end_date_str.strftime("%Y-%m-%d"),
                )
        else:
            # Otherwise, get all active drivers
            drivers_df = DriverService.get_many(conditions={'is_active': True})
            active_drivers = [(driver['id'], driver['display_name']) for _, driver in drivers_df.iterrows()]
            
        driver_options = {driver[0]: driver[1] for driver in active_drivers} if active_drivers else {}
        
        form.create_field(
            key="driver_id",
            label="Motorista",
            type="select",
            required=True,
            options=list(driver_options.keys()) if driver_options else [],
            format_func=lambda x: driver_options.get(x, "Selecione um motorista"),
            help="Selecione o motorista para este registo"
        )
        
        # Store driver name in a hidden field
        if form.data.get("driver_id") in driver_options:
            form.data["driver_name"] = driver_options[form.data["driver_id"]]
    except Exception as e:
        st.error(f"Erro ao carregar motoristas: {str(e)}")
    
    # Load cars
    try:
        cars = CarService.get_all_license_plates()
        car_options = {car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars} if cars else {}
        
        form.create_field(
            key="car_id",
            label="Veículo",
            type="select",
            required=True,
            options=list(car_options.keys()) if car_options else [],
            format_func=lambda x: car_options.get(x, "Selecione um veículo"),
            help="Selecione o veículo utilizado para estes serviços"
        )
        
        # Store license plate in a hidden field
        if form.data.get("car_id") in car_options:
            car_info = car_options[form.data["car_id"]]
            form.data["license_plate"] = car_info.split(" ")[0]
    except Exception as e:
        st.error(f"Erro ao carregar veículos: {str(e)}")

    # Revenue information
    form.create_section("Valores e Viagens")
    
    form.create_columns(2)
    form.create_field(
        key="gross_revenue",
        label="Receita Bruta",
        type="number",
        required=True,
        min_value=0.0,
        step=0.01,
        format="%.2f",
        help="Receita total antes da comissão"
    )
    
    form.create_field(
        key="commission_percentage",
        label="Comissão (%)",
        type="number",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        help="Percentagem de comissão da plataforma"
    )
    form.end_columns()
    
    form.create_columns(2)
    form.create_field(
        key="tip",
        label="Gorjeta",
        type="number",
        min_value=0.0,
        default=0.0,
        step=0.01,
        format="%.2f",
        help="Total de gorjetas recebidas"
    )
    
    form.create_field(
        key="num_travels",
        label="Número de Viagens",
        type="number",
        required=True,
        min_value=0,
        step=1,
        help="Número total de viagens realizadas"
    )
    form.end_columns()
    
    form.create_field(
        key="num_kilometers",
        label="Número de Quilómetros",
        type="number",
        required=True,
        min_value=0.0,
        step=0.1,
        format="%.1f",
        help="Distância total percorrida"
    )
    
    # Populate form with existing data if available
    if existing_data:
        for key, value in existing_data.items():
            if key in form.data:
                form.data[key] = value
    
    # Required fields notice
    form.create_section(None, "**Campos obrigatórios*")

    return form
