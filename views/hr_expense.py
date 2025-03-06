import streamlit as st
import time
from datetime import date
from services.hr_expense_service import HRExpenseService
from services.driver_service import DriverService
from utils.error_handlers import handle_streamlit_error

@st.dialog("Delete HR Expense")
@handle_streamlit_error()
def delete_expense(expense_id):
    """Dialog to confirm and delete an expense"""
    if st.button("Confirmar Eliminação"):
        with st.spinner("A eliminar despesa..."):
            HRExpenseService.delete_expense(expense_id)
        st.success("Despesa eliminada com sucesso")
        time.sleep(2)
        st.page_link("views/hr_expenses.py")

@handle_streamlit_error()
def expense_form(existing_data=None):
    """Display form for adding or editing HR expenses."""
    # Default values for new records
    if existing_data is None:
        existing_data = {}
        
        # Set default dates to next month if creating new
        try:
            start_date, end_date = HRExpenseService.get_next_month_dates()
            existing_data['start_date'] = start_date
            existing_data['end_date'] = end_date
            existing_data['payment_date'] = end_date
            
            # Get default working days for next month
            working_days = HRExpenseService.get_working_days(start_date.year, start_date.month)
            existing_data['working_days'] = working_days
            existing_data['meal_allowance_per_day'] = 6.0
            existing_data['other_benefits'] = 0.0
        except Exception as e:
            st.warning(f"Erro ao calcular valores padrão: {e}")
            existing_data['start_date'] = date.today()
            existing_data['end_date'] = date.today()
            existing_data['payment_date'] = date.today()
            existing_data['working_days'] = 20
            existing_data['meal_allowance_per_day'] = 6.0
            existing_data['other_benefits'] = 0.0

    data = {}

    # Create form for HR expense data
    with st.form("hr_expense_form", clear_on_submit=True):
        st.subheader("Informação da Despesa")

        # Driver selection
        try:
            drivers = DriverService.get_all_drivers()
            if not drivers:
                st.warning("Não existem motoristas registados no sistema")
                driver_options = {}
            else:
                # Create a dictionary for driver selection
                driver_options = {
                    driver[0]: driver[1] for driver in drivers
                }
            
            default_index = 0
            if existing_data.get('driver_id') in driver_options:
                default_index = list(driver_options.keys()).index(existing_data.get('driver_id'))
            
            driver_id = st.selectbox(
                "Motorista *",
                options=list(driver_options.keys()) if driver_options else [],
                format_func=lambda x: driver_options.get(x, "Selecione um motorista"),
                index=default_index,
                help="Selecione o motorista para esta despesa"
            )
            data["driver_id"] = driver_id
            
        except Exception as e:
            st.error(f"Erro ao carregar motoristas: {str(e)}")

        # Date information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data["start_date"] = st.date_input(
                "Data Início *",
                value=existing_data.get('start_date', date.today()),
                help="Data de início do período"
            )
            
        with col2:
            data["end_date"] = st.date_input(
                "Data Fim *",
                value=existing_data.get('end_date', date.today()),
                help="Data de fim do período"
            )
            
        with col3:
            data["payment_date"] = st.date_input(
                "Data de Pagamento *",
                value=existing_data.get('payment_date', date.today()),
                help="Data em que o pagamento foi/será efetuado"
            )
        
        # Suggest working days if dates are in same month
        try:
            if (data["start_date"].year == data["end_date"].year and 
                data["start_date"].month == data["end_date"].month):
                suggested_days = HRExpenseService.get_working_days(
                    data["start_date"].year, data["start_date"].month)
                st.info(f"Dias úteis estimados para este mês: {suggested_days}")
        except:
            pass

        # Salary information
        st.subheader("Informação Salarial")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data["base_salary"] = st.number_input(
                "Salário Base (€) *",
                min_value=0.0,
                value=float(existing_data.get('base_salary', 0)),
                step=50.0,
                format="%.2f",
                help="Valor do salário base para o período"
            )
            
        with col2:
            data["working_days"] = st.number_input(
                "Dias Úteis Trabalhados *",
                min_value=0,
                value=int(existing_data.get('working_days', 20)),
                step=1,
                help="Número de dias úteis trabalhados no período"
            )

        # Meal allowance
        # st.subheader("Subsídio de Alimentação")
        
        col1, col2 = st.columns(2)

        with col1:
            data["meal_allowance_per_day"] = st.number_input(
                "Subsídio de Alimentação / Dia (€) *",
                min_value=0.0,
                value=float(existing_data.get('meal_allowance_per_day', 6.0)),
                step=0.01,
                format="%.2f",
                help="Valor do subsídio de alimentação por dia"
            )
            
            # Show calculated total meal allowance
            meal_allowance_total = round(data["working_days"] * data["meal_allowance_per_day"], 2)
            st.info(f"Subsídio de Alimentação Total: {meal_allowance_total:.2f}€ (dias úteis × subsídio por dia)")

        with col2:
            # Other benefits
            data["other_benefits"] = st.number_input(
                "Outros Benefícios (€)",
                min_value=0.0,
                value=float(existing_data.get('other_benefits', 0)),
                step=10.0,
                format="%.2f",
                help="Outros benefícios ou compensações"
            )
        
        # Notes
        data["notes"] = st.text_area(
            "Notas",
            value=existing_data.get('notes', ''),
            help="Notas adicionais ou comentários sobre a despesa"
        )

        # Total calculation (displayed, not editable)
        total_expense = data.get('base_salary', 0) + meal_allowance_total + data.get('other_benefits', 0)
        
        st.info(f"**Custo Total:** {total_expense:.2f} €")

        # Form submission
        st.markdown("**Campos obrigatórios*")

        # Change button text based on mode
        button_text = "Atualizar" if existing_data.get('id') else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data


