import streamlit as st

def main():
    """Main application entry point."""
    # Set page config at the very start
    st.set_page_config(
        page_title="Revenue Management System",
        page_icon="💰",
        layout="centered"
    )

    page_revenue = st.Page("views/revenue/__init__.py", title="Revenue Management", url_path="revenue")
    page_drivers = st.Page("views/drivers.py", title="Driver Management")
    page_driver  = st.Page("views/driver.py", title="Add Driver")
    page_cars    = st.Page("views/cars/__init__.py", title="Car Management", url_path="cars")
    page_faqs    = st.Page("views/faq.py", title="FAQs")
    
    # Use the container to display content
    pg = st.navigation([
        # page_revenue,
        page_driver,
        page_drivers,
        # page_cars,
        # page_faqs
    ])

    pg.run()

if __name__ == "__main__":
    main()