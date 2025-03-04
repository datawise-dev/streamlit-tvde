import streamlit as st
import pandas as pd
from services.driver_service import DriverService
from .form import show_driver_form

def show_driver_list():
    """Display enhanced list of drivers with edit and delete options."""
    try:
        df = DriverService.load_drivers()
        if not df.empty:
            # Add filters
            st.subheader("Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                display_name_filter = st.text_input(
                    "Filter by Display Name",
                    help="Filter drivers by display name"
                )
                
            with col2:
                is_active_filter = st.toggle(
                    "Only Active Drivers",
                    value=True,
                    help="Show only active drivers"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if display_name_filter:
                display_name_filter = display_name_filter.lower()
                filtered_df = filtered_df[
                    filtered_df['display_name'].str.lower().str.contains(display_name_filter)
                ]
                
            if is_active_filter:
                filtered_df = filtered_df[filtered_df['is_active']]

            # Display data - show most relevant columns in the table
            display_cols = [
                'display_name', 'first_name', 'last_name', 'nif', 
                'location', 'postal_code', 'is_active'
            ]
            
            st.dataframe(
                filtered_df[display_cols],
                use_container_width=True
            )

            # View detailed information for a selected driver
            with st.expander("View Detailed Driver Information"):
                driver_to_view = st.selectbox(
                    "Select driver to view details",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: filtered_df[filtered_df['id'] == x]['display_name'].iloc[0]
                )
                
                selected_driver = filtered_df[filtered_df['id'] == driver_to_view].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Personal Information**")
                    st.write(f"**Display Name:** {selected_driver['display_name']}")
                    st.write(f"**Full Name:** {selected_driver['first_name']} {selected_driver['last_name']}")
                    st.write(f"**NIF:** {selected_driver['nif']}")
                    
                with col2:
                    st.write("**Address**")
                    st.write(f"**Address:** {selected_driver['address_line1']}")
                    if pd.notna(selected_driver['address_line2']):
                        st.write(f"{selected_driver['address_line2']}")
                    st.write(f"{selected_driver['postal_code']}, {selected_driver['location']}")
                    
                st.write("**Status**")
                status_text = "Active" if selected_driver['is_active'] else "Inactive"
                status_color = "green" if selected_driver['is_active'] else "red"
                st.markdown(f"**Status:** :<span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)

            # Management options
            st.subheader("Gerir Motoristas")
            col1, col2 = st.columns(2)
            
            with col1:
                driver_to_edit = st.selectbox(
                    "Selecionar motorista para editar",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: filtered_df[filtered_df['id'] == x]['display_name'].iloc[0]
                )
                if st.button("Editar Selecionado"):
                    driver_data = DriverService.get_driver(driver_to_edit)
                    if show_driver_form(driver_data):
                        st.rerun()

            with col2:
                driver_to_delete = st.selectbox(
                    "Selecionar motorista para eliminar",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: filtered_df[filtered_df['id'] == x]['display_name'].iloc[0],
                    key="delete_driver"
                )
                if st.button("Eliminar Selecionado", key="delete_button"):
                    if st.checkbox("Confirmar eliminação", key="confirm_delete"):
                        try:
                            if DriverService.delete_driver(driver_to_delete):
                                st.success("Motorista eliminado com sucesso!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao eliminar motorista: {str(e)}")

            # Summary statistics
            st.subheader("Estatísticas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_drivers = len(filtered_df)
                st.metric("Total de Motoristas", f"{total_drivers}")
            
            with col2:
                active_drivers = len(filtered_df[filtered_df['is_active'] == True])
                inactive_drivers = len(filtered_df[filtered_df['is_active'] == False])
                st.metric("Motoristas Ativos", f"{active_drivers}")
                st.metric("Motoristas Inativos", f"{inactive_drivers}")
            
            with col3:
                locations_count = filtered_df['location'].value_counts()
                most_common_location = locations_count.idxmax() if not locations_count.empty else "N/A"
                st.metric("Local mais comum", f"{most_common_location}")
        
        else:
            st.info("Não existem motoristas registados no sistema.")
    
    except Exception as e:
        st.error(f"Erro ao carregar motoristas: {str(e)}")