import streamlit as st
from sections.drivers.service import DriverService
from utils.delete_helpers import generic_delete_page


@st.dialog("Eliminar Motorista")
def driver_delete(car_id):
    """Dialog to confirm driver deletion."""
    generic_delete_page(
        car_id, "motorista", DriverService, redirect_path="sections/drivers/page.py"
    )
