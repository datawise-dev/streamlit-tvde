import streamlit as st
from services.revenue_service import RevenueService
from services.driver_service import DriverService
from services.car_service import CarService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_revenue_form():
    """Display and handle the manual entry form with enhanced validation and async loading."""
    
    st.subheader("Inserção Manual")
    
    # Initialize session state for driver data if it doesn't exist
    if 'driver_data_loading' not in st.session_state:
        st.session_state.driver_data_loading = False
        st.session_state.driver_options = {}
        st.session_state.driver_data_loaded = False
        
    # Initialize session state for car data if it doesn't exist
    if 'car_data_loading' not in st.session_state:
        st.session_state.car_data_loading = False
        st.session_state.car_options = {}
        st.session_state.car_data_loaded = False
    
    # Create a form for data entry
    with st.form("revenue_entry_form"):
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data Início *",
                help="Data de início do período de receita"
            )
            
            end_date = st.date_input(
                "Data Fim *",
                help="Data de fim do período de receita"
            )

            # Driver selection with loading state
            driver_placeholder = st.empty()
            
            # Always show the driver selection UI element, but it may be disabled
            driver_id = driver_placeholder.selectbox(
                "Motorista *" + (" (A carregar...)" if not st.session_state.driver_data_loaded else ""),
                options=[] if not st.session_state.driver_data_loaded else list(st.session_state.driver_options.keys()),
                format_func=lambda x: st.session_state.driver_options.get(x, "Selecione um motorista"),
                help="Selecione o motorista para este registo",
                disabled=not st.session_state.driver_data_loaded
            )
            
            # Get the driver name from the selection
            driver_name = st.session_state.driver_options.get(driver_id, "") if driver_id else ""
            
            platform = st.selectbox(
                "Plataforma *",
                options=["Uber", "Bolt", "Transfer"],
                help="Selecione a plataforma onde o serviço foi prestado"
            )
            
            commission = st.number_input(
                "Comissão (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                help="Percentagem de comissão da plataforma"
            )
        
        with col2:
            # Car selection with loading state
            car_placeholder = st.empty()
            
            # Always show the car selection UI element, but it may be disabled
            car_id = car_placeholder.selectbox(
                "Veículo *" + (" (A carregar...)" if not st.session_state.car_data_loaded else ""),
                options=[] if not st.session_state.car_data_loaded else list(st.session_state.car_options.keys()),
                format_func=lambda x: st.session_state.car_options.get(x, "Selecione um veículo"),
                help="Selecione o veículo utilizado para estes serviços",
                disabled=not st.session_state.car_data_loaded
            )
            
            # Get the license plate from the selection
            if car_id and car_id in st.session_state.car_options:
                car_info = st.session_state.car_options.get(car_id, "")
                # Extract just the license plate from the display string
                # Format is typically "XX-XX-XX (Brand Model)"
                license_plate = car_info.split(" ")[0]  # Get the first part before space
            else:
                license_plate = ""
            
            gross_revenue = st.number_input(
                "Receita Bruta *",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Receita total antes da comissão"
            )
            
            num_travels = st.number_input(
                "Número de Viagens *",
                min_value=0,
                step=1,
                help="Número total de viagens realizadas"
            )
            
            tip = st.number_input(
                "Gorjeta",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Total de gorjetas recebidas"
            )
            
            num_kms = st.number_input(
                "Número de Quilómetros *",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                help="Distância total percorrida"
            )

        # Mark required fields
        st.markdown("**Campos obrigatórios*")
            
        # Add a submit button to the form
        submit_button = st.form_submit_button("Submeter", use_container_width=True)
    
    # Load data outside the form but only once
    # This allows the form to be displayed while the data is loading
    
    # Load driver data asynchronously
    if not st.session_state.driver_data_loaded and not st.session_state.driver_data_loading:
        st.session_state.driver_data_loading = True
        
        with st.spinner("A carregar dados de motoristas..."):
            try:
                active_drivers = DriverService.get_active_drivers(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                if not active_drivers:
                    st.warning("Não existem motoristas ativos para o período selecionado")
                    st.session_state.driver_options = {}
                else:
                    # Create a dictionary for driver selection
                    st.session_state.driver_options = {
                        driver[0]: f"{driver[1]}" for driver in active_drivers
                    }
                
                st.session_state.driver_data_loaded = True
                st.session_state.driver_data_loading = False
                
                # Only rerun if car data is also loaded, otherwise wait for both to load
                if st.session_state.car_data_loaded:
                    st.rerun()  # Rerun to update the UI with loaded data
                
            except Exception as e:
                st.error(f"Erro ao carregar motoristas: {str(e)}")
                st.session_state.driver_data_loading = False
                st.session_state.driver_data_loaded = True  # Set as loaded to prevent infinite loading
    
    # Load car data asynchronously
    if not st.session_state.car_data_loaded and not st.session_state.car_data_loading:
        st.session_state.car_data_loading = True
        
        with st.spinner("A carregar dados de veículos..."):
            try:
                cars = CarService.get_all_license_plates()
                
                if not cars:
                    st.warning("Não existem veículos disponíveis no sistema")
                    st.session_state.car_options = {}
                else:
                    # Create a dictionary for car selection with a meaningful display format
                    st.session_state.car_options = {
                        car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars
                    }
                
                st.session_state.car_data_loaded = True
                st.session_state.car_data_loading = False
                
                # Only rerun if driver data is also loaded, otherwise wait for both to load
                if st.session_state.driver_data_loaded:
                    st.rerun()  # Rerun to update the UI with loaded data
                
            except Exception as e:
                st.error(f"Erro ao carregar veículos: {str(e)}")
                st.session_state.car_data_loading = False
                st.session_state.car_data_loaded = True  # Set as loaded to prevent infinite loading
    
    # Handle form submission
    if submit_button:
        # First check if all required data is loaded
        if not (st.session_state.driver_data_loaded and st.session_state.car_data_loaded):
            st.error("Aguarde o carregamento dos dados de motoristas e veículos antes de submeter.")
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
        
        # Validate using the enhanced validation system
        is_valid, errors = RevenueService.validate(data)
        if not is_valid:
            # Display all validation errors at once
            for error in errors:
                st.error(error)
            return
        
        # Attempt to insert data
        try:
            if RevenueService.insert_revenue_data(data):
                st.success("Dados de receita inseridos com sucesso!")
                
                # Display a summary of the entered data
                st.subheader("Resumo da Entrada")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Receita Bruta", f"{gross_revenue:,.2f} €")
                with col2:
                    commission_amount = gross_revenue * (commission / 100)
                    st.metric("Valor da Comissão", f"{commission_amount:,.2f} €")
                with col3:
                    net_revenue = gross_revenue - commission_amount + tip
                    st.metric("Receita Líquida", f"{net_revenue:,.2f} €")
                
                # Reset the form by clearing the session state for a new entry
                if 'driver_data_loaded' in st.session_state:
                    del st.session_state.driver_data_loaded
                if 'driver_data_loading' in st.session_state:
                    del st.session_state.driver_data_loading
                if 'driver_options' in st.session_state:
                    del st.session_state.driver_options
                    
                if 'car_data_loaded' in st.session_state:
                    del st.session_state.car_data_loaded
                if 'car_data_loading' in st.session_state:
                    del st.session_state.car_data_loading
                if 'car_options' in st.session_state:
                    del st.session_state.car_options
                    
        except Exception as e:
            st.error(f"Erro ao inserir dados: {str(e)}")
