from .manual_entry import show_manual_entry_view
from .csv_upload import show_csv_upload_view
from .data_view import show_data_view

def show_revenue_view():
    """Main revenue view combining all revenue-related functionalities."""
    import streamlit as st
    
    st.title("Revenue Management")
    
    try:
        tab1, tab2, tab3 = st.tabs(["Manual Entry", "CSV Upload", "View Data"])
        
        with tab1:
            show_manual_entry_view()
            
        with tab2:
            show_csv_upload_view()
            
        with tab3:
            show_data_view()
            
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.error("Please check your database connection settings")