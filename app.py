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

# Função para criar a barra lateral personalizada
def create_custom_sidebar():
    """Create a custom sidebar navigation."""
    with st.sidebar:
        st.title("Menu de Navegação")
        
        # Main pages
        st.subheader("🏠 Principal")
        st.page_link("views/home.py", label="Página Inicial")
        
        # Revenue section
        st.subheader("💰 Receitas")
        st.page_link("views/revenues.py", label="Receitas")
        
        # Management section
        st.subheader("📋 Gestão")
        st.page_link("views/drivers/page.py", label="🧑‍💼 Motoristas")
        st.page_link("views/cars/page.py", label="🚗 Veículos")
        
        # Expenses section
        st.subheader("💶 Despesas")
        st.page_link("views/hr_expenses.py", label="👥 RH")
        st.page_link("views/car_expenses.py", label="🚗 Veículos")
        st.page_link("views/ga_expenses.py", label="📊 G&A")
        
        # Help section
        st.subheader("❓ Ajuda")
        st.page_link("views/faq.py", label="Perguntas Frequentes")

@handle_streamlit_error()
def main():
    """Main application entry point."""
    # Set page config at the very start
    st.set_page_config(
        page_title="Revenue Management System",
        page_icon="💰",
        layout="wide"
    )

    # Define all pages (including hidden ones)
    pages = [
        # Main pages (visible in navigation)
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
        st.Page("views/drivers/page.py", title="Driver Management", icon="🧑‍💼", url_path="drivers"),
        st.Page("views/cars/page.py", title="Car Management", icon="🚗", url_path="cars"),
        st.Page("views/hr_expenses.py", title="HR Expenses", icon="👥", url_path="hr_expenses"),
        st.Page("views/car_expenses.py", title="Car Expenses", icon="🚗", url_path="car_expenses"),
        st.Page("views/ga_expenses.py", title="G&A Expenses", icon="📊", url_path="ga_expenses"),
        st.Page("views/faq.py", title="FAQs", icon="❓"),
        
        # Hidden pages (accessible via links)
        st.Page("views/revenues.py", title="Revenue Management", icon="💰", url_path="revenues"),
        st.Page("views/revenue.py", title="Add Revenue Item", icon="💰", url_path="revenue"),
        st.Page("views/drivers/add.py", title="Add Driver", icon="➕", url_path="drivers_add"),
        st.Page("views/drivers/edit.py", title="Edit Driver", icon="✏️", url_path="drivers_edit"),
        st.Page("views/cars/add.py", title="Add Car", icon="➕", url_path="car_add"),
        st.Page("views/cars/edit.py", title="Edit Car", icon="✏️", url_path="car_edit"),
        st.Page("views/hr_expense.py", title="Add HR Expense", icon="➕", url_path="hr_expense"),
        st.Page("views/car_expense.py", title="Add Car Expense", icon="➕", url_path="car_expense"),
        st.Page("views/ga_expense.py", title="G&A Expense", icon="➕", url_path="ga_expense")
    ]

    # Set up navigation with position="hidden" to hide default navigation
    pg = st.navigation(pages, position="hidden")
    
    # Add our custom sidebar
    create_custom_sidebar()
    
    # Run the current page
    pg.run()

if __name__ == "__main__":
    main()