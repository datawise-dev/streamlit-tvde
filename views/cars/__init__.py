from .form import show_car_form
from .list import show_car_list

def show_car_view():
    """Main car view combining form and list functionalities."""
    import streamlit as st
    
    st.title("Car Management")
    
    tab1, tab2 = st.tabs(["Add Car", "View/Edit Cars"])
    
    with tab1:
        show_car_form()
        
    with tab2:
        show_car_list()