import streamlit as st
from sections.car_expenses.service import CarExpenseService
from sections.car_expenses.form import car_expense_form, car_expense_types
from utils.page_generators import generate_add_page

# Instruções personalizadas para importação em massa de despesas de veículos
car_expenses_help_content = {
    "Formato dos Dados": """
    Certifique-se de que:
    - As datas estão no formato YYYY-MM-DD
    - A Data de Início não pode ser posterior à Data de Fim
    - O ID do Veículo deve corresponder a um veículo existente no sistema
    - O Tipo de Despesa deve ser um dos valores válidos
    - Para despesas do tipo 'Credit', a Data de Fim é obrigatória
    - Os valores monetários devem usar o ponto como separador decimal
    """,
    "Tipos de Despesa": f"""
    Os tipos de despesa disponíveis são:
    {', '.join(car_expense_types)}
    
    Nota: Use os valores em inglês na coluna do tipo de despesa.
    """
}

# Gerar a página de adição diretamente no nível do módulo
generate_add_page(
    entity_name="despesa de veículo",
    entity_name_plural="despesas de veículos",
    list_page_path="sections/car_expenses/page.py",
    form_class=car_expense_form,
    service_class=CarExpenseService,
    bulk_import_help=car_expenses_help_content,
    success_message="Despesa de veículo adicionada com sucesso!"
)
