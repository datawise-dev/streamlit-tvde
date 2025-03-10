import streamlit as st
from datetime import date
from services.driver_service import DriverService
from services.hr_expense_service import HRExpenseService
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def hr_expense_form(existing_data=None):
    """Display form for HR expense data with error handling."""

    if existing_data is None:
        existing_data = {}
        clear_form = True

        # Set default dates to next month if creating new
        try:
            start_date, end_date = HRExpenseService.get_next_month_dates()
            existing_data["start_date"] = start_date
            existing_data["end_date"] = end_date
            existing_data["payment_date"] = end_date

            # Get default working days for next month
            working_days = HRExpenseService.get_working_days(
                start_date.year, start_date.month
            )
            existing_data["working_days"] = working_days
            existing_data["meal_allowance_per_day"] = 6.0
            existing_data["other_benefits"] = 0.0
        except Exception as e:
            existing_data["start_date"] = date.today()
            existing_data["end_date"] = date.today()
            existing_data["payment_date"] = date.today()
            existing_data["working_days"] = 20
            existing_data["meal_allowance_per_day"] = 6.0
            existing_data["other_benefits"] = 0.0
    else:
        clear_form = False  # Não limpar quando estiver em modo de edição

    data = dict()

    # Create form for HR expense data
    with st.form("hr_expense_form", clear_on_submit=clear_form):
        st.subheader("Informação da Despesa")

        # Driver selection
        try:
            drivers = DriverService.get_all_drivers()
            if not drivers:
                st.warning("Não existem motoristas registados no sistema")
                driver_options = {}
            else:
                # Create a dictionary for driver selection
                driver_options = {driver[0]: driver[1] for driver in drivers}

            default_index = 0
            if existing_data.get("driver_id") in driver_options:
                default_index = list(driver_options.keys()).index(
                    existing_data.get("driver_id")
                )

            driver_id = st.selectbox(
                "Motorista *",
                options=list(driver_options.keys()) if driver_options else [],
                format_func=lambda x: driver_options.get(x, "Selecione um motorista"),
                index=default_index if driver_options else 0,
                help="Selecione o motorista para esta despesa",
            )
            data["driver_id"] = driver_id

        except Exception as e:
            st.error(f"Erro ao carregar motoristas: {str(e)}")

        # Date information
        col1, col2, col3 = st.columns(3)

        with col1:
            data["start_date"] = st.date_input(
                "Data Início *",
                value=existing_data.get("start_date", date.today()),
                help="Data de início do período",
            )

        with col2:
            data["end_date"] = st.date_input(
                "Data Fim *",
                value=existing_data.get("end_date", date.today()),
                help="Data de fim do período",
            )

        with col3:
            data["payment_date"] = st.date_input(
                "Data de Pagamento *",
                value=existing_data.get("payment_date", date.today()),
                help="Data em que o pagamento foi/será efetuado",
            )

        # Salary information
        st.subheader("Informação Salarial")

        col1, col2 = st.columns(2)

        with col1:
            data["base_salary"] = st.number_input(
                "Salário Base (€) *",
                min_value=0.0,
                value=float(existing_data.get("base_salary", 0)),
                step=50.0,
                format="%.2f",
                help="Valor do salário base para o período",
            )

        with col2:
            data["working_days"] = st.number_input(
                "Dias Úteis Trabalhados *",
                min_value=0,
                value=int(existing_data.get("working_days", 20)),
                step=1,
                help="Número de dias úteis trabalhados no período",
            )

        # Allowances and benefits
        col1, col2 = st.columns(2)

        with col1:
            data["meal_allowance_per_day"] = st.number_input(
                "Subsídio de Alimentação / Dia (€) *",
                min_value=0.0,
                value=float(existing_data.get("meal_allowance_per_day", 6.0)),
                step=0.01,
                format="%.2f",
                help="Valor do subsídio de alimentação por dia",
            )

        with col2:
            # Other benefits
            data["other_benefits"] = st.number_input(
                "Outros Benefícios (€)",
                min_value=0.0,
                value=float(existing_data.get("other_benefits", 0)),
                step=10.0,
                format="%.2f",
                help="Outros benefícios ou compensações",
            )

        # Notes
        data["notes"] = st.text_area(
            "Notas",
            value=existing_data.get("notes", ""),
            help="Notas adicionais ou comentários sobre a despesa",
        )

        # Total calculation (displayed, not editable)
        # total_expense = data.get('base_salary', 0) + meal_allowance_total + data.get('other_benefits', 0)

        # st.info(f"**Custo Total:** {total_expense:.2f} €")

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data.get("id") else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data
