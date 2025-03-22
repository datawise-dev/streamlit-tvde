import streamlit as st
from sections.drivers.service import DriverService
from sections.cars.service import CarService
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def revenue_form(existing_data=None):
    """Display and handle the revenue entry form with simplified loading."""

    if existing_data is None:
        existing_data = {}
        clear_form = True
    else:
        clear_form = False  # Não limpar quando estiver em modo de edição

    data = {}

    # Carregar dados dos motoristas e veículos diretamente
    try:
        # Se estamos num formulário com datas existentes, usamos essas datas para filtrar motoristas ativos
        if (
            existing_data
            and "start_date" in existing_data
            and "end_date" in existing_data
        ):
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
            # Caso contrário, obtemos todos os motoristas
            active_drivers = DriverService.get_all_drivers()

        driver_options = (
            {driver[0]: f"{driver[1]}" for driver in active_drivers}
            if active_drivers
            else {}
        )

        # Carregar veículos
        cars = CarService.get_all_license_plates()
        car_options = (
            {car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars} if cars else {}
        )
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        driver_options = {}
        car_options = {}

    # Create a form for data entry
    with st.form("revenue_entry_form", clear_on_submit=clear_form):
        # Create two columns for better layout
        col1, col2 = st.columns(2)

        with col1:
            # Use existing data if available
            default_start_date = existing_data.get("start_date")
            default_end_date = existing_data.get("end_date")

            start_date = st.date_input(
                "Data Início *",
                value=default_start_date,
                help="Data de início do período de receita",
            )

            end_date = st.date_input(
                "Data Fim *",
                value=default_end_date,
                help="Data de fim do período de receita",
            )

            # Driver selection
            default_driver_index = 0
            if existing_data.get("driver_id") in driver_options:
                default_driver_index = list(driver_options.keys()).index(
                    existing_data.get("driver_id")
                )

            driver_id = st.selectbox(
                "Motorista *",
                options=list(driver_options.keys()) if driver_options else [],
                format_func=lambda x: driver_options.get(x, "Selecione um motorista"),
                index=(
                    default_driver_index
                    if driver_options and default_driver_index < len(driver_options)
                    else 0
                ),
                help="Selecione o motorista para este registo",
                disabled=not driver_options,
            )

            # Get the driver name from the selection
            driver_name = driver_options.get(driver_id, "") if driver_id else ""

            platform = st.selectbox(
                "Plataforma *",
                options=["Uber", "Bolt", "Transfer"],
                index=(
                    ["Uber", "Bolt", "Transfer"].index(
                        existing_data.get("platform", "Uber")
                    )
                    if existing_data.get("platform") in ["Uber", "Bolt", "Transfer"]
                    else 0
                ),
                help="Selecione a plataforma onde o serviço foi prestado",
            )

            commission = st.number_input(
                "Comissão (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(existing_data.get("commission_percentage", 0.0)),
                step=0.1,
                format="%.1f",
                help="Percentagem de comissão da plataforma",
            )

        with col2:
            # Car selection
            default_car_index = 0
            if existing_data.get("car_id") in car_options:
                default_car_index = list(car_options.keys()).index(
                    existing_data.get("car_id")
                )

            car_id = st.selectbox(
                "Veículo *",
                options=list(car_options.keys()) if car_options else [],
                format_func=lambda x: car_options.get(x, "Selecione um veículo"),
                index=(
                    default_car_index
                    if car_options and default_car_index < len(car_options)
                    else 0
                ),
                help="Selecione o veículo utilizado para estes serviços",
                disabled=not car_options,
            )

            # Get the license plate from the selection
            license_plate = ""
            if car_id and car_id in car_options:
                car_info = car_options.get(car_id, "")
                # Extract just the license plate from the display string
                # Format is typically "XX-XX-XX (Brand Model)"
                license_plate = car_info.split(" ")[
                    0
                ]  # Get the first part before space
            elif existing_data.get("license_plate"):
                license_plate = existing_data.get("license_plate")

            gross_revenue = st.number_input(
                "Receita Bruta *",
                min_value=0.0,
                value=float(existing_data.get("gross_revenue", 0.0)),
                step=0.01,
                format="%.2f",
                help="Receita total antes da comissão",
            )

            num_travels = st.number_input(
                "Número de Viagens *",
                min_value=0,
                value=int(existing_data.get("num_travels", 0)),
                step=1,
                help="Número total de viagens realizadas",
            )

            tip = st.number_input(
                "Gorjeta",
                min_value=0.0,
                value=float(existing_data.get("tip", 0.0)),
                step=0.01,
                format="%.2f",
                help="Total de gorjetas recebidas",
            )

            num_kms = st.number_input(
                "Número de Quilómetros *",
                min_value=0.0,
                value=float(existing_data.get("num_kilometers", 0.0)),
                step=0.1,
                format="%.1f",
                help="Distância total percorrida",
            )

        # Mark required fields
        st.markdown("**Campos obrigatórios*")

        # Add a submit button to the form
        submit_button = st.form_submit_button(
            "Atualizar" if existing_data.get("id") else "Submeter",
            use_container_width=True,
        )

    # Return the form data and submit state
    if submit_button:
        # Verificar se temos motoristas e veículos carregados
        if not driver_options:
            st.error("Não foi possível carregar a lista de motoristas.")
            return submit_button, None

        if not car_options:
            st.error("Não foi possível carregar a lista de veículos.")
            return submit_button, None

        # Prepare data dictionary
        data = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "driver_name": driver_name,
            "license_plate": license_plate,
            "platform": platform,
            "gross_revenue": gross_revenue,
            "commission_percentage": commission,
            "tip": tip,
            "num_travels": num_travels,
            "num_kilometers": num_kms,
        }

        # Add ID if it exists (for updates)
        if existing_data.get("id"):
            data["id"] = existing_data.get("id")

    return submit_button, data
