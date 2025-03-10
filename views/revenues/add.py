import streamlit as st
from services.revenue_service import RevenueService
from views.revenues.form import revenue_form
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    """Main function to display the add revenue page."""
    st.title("Adicionar Nova Receita")
    st.subheader("Inserção Manual")

    submit_button, revenue_data = revenue_form()

    # Handle form submission
    if submit_button and revenue_data:
        # Validate using the enhanced validation system
        is_valid, errors = RevenueService.validate(revenue_data)
        if not is_valid:
            # Display all validation errors at once
            for error in errors:
                st.error(error)
            st.stop()

        # Attempt to insert data
        try:
            with st.spinner("A inserir dados..."):
                if RevenueService.insert_revenue_data(revenue_data):
                    st.success("Dados de receita inseridos com sucesso!")

                    # Display a summary of the entered data
                    st.subheader("Resumo da Entrada")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Receita Bruta", f"{revenue_data['gross_revenue']:,.2f} €"
                        )
                    with col2:
                        commission_amount = revenue_data["gross_revenue"] * (
                            revenue_data["commission_percentage"] / 100
                        )
                        st.metric("Valor da Comissão", f"{commission_amount:,.2f} €")
                    with col3:
                        net_revenue = (
                            revenue_data["gross_revenue"]
                            - commission_amount
                            + revenue_data["tip"]
                        )
                        st.metric("Receita Líquida", f"{net_revenue:,.2f} €")

                    # Botão para adicionar outra receita
                    st.page_link(
                        "views/revenues/add.py",
                        label="Adicionar Outra Receita",
                        icon="➕",
                    )
        except Exception as e:
            st.error(f"Erro ao inserir dados: {str(e)}")

    # Navigation button
    st.page_link("views/revenues/page.py", label="Voltar à lista de Receitas", icon="⬅️")


# Execute the main function
main()
