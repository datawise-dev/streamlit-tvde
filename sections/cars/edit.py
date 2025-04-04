from sections.cars.service import CarService
from sections.cars.form import car_form
from sections.cars.delete import car_delete
from utils.page_generators import generate_edit_page

# Gerar a página de edição diretamente no nível do módulo
generate_edit_page(
    entity_name="carro",                   # Nome em português para exibição
    entity_name_plural="veículos",         # Plural em português para exibição
    list_page_path="sections/cars/page.py", # URL em inglês para navegação
    form_class=car_form,
    service_class=CarService,
    delete_dialog=car_delete,
    success_message="Veículo atualizado com sucesso!"
)