import streamlit as st
from typing import List
from sections.drivers.service import DriverService
from utils.delete_helpers import generic_record_delete, generic_bulk_delete


def delete_driver(driver_id):
    """Dialog to confirm driver deletion."""
    generic_record_delete(
        entity_id=driver_id,
        entity_name="motorista",
        service_class=DriverService,
        redirect_path="sections/drivers/page.py"
    )

def bulk_delete_drivers(driver_ids: List[int]):
    """Dialog to confirm deletion of multiple drivers."""
    generic_bulk_delete(
        record_ids=driver_ids,
        service_class=DriverService,
        entity_name="motorista",
        session_key="drivers_data_loaded"
    )
