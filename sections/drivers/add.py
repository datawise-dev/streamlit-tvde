# Para motoristas (sections/drivers/add.py)
import streamlit as st
from sections.drivers.service import DriverService
from sections.drivers.form import driver_form
from utils.page_generators import generate_add_page

# Instruções personalizadas para importação em massa de motoristas
motoristas_help_content = {
    "Formato dos Dados": """
    Certifique-se de que:
    - O NIF tem 9 dígitos
    - O código postal segue o formato XXXX-XXX
    - O nome de exibição é único para cada motorista
    """,
    "Campos Obrigatórios": """
    Os campos obrigatórios são:
    - Nome de Exibição
    - Nome
    - Apelido
    - NIF
    """
}

# Gerar a página de adição com instruções personalizadas
generate_add_page(
    entity_name="motorista",
    entity_name_plural="motoristas",
    list_page_path="sections/drivers/page.py",
    form_class=driver_form,
    service_class=DriverService,
    bulk_import_help=motoristas_help_content,
    success_message="Motorista adicionado com sucesso!"
)
