import streamlit as st
from typing import List
from sections.cars.service import CarService
from utils.delete_helpers import generic_record_delete, generic_bulk_delete


def delete_car(car_id):
    """Dialog to confirm car deletion."""
    generic_record_delete(
        entity_id=car_id,
        entity_name="veiculo",
        service_class=CarService,
        redirect_path="sections/cars/page.py"
    )

def bulk_delete_cars(car_ids: List[int]):
    """Dialog to confirm deletion of multiple cars."""
    generic_bulk_delete(
        record_ids=car_ids,
        service_class=CarService,
        entity_name="veiculo",
        session_key="cars_data_loaded"
    )
