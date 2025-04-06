import streamlit as st
from sections.cars.service import CarService
from utils.delete_helpers import generic_record_delete


def delete_car(car_id):
    """Dialog to confirm car deletion."""
    generic_record_delete(
        entity_id=car_id,
        entity_name="veiculo",
        service_class=CarService,
        redirect_path="sections/cars/page.py"
    )
