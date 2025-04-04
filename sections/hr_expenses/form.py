import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder
from sections.hr_expenses.service import HRExpenseService
from sections.drivers.service import DriverService


@handle_streamlit_error()
def hr_expense_form(existing_data=None):
    """Display form for HR expense data with error handling using FormBuilder."""

    form = FormBuilder("hr_expense_form")

    # --- Basic Expense Information ---
    form.create_section("Informação da Despesa")

    # Driver selection
    try:
        drivers = DriverService.get_many(conditions={'is_active': True})
        if drivers.empty:
            driver_options = {}
            st.warning("Não existem motoristas registados no sistema")
        else:
            # Create a dictionary for driver selection
            driver_options = {driver['id']: driver['display_name'] for _, driver in drivers.iterrows()}

        form.create_field(
            key="driver_id",
            label="Motorista",
            type="select",
            required=True,
            options=list(driver_options.keys()) if driver_options else [],
            format_func=lambda x: driver_options.get(x, "Selecione um motorista"),
            help="Selecione o motorista para esta despesa"
        )
    except Exception as e:
        st.error(f"Erro ao carregar motoristas: {str(e)}")

    # Date information
    form.create_columns(3)
    form.create_field(
        key="start_date",
        label="Data Início",
        type="date",
        required=True,
        help="Data de início do período"
    )
    
    form.create_field(
        key="end_date",
        label="Data Fim",
        type="date",
        required=True,
        help="Data de fim do período"
    )
    
    form.create_field(
        key="payment_date",
        label="Data de Pagamento",
        type="date",
        required=True,
        help="Data em que o pagamento foi/será efetuado"
    )
    form.end_columns()

    # Salary information
    form.create_section("Informação Salarial")

    form.create_columns(2)
    form.create_field(
        key="base_salary",
        label="Salário Base (€)",
        type="number",
        required=True,
        min_value=0.0,
        step=50.0,
        format="%.2f",
        help="Valor do salário base para o período"
    )
    
    form.create_field(
        key="working_days",
        label="Dias Úteis Trabalhados",
        type="number",
        required=True,
        min_value=0,
        step=1,
        help="Número de dias úteis trabalhados no período"
    )
    form.end_columns()

    # Allowances and benefits
    form.create_columns(2)
    form.create_field(
        key="meal_allowance_per_day",
        label="Subsídio de Alimentação / Dia (€)",
        type="number",
        required=True,
        min_value=0.0,
        step=0.01,
        format="%.2f",
        help="Valor do subsídio de alimentação por dia"
    )
    
    form.create_field(
        key="other_benefits",
        label="Outros Benefícios (€)",
        type="number",
        min_value=0.0,
        step=10.0,
        format="%.2f",
        default=0.0,
        help="Outros benefícios ou compensações"
    )
    form.end_columns()

    # Notes
    form.create_field(
        key="notes",
        label="Notas",
        type="textarea",
        help="Notas adicionais ou comentários sobre a despesa"
    )

    # Set default dates to next month if creating new
    if existing_data is None:
        start_date, end_date = HRExpenseService.get_next_month_dates()
        form.data["start_date"] = start_date
        form.data["end_date"] = end_date
        form.data["payment_date"] = end_date

        # Get default working days for next month
        working_days = HRExpenseService.get_working_days(
            start_date.year, start_date.month
        )
        form.data["working_days"] = working_days
        form.data["meal_allowance_per_day"] = 6.0
        form.data["other_benefits"] = 0.0
    else:
        # Populate with existing data
        for key, value in existing_data.items():
            if key in form.data:
                form.data[key] = value

    # Required fields notice
    form.create_section(None, "**Campos obrigatórios*")

    return form
