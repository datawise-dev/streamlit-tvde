from .form import show_driver_form
from .list import show_driver_list

def show_driver_view():
    """Main driver view combining form and list functionalities."""
    import streamlit as st
    
    st.title("Driver Management")
    
    tab1, tab2 = st.tabs(["Add Driver", "View/Edit Drivers"])
    
    with tab1:
        show_driver_form()
        
    with tab2:
        show_driver_list()