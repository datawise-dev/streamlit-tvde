# Para carros (sections/cars/add.py)
import streamlit as st
from sections.cars.service import CarService
from sections.cars.form import car_form
from utils.page_generators import generate_add_page

# Instruções personalizadas para importação em massa de veículos
carros_help_content = {
    "Formato dos Dados": """
    Certifique-se de que:
    - A matrícula segue o formato XX-XX-XX
    - A categoria do veículo é uma das seguintes: Economy, Standard, Premium, Luxury
    - A data de aquisição está no formato YYYY-MM-DD
    - O custo de aquisição é um valor numérico
    """,
    "Campos Obrigatórios": """
    Os campos obrigatórios são:
    - Matrícula
    - Marca
    - Modelo
    - Categoria
    - Data de Aquisição
    - Custo de Aquisição
    """
}

# Gerar a página de adição com instruções personalizadas
generate_add_page(
    entity_name="carro",
    entity_name_plural="veículos",
    list_page_path="sections/cars/page.py",
    form_class=car_form,
    service_class=CarService,
    bulk_import_help=carros_help_content,
    success_message="Veículo adicionado com sucesso!"
)