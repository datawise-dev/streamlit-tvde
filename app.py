import streamlit as st
import logging
from utils.error_handlers import handle_streamlit_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@handle_streamlit_error()
def main():
    """Main application entry point."""
    # Set page config at the very start
    st.set_page_config(
        page_title="Revenue Management System",
        page_icon="💰",
        layout="wide"
    )

    page_home    = st.Page("views/home.py", title="Home", default=True)
    page_revenue = st.Page("views/revenue/__init__.py", title="Revenue Management", url_path="revenue")
    page_drivers = st.Page("views/drivers.py", title="Driver Management", url_path="drivers")
    page_driver  = st.Page("views/driver.py", title="Add Driver", url_path="driver")
    page_cars    = st.Page("views/cars.py", title="Car Management", url_path="cars")
    page_car     = st.Page("views/car.py", title="Add Car", url_path="car")
    page_hr_expenses = st.Page("views/hr_expenses.py", title="HR Expenses", url_path="hr_expenses")
    page_hr_expense  = st.Page("views/hr_expense.py", title="Add HR Expense", url_path="hr_expense")
    page_faqs    = st.Page("views/faq.py", title="FAQs")
    
    # Use the container to display content
    pg = st.navigation([
        page_home,
        # page_revenue,
        page_driver,
        page_drivers,
        page_car,
        page_cars,
        page_hr_expense,
        page_hr_expenses,
        page_faqs
    ])

    pg.run()

if __name__ == "__main__":
    main()