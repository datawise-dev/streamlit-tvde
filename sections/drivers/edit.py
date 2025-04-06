import streamlit as st
from sections.drivers.service import DriverService
from sections.drivers.form import driver_form
from sections.drivers.delete import delete_driver
from utils.page_generators import generate_edit_page

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="motorista",               # Nome em português para exibição
    entity_name_plural="motoristas",       # Plural em português para exibição
    list_page_path="sections/drivers/page.py", # URL em inglês para navegação
    form_class=driver_form,
    service_class=DriverService,
    delete_dialog=delete_driver,
    success_message="Motorista atualizado com sucesso!"
)
