import streamlit as st
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_home_page():
    """Display a simple home page with text."""
    
    st.title("Sistema de Gestão de Receitas")
    
    st.markdown("""
    ## Bem-vindo
    
    Este é o sistema de gestão para controlo de receitas, motoristas e veículos.
    
    ### Funcionalidades Principais:
    
    * **Gestão de Receitas** - Registar e visualizar entradas de receitas
    * **Gestão de Motoristas** - Adicionar e gerir motoristas
    * **Gestão de Veículos** - Controlar a sua frota de veículos
    
    Utilize o menu lateral para navegar entre as várias secções do sistema.
    
    Para começar, selecione uma das opções no menu.
    """)

# if __name__ == "__main__":
show_home_page()