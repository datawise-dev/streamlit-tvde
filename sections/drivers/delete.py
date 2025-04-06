import streamlit as st
from sections.drivers.service import DriverService
from utils.delete_helpers import generic_record_delete


def delete_driver(driver_id):
    """Dialog to confirm driver deletion."""
    generic_record_delete(
        entity_id=driver_id,
        entity_name="motorista",
        service_class=DriverService,
        redirect_path="sections/drivers/page.py"
    )
