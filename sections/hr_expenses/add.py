import streamlit as st
from sections.hr_expenses.service import HRExpenseService
from sections.hr_expenses.form import hr_expense_form
from utils.page_generators import generate_add_page

# Instruções personalizadas para importação em massa de despesas RH
hr_expenses_help_content = {
    "Formato dos Dados": """
    Certifique-se de que:
    - As datas estão no formato YYYY-MM-DD
    - A Data de Início não pode ser posterior à Data de Fim
    - O ID do Motorista deve corresponder a um motorista existente no sistema
    - Os valores monetários devem usar o ponto como separador decimal
    """,
    "Campos Obrigatórios": """
    Os campos obrigatórios são:
    - ID do Motorista
    - Data de Início
    - Data de Fim
    - Data de Pagamento
    - Salário Base
    - Dias Úteis Trabalhados
    - Subsídio de Alimentação / Dia
    """
}

# Gerar a página de adição diretamente no nível do módulo
generate_add_page(
    entity_name="despesa RH",
    entity_name_plural="despesas RH",
    list_page_path="sections/hr_expenses/page.py",
    form_class=hr_expense_form,
    service_class=HRExpenseService,
    bulk_import_help=hr_expenses_help_content,
    success_message="Despesa RH adicionada com sucesso!"
)
