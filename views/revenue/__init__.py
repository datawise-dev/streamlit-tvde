import streamlit as st
from views.revenue.form import show_revenue_form
from views.revenue.csv_upload import show_csv_upload_view
from views.revenue.data_view import show_data_view

"""Main revenue view combining all revenue-related functionalities."""

st.title("Revenue Management")

try:
    tab1, tab2, tab3 = st.tabs(["Manual Entry", "Bulk Upload", "View Data"])
    
    with tab1:
        show_revenue_form()
        
    with tab2:
        show_csv_upload_view()
        
    with tab3:
        show_data_view()
        
except Exception as e:
    st.error(f"Application Error: {str(e)}")
    st.error("Please check your database connection settings")