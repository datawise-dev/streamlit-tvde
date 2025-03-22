import streamlit as st
from sections.revenues.service import RevenueService
from sections.revenues.form import revenue_form
from sections.revenues.delete import delete_revenue_records
from utils.navigation import check_query_params
from utils.error_handlers import handle_streamlit_error


@handle_streamlit_error()
def main():
    """Main function to display the edit revenue page."""
    check_query_params()

    if "id" not in st.query_params:
        st.warning("ID da receita em falta")
        st.stop()

    try:
        revenue_id = int(st.query_params["id"])
        # Get revenue data
        existing_data = RevenueService.get_revenue(revenue_id)
        if not existing_data:
            st.error("Receita não encontrada.")
            st.stop()

        st.title(f"Editar Receita")
        st.subheader(
            f"Motorista: {existing_data.get('driver_name', '')} | Plataforma: {existing_data.get('platform', '')}"
        )

    except (ValueError, TypeError):
        st.error("ID de receita inválido.")
        st.stop()

    submit_button, revenue_data = revenue_form(existing_data)

    # Handle form submission
    if submit_button and revenue_data:
        # Validate using the enhanced validation system
        is_valid, errors = RevenueService.validate(revenue_data)
        if not is_valid:
            # Display all validation errors at once
            for error in errors:
                st.error(error)
            st.stop()

        # Attempt to update data
        try:
            with st.spinner("A atualizar dados..."):
                if RevenueService.update_revenue(revenue_id, revenue_data):
                    st.success("Dados de receita atualizados com sucesso!")

                    # Display a summary of the updated data
                    st.subheader("Resumo Atualizado")
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
        except Exception as e:
            st.error(f"Erro ao atualizar dados: {str(e)}")

    # Navigation and action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.page_link(
            "sections/revenues/page.py",
            label="Voltar à lista de Receitas",
            icon="⬅️",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "Eliminar Esta Receita", type="tertiary", icon="🗑️", use_container_width=True
        ):
            if revenue_id:
                delete_revenue_records(revenue_id)


# Execute the main function
main()
