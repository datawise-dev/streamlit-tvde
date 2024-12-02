import streamlit as st
from views.revenue.manual_entry import show_manual_entry_view
import streamlit as st
from views.revenue import show_revenue_view
from views.drivers import show_driver_view
from views.cars import show_car_view
from views.faq import show_faq_view

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Revenue Management System",
        page_icon="💰",
        layout="centered"
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        selected_page = st.radio(
            "Select a section:",
            options=[
                "Revenue Management",
                "Driver Management",
                "Car Management",
                "FAQ"
            ],
            index=0
        )
    
    # Display content based on selection
    if selected_page == "Revenue Management":
        show_revenue_view()
    elif selected_page == "Driver Management":
        show_driver_view()
    elif selected_page == "Car Management":
        show_car_view()
    else:  # FAQ
        show_faq_view()

if __name__ == "__main__":
    main()