import streamlit as st
import pandas as pd
from services.revenue_service import RevenueService
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_data_view():
    """Display and handle the data view section."""
    st.header("Registos de Receita")
    
    # Filter section
    with st.form("filter_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            driver_filter = st.text_input(
                "Filtrar por Motorista",
                help="Filtrar por nome do motorista"
            )
            
        with col2:
            plate_filter = st.text_input(
                "Filtrar por Matrícula",
                help="Filtrar por matrícula do veículo"
            )
            
        with col3:
            platform_filter = st.selectbox(
                "Plataforma",
                options=["Todas", "Uber", "Bolt", "Transfer"],
                index=0,
                help="Filtrar por plataforma de serviço"
            )
            
        date_range = st.date_input(
            "Intervalo de Datas",
            value=[],
            help="Filtrar por intervalo de datas"
        )
        
        submit_button = st.form_submit_button("Filtrar", use_container_width=True)
    
    # Load data
    with st.spinner("A carregar dados...", show_time=True):
        df = RevenueService.load_data()
        
        if df.empty:
            st.info("Não existem registos de receita.")
            return
        
        # Convert date columns to pandas datetime
        for col in ['start_date', 'end_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
    
    # Apply filters
    filtered_df = df.copy()
    
    if driver_filter:
        filtered_df = filtered_df[
            filtered_df['driver_name'].str.lower().str.contains(driver_filter.lower())
        ]
        
    if plate_filter:
        filtered_df = filtered_df[
            filtered_df['license_plate'].str.lower().str.contains(plate_filter.lower())
        ]
        
    if platform_filter != "Todas":
        filtered_df = filtered_df[filtered_df['platform'] == platform_filter]
        
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['start_date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['end_date'] <= pd.to_datetime(date_range[1]))
        ]

    
    # Display records
    st.subheader(f"Registos ({len(filtered_df)} encontrados)")
    
    # Add selection column for deletion
    selection = st.checkbox("Selecionar para Eliminar")
    
    if selection:
        # Add selection column to dataframe
        filtered_df['select'] = False
        selected_indices = []
        
        # Create column configuration for display
        column_config = {
            "select": st.column_config.CheckboxColumn("Selecionar"),
            "start_date": st.column_config.DateColumn("Data Início"),
            "end_date": st.column_config.DateColumn("Data Fim"),
            "driver_name": st.column_config.TextColumn("Motorista"),
            "license_plate": st.column_config.TextColumn("Matrícula"),
            "platform": st.column_config.TextColumn("Plataforma"),
            "gross_revenue": st.column_config.NumberColumn("Receita Bruta", format="%.2f €"),
            "commission_percentage": st.column_config.NumberColumn("Comissão %", format="%.2f%%"),
            "tip": st.column_config.NumberColumn("Gorjeta", format="%.2f €"),
            "num_travels": st.column_config.NumberColumn("Viagens"),
            "num_kilometers": st.column_config.NumberColumn("Km", format="%.1f")
        }
        
        # Show interactive dataframe with selection
        edited_df = st.data_editor(
            filtered_df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            disabled=filtered_df.columns.tolist() if filtered_df.empty else 
                    [col for col in filtered_df.columns if col != 'select']
        )
        
        # Get selected rows
        selected_rows = edited_df[edited_df['select']].copy()
        
        if not selected_rows.empty:
            st.warning(f"Selecionados {len(selected_rows)} registos para eliminar.")
            
            if st.button("Eliminar Selecionados", type="primary"):
                selected_ids = selected_rows['id'].tolist()
                
                with st.spinner("A eliminar registos..."):
                    if RevenueService.delete_records(selected_ids):
                        st.success(f"{len(selected_ids)} registos eliminados com sucesso.")
                        st.rerun()  # Refresh the page
                    else:
                        st.error("Ocorreu um erro ao eliminar os registos.")
    else:
        # Just display the data without selection
        st.dataframe(
            filtered_df,
            column_config={
                "start_date": st.column_config.DateColumn("Data Início"),
                "end_date": st.column_config.DateColumn("Data Fim"),
                "driver_name": st.column_config.TextColumn("Motorista"),
                "license_plate": st.column_config.TextColumn("Matrícula"),
                "platform": st.column_config.TextColumn("Plataforma"),
                "gross_revenue": st.column_config.NumberColumn("Receita Bruta", format="%.2f €"),
                "commission_percentage": st.column_config.NumberColumn("Comissão %", format="%.2f%%"),
                "tip": st.column_config.NumberColumn("Gorjeta", format="%.2f €"),
                "num_travels": st.column_config.NumberColumn("Viagens"),
                "num_kilometers": st.column_config.NumberColumn("Km", format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )

    
    # Show summary stats
    if not filtered_df.empty:
        st.subheader("Resumo")
        
        # Calculate summary values
        total_revenue = filtered_df['gross_revenue'].sum()
        total_commission = (filtered_df['gross_revenue'] * filtered_df['commission_percentage'] / 100).sum()
        net_revenue = total_revenue - total_commission + filtered_df['tip'].sum()
        avg_commission = filtered_df['commission_percentage'].mean()
        total_trips = filtered_df['num_travels'].sum()
        total_km = filtered_df['num_kilometers'].sum()
        
        # Display in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Receita Bruta", f"{total_revenue:.2f} €")
            st.metric("Receita Líquida", f"{net_revenue:.2f} €")
            
        with col2:
            st.metric("Comissão Total", f"{total_commission:.2f} €")
            st.metric("Comissão Média", f"{avg_commission:.2f}%")
            
        with col3:
            st.metric("Total Viagens", f"{int(total_trips)}")
            st.metric("Total Km", f"{total_km:.1f} km")

# Execute the function directly (no if __name__ == "__main__" check)
show_data_view()
