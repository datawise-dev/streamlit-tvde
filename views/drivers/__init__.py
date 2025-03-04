import streamlit as st
from views.drivers.form import show_driver_form
from views.drivers.list import show_driver_list

"""Main driver view combining form and list functionalities."""

st.title("Driver Management")

tab1, tab2 = st.tabs(["Add Driver", "View/Edit Drivers"])

with tab1:
    show_driver_form()
    
with tab2:
    show_driver_list()