import streamlit as st
from sections.ga_expenses.service import GAExpenseService
from sections.ga_expenses.form import ga_expense_form, expense_type_options
from utils.page_generators import generate_add_page

# Instruções personalizadas para importação em massa de despesas G&A
ga_expenses_help_content = {
    "Formato dos Dados": """
    Certifique-se de que:
    - As datas estão no formato YYYY-MM-DD
    - A Data de Início não pode ser posterior à Data de Fim
    - O Tipo de Despesa deve ser um dos valores válidos
    - Os valores monetários devem usar o ponto como separador decimal
    """,
    "Tipos de Despesa": f"""
    Os tipos de despesa disponíveis são:
    {', '.join(expense_type_options)}
    
    Nota: Use os valores em inglês (após o parêntesis) na coluna do tipo de despesa.
    """
}

# Gerar a página de adição diretamente no nível do módulo
generate_add_page(
    entity_name="despesa G&A",
    entity_name_plural="despesas G&A",
    list_page_path="sections/ga_expenses/page.py",
    form_class=ga_expense_form,
    service_class=GAExpenseService,
    bulk_import_help=ga_expenses_help_content,
    success_message="Despesa G&A adicionada com sucesso!"
)
