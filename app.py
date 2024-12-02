import streamlit as st
from views.manual_entry import show_manual_entry_view
from views.csv_upload import show_csv_upload_view
from views.data_view import show_data_view
from views.faq_view import show_faq_view

def show_main_content():
    """Display the main revenue management interface."""
    st.title("Revenue Data Management")
    
    try:
        
        # Create tabs for different sections
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

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Revenue Data Management",
        page_icon="💰",
        layout="centered"
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        selected_page = st.radio(
            "Select a section:",
            options=["Revenue Management", "FAQ"],
            index=0
        )
    
    # Display content based on selection
    if selected_page == "Revenue Management":
        show_main_content()
    else:
        show_faq_view()

if __name__ == "__main__":
    main()