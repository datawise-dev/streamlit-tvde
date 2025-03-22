import streamlit as st
from utils.error_handlers import handle_streamlit_error
from datetime import date

# Dictionary to map between Portuguese and English expense types
EXPENSE_TYPE_MAP_PT_TO_EN = {
    "Renda": "Rental",
    "Licenças - RNAVT": "Licences - RNAVT",
    "Seguro": "Insurance",
    "Eletricidade": "Electricity",
    "Água": "Water",
    "Outros": "Other"
}

EXPENSE_TYPE_MAP_EN_TO_PT = {v: k for k, v in EXPENSE_TYPE_MAP_PT_TO_EN.items()}

@handle_streamlit_error()
def ga_expense_form(existing_data=None):
    """Display form for G&A expense data with error handling."""
    
    if existing_data is None:
        existing_data = dict()
        clear_form = True
    else:
        clear_form = False  # Don't clear when in edit mode
        
    data = dict()
    
    # Create form for G&A expense data
    with st.form("ga_expense_form", clear_on_submit=clear_form):
        st.subheader("Informação da Despesa G&A")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense type selection - translated options
            expense_type_options_en = ["Rental", "Licences - RNAVT", "Insurance", "Electricity", "Water", "Other"]
            expense_type_options_pt = [EXPENSE_TYPE_MAP_EN_TO_PT.get(opt, opt) for opt in expense_type_options_en]
            
            default_type_index = 0
            if existing_data.get('expense_type') in expense_type_options_en:
                default_type_index = expense_type_options_en.index(existing_data.get('expense_type'))
            
            # Display Portuguese options, but store English values
            selected_type_pt = st.selectbox(
                "Tipo de Despesa *",
                options=expense_type_options_pt,
                index=default_type_index,
                help="Tipo de despesa G&A"
            )
            
            # Map back to English for storage
            data["expense_type"] = EXPENSE_TYPE_MAP_PT_TO_EN.get(selected_type_pt, selected_type_pt)
            
        with col2:
            data["payment_date"] = st.date_input(
                "Data de Pagamento",
                value=existing_data.get('payment_date', None),
                help="Data em que a despesa foi paga"
            )
            
        # Date information
        col1, col2 = st.columns(2)
        
        with col1:
            data["start_date"] = st.date_input(
                "Data de Início *",
                value=existing_data.get('start_date', date.today()),
                help="Quando a despesa ocorreu ou começou"
            )
            
        with col2:
            data["end_date"] = st.date_input(
                "Data de Fim",
                value=existing_data.get('end_date', None),
                help="Data de fim (se aplicável, por exemplo, para despesas baseadas em períodos)"
            )
            
        # Amount and VAT
        col1, col2 = st.columns(2)
        
        with col1:
            data["amount"] = st.number_input(
                "Montante (€) *",
                min_value=0.0,
                value=float(existing_data.get('amount', 0)),
                step=0.01,
                format="%.2f",
                help="Valor da despesa em euros"
            )
            
        with col2:
            data["vat"] = st.number_input(
                "IVA (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(existing_data.get('vat', 23.0)),
                step=0.1,
                format="%.1f",
                help="Percentagem de IVA aplicada a esta despesa"
            )
            
        # Description
        data["description"] = st.text_area(
            "Descrição / Comentários",
            value=existing_data.get('description', ''),
            help="Detalhes adicionais sobre a despesa"
        )
        
        # Form submission
        st.markdown("**Campos obrigatórios*")
        
        # Change button text based on mode
        button_text = "Atualizar" if existing_data.get('id') else "Adicionar"
        submit_button = st.form_submit_button(button_text, use_container_width=True)
        
        return submit_button, data
