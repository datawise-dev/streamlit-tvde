import streamlit as st
import pandas as pd
from services.revenue_service import RevenueService
from utils.data_processing import map_columns, get_standard_columns
from utils.error_handlers import handle_streamlit_error

@handle_streamlit_error()
def show_csv_upload_view():
    """Display and handle the CSV upload form."""
    st.header("CSV File Upload")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                raise ValueError("Formato de arquivo inválido. Por favor, carregue um arquivo CSV ou Excel.")
            
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            # Column mapping
            st.subheader("Column Mapping")
            st.write("Map your CSV columns to standard columns:")
            
            col_mapping = map_columns(df.columns)
            final_mapping = {}
            
            for std_col in get_standard_columns():
                mapped_col = st.selectbox(
                    f"Map column for {std_col}",
                    options=[""] + list(df.columns),
                    index=0 if std_col not in col_mapping.values() 
                    else list(df.columns).index(
                        next(k for k, v in col_mapping.items() if v == std_col)
                    ) + 1
                )
                if mapped_col:
                    final_mapping[mapped_col] = std_col
            
            if st.button("Upload CSV Data"):
                if len(final_mapping) != len(get_standard_columns()):
                    st.error("Por favor, mapeie todas as colunas necessárias")
                else:
                    try:
                        mapped_df = df[list(final_mapping.keys())].rename(columns=final_mapping)
                        
                        # Convert date columns to proper format
                        for date_col in ['start_date', 'end_date']:
                            mapped_df[date_col] = pd.to_datetime(mapped_df[date_col]).dt.strftime('%Y-%m-%d')
                        
                        data_list = mapped_df.to_dict('records')
                        
                        if RevenueService.bulk_insert_revenue_data(data_list):
                            st.success(f"Successfully uploaded {len(data_list)} records!")
                    except Exception as e:
                        st.error(f"Erro ao processar CSV: {str(e)}")
        
        except Exception as e:
            st.error(f"Erro ao ler arquivo CSV: {str(e)}")