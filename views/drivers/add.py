import streamlit as st
import time
from services.driver_service import DriverService
from views.drivers.form import driver_form

# Main view function with error handling
# """Main driver form view with error handling."""
st.title("Adicionar Motorista")

submit_button, driver_data = driver_form()

required_fields = ["display_name", "first_name", "last_name", "nif"]

if submit_button:

    for k in required_fields:
        if driver_data.get(k, ""):
            continue
        st.error("Todos os campos obrigatórios devem ser preenchidos")
        st.stop()

    try:
        with st.spinner("A adicionar dados...", show_time=True):
            DriverService.insert_driver(driver_data)
        st.success("Motorista adicionado com sucesso!")
        time.sleep(5)
        # Clear form after successful insert
        st.rerun()
    except Exception as e:
        st.error("Não foi possível adicionar o motorista.")
        st.error(str(e))

st.page_link("views/drivers.py", label="Voltar à lista de Motoristas", icon="⬅️")