# Main page content
@handle_streamlit_error()
def main():
    # Main page content
    st.title("Gestão de Despesas RH")

    # Set page title based on mode
    existing_data = None
    if "id" in st.query_params:
        try:
            expense_id = int(st.query_params["id"])
            # Get expense data
            existing_data = HRExpenseService.get_expense(expense_id)
            if not existing_data:
                st.error("Despesa não encontrada.")
            else:
                st.subheader(f"Editar Despesa: {existing_data.get('driver_name', '')}")
                
                # Delete button
                if st.button("Eliminar Esta Despesa"):
                    st.warning("Tem a certeza que deseja eliminar esta despesa?")
                    delete_expense(expense_id)
        except Exception as e:
            st.error(f"Erro ao carregar informação da despesa: {str(e)}")
            existing_data = None
    else:
        st.subheader("Adicionar Nova Despesa")

    # Show the form
    try:
        submit_button, expense_data = expense_form(existing_data)
    except Exception as e:
        st.error(f"Erro ao renderizar o formulário: {str(e)}")
        st.stop()

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = ["driver_id", "start_date", "end_date", "payment_date", 
                        "base_salary", "working_days", "meal_allowance_per_day"]

        # Convert dates to strings
        for field in ['start_date', 'end_date', 'payment_date']:
            if isinstance(expense_data.get(field), date):
                expense_data[field] = expense_data[field].strftime('%Y-%m-%d')

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not expense_data.get(field):
                missing_fields.append(field)
                
        if missing_fields:
            st.error(f"Campos obrigatórios em falta: {', '.join(missing_fields)}")
            st.stop()
        
        # Validate dates
        if expense_data['end_date'] < expense_data['start_date']:
            st.error("A data de fim não pode ser anterior à data de início")
            st.stop()

        # Update or insert
        try:
            if existing_data and 'id' in existing_data:
                with st.spinner("A atualizar dados..."):
                    HRExpenseService.update_expense(existing_data['id'], expense_data)
                st.success("Despesa atualizada com sucesso!")
                st.page_link("views/hr_expenses.py", label="Voltar à lista de Despesas")
            else:
                with st.spinner("A adicionar dados..."):
                    HRExpenseService.insert_expense(expense_data)
                st.success("Despesa adicionada com sucesso!")
                time.sleep(2)
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao guardar dados: {str(e)}")

    # Link to return to list
    st.page_link("views/hr_expenses.py", label="Voltar à lista de Despesas", icon="⬅️")
