import streamlit as st
import pandas as pd
from services.hr_expense_service import HRExpenseService

st.title("Gestão de Despesas de RH")

with st.form('search_expenses_form'):
    col1, col2, col3 = st.columns(3)

    with col1:
        driver_filter = st.text_input(
            "Filtrar por Motorista",
            help="Filtrar despesas por nome do motorista"
        )
        
    with col2:
        date_range = st.date_input(
            "Intervalo de Datas de Pagamento",
            value=[],
            help="Filtrar por data de pagamento"
        )
    
    with col3:
        month_year_filter = st.selectbox(
            "Filtrar por Mês/Ano",
            options=["Todos"] + [f"{m}/{y}" for y in range(2020, 2026) for m in range(1, 13)],
            index=0,
            help="Filtrar por mês e ano específico"
        )

    submit_button = st.form_submit_button("Pesquisar", use_container_width=True)

# Load data
with st.spinner("A carregar dados...", show_time=True):
    # try:
    # Fetch all HR expenses
    df = HRExpenseService.load_expenses()
        
if df.empty:
    st.info("Não existem despesas de RH registadas no sistema.")
    
    # Still show the add button
    st.page_link("views/hr_expense.py", label="Adicionar Nova Despesa", icon="➕")
    st.stop()

# Apply filters
filtered_df = df.copy()

if driver_filter:
    driver_filter = driver_filter.lower()
    filtered_df = filtered_df[
        filtered_df['driver_name'].str.lower().str.contains(driver_filter)
    ]
    
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['payment_date'] >= date_range[0]) &
        (filtered_df['payment_date'] <= date_range[1])
    ]
    
if month_year_filter != "Todos":
    month, year = month_year_filter.split('/')
    month, year = int(month), int(year)
    filtered_df = filtered_df[
        (filtered_df['start_date'].dt.month == month) &
        (filtered_df['start_date'].dt.year == year)
    ]

# Compute summary statistics
if not filtered_df.empty:
    st.subheader("Resumo")
    
    total_expenses = filtered_df['total_expense'].sum()
    total_base_salary = filtered_df['base_salary'].sum()
    total_meal_allowance = filtered_df['meal_allowance_total'].sum()
    total_other_benefits = filtered_df['other_benefits'].sum()
    driver_count = filtered_df['driver_id'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Despesas", f"{total_expenses:.2f} €")
    
    with col2:
        st.metric("Total Salários Base", f"{total_base_salary:.2f} €")
    
    with col3:
        st.metric("Total Subsídio Alimentação", f"{total_meal_allowance:.2f} €")
    
    with col4:
        st.metric("Motoristas", f"{driver_count}")

# Add edit link column for the dataframe
filtered_df["edit_link"] = filtered_df["id"].apply(lambda x: f"/hr_expense?id={x}")

# Prepare display columns
display_cols = [
    "edit_link", "driver_name", "start_date", "end_date", "payment_date",
    "base_salary", "working_days", "meal_allowance_per_day",
    "meal_allowance_total", "other_benefits", "total_expense"
]

# Show dataframe with clickable edit column
st.subheader("Lista de Despesas")
st.dataframe(
    filtered_df[display_cols],
    column_config={
        "driver_name": st.column_config.TextColumn(
            "Motorista", 
            width="medium"
        ),
        "start_date": st.column_config.DateColumn(
            "Data Início",
            format="DD/MM/YYYY",
            width="small"
        ),
        "end_date": st.column_config.DateColumn(
            "Data Fim",
            format="DD/MM/YYYY",
            width="small"
        ),
        "payment_date": st.column_config.DateColumn(
            "Data Pagamento",
            format="DD/MM/YYYY",
            width="small"
        ),
        "base_salary": st.column_config.NumberColumn(
            "Salário Base",
            format="%.2f €",
            width="small"
        ),
        "working_days": st.column_config.NumberColumn(
            "Dias Úteis",
            width="small"
        ),
        "meal_allowance_per_day": st.column_config.NumberColumn(
            "Subsídio/Dia",
            format="%.2f €",
            width="small"
        ),
        "meal_allowance_total": st.column_config.NumberColumn(
            "Subsídio Total",
            format="%.2f €",
            width="small"
        ),
        "other_benefits": st.column_config.NumberColumn(
            "Outros Benefícios",
            format="%.2f €",
            width="small"
        ),
        "total_expense": st.column_config.NumberColumn(
            "Total",
            format="%.2f €",
            width="small"
        ),
        "edit_link": st.column_config.LinkColumn(
            "Editar",
            width="small",
            help="Clique para editar",
            display_text="✏️",
            pinned=True
        )
    },
    use_container_width=True,
    hide_index=True
)

# Button to add a new HR expense
st.page_link("views/hr_expense.py", label="Adicionar Nova Despesa", icon="➕")