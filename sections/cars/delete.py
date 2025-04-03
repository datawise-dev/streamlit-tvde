import streamlit as st
from sections.cars.service import CarService
from utils.delete_helpers import generic_delete_page


@st.dialog("Eliminar Veículo")
def car_delete(car_id):
    """Dialog to confirm car deletion."""
    generic_delete_page(
        car_id, "veiculo", CarService, redirect_path="sections/cars/page.py"
    )
