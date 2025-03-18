import streamlit as st
import pandas as pd
import tempfile
import os
from typing import Dict, List, Callable
import logging
from utils.error_handlers import handle_streamlit_error

logger = logging.getLogger(__name__)

@handle_streamlit_error()
def bulk_import_component(
    entity_name: str,
    standard_fields: List[str],
    validation_function: Callable,
    upload_function: Callable,
    field_display_names: Dict[str, str] = None,
):
    """
    Reusable component for bulk import across different entities.
    
    Args:
        entity_name: Name of the entity being imported (e.g., "receitas", "motoristas")
        standard_fields: List of standard field names for the entity
        validation_function: Function that validates a data record
        upload_function: Function that uploads validated data
        field_display_names: Dictionary mapping field names to display names
    """
    if field_display_names is None:
        field_display_names = {field: field for field in standard_fields}
    
    st.subheader(f"Importação em Massa de {entity_name.capitalize()}")
    
    # File upload
    uploaded_file = st.file_uploader(
        f"Carregue um ficheiro CSV ou Excel com os dados de {entity_name}",
        type=["csv", "xlsx", "xls"],
        help=f"O ficheiro deve conter colunas correspondentes aos campos necessários para {entity_name}."
    )
    
    if uploaded_file is not None:
        # Process the file
        try:
            # Create a temporary file to store the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_filepath = tmp_file.name
            
            # Read the file based on its extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(tmp_filepath)
            else:  # Excel file
                df = pd.read_excel(tmp_filepath)
            
            # Clean up the temporary file
            os.unlink(tmp_filepath)
            
            # Preview the data
            st.subheader("Pré-visualização dos Dados")
            st.dataframe(df.head(10))
            
            # Column mapping
            st.subheader("Mapeamento de Colunas")
            st.write("Associe as colunas do seu ficheiro aos campos necessários:")
            
            column_mapping = {}
            file_columns = ["-- Não Mapear --"] + list(df.columns)
            
            for field in standard_fields:
                display_name = field_display_names.get(field, field)
                
                # Try to find a matching column automatically
                default_index = 0
                for i, col in enumerate(file_columns):
                    if col.lower().replace(" ", "_") == field.lower() or col.lower() == field.lower():
                        default_index = i
                        break
                
                selected_column = st.selectbox(
                    f"{display_name}:",
                    options=file_columns,
                    index=default_index,
                    key=f"mapping_{field}"
                )
                
                if selected_column != "-- Não Mapear --":
                    column_mapping[field] = selected_column
            
            # Process button
            if st.button("Processar e Importar Dados", use_container_width=True):
                # Validate column mapping
                missing_required_fields = [field for field in standard_fields if field not in column_mapping]
                if missing_required_fields:
                    # Convert field names to display names for error message
                    missing_field_names = [field_display_names.get(field, field) for field in missing_required_fields]
                    st.error(f"Campos obrigatórios não mapeados: {', '.join(missing_field_names)}")
                    return
                
                # Process and validate each row
                records = []
                errors = []
                
                with st.spinner("A validar dados..."):
                    progress_bar = st.progress(0)
                    total_rows = len(df)
                    
                    for index, row in df.iterrows():
                        record = {}
                        
                        # Map the columns to fields
                        for field, column in column_mapping.items():
                            # Handle both numerical and non-numerical fields
                            if pd.isna(row[column]):
                                record[field] = None
                            else:
                                # Handle date columns specially
                                if field in ['start_date', 'end_date', 'payment_date', 'acquisition_date']:
                                    try:
                                        # Try to convert to ISO date format string
                                        if isinstance(row[column], str):
                                            date_obj = pd.to_datetime(row[column])
                                            record[field] = date_obj.strftime('%Y-%m-%d')
                                        elif pd.notna(row[column]):
                                            # Handle pandas Timestamp or datetime
                                            record[field] = row[column].strftime('%Y-%m-%d')
                                        else:
                                            record[field] = None
                                    except Exception as e:
                                        logger.error(f"Error parsing date in row {index+2}, column {column}: {str(e)}")
                                        record[field] = row[column]  # Let validation catch this
                                else:
                                    record[field] = row[column]
                        
                        # Validate the record
                        is_valid, error_messages = validation_function(record)
                        
                        if is_valid:
                            records.append(record)
                        else:
                            error_info = {
                                "row": index + 2,  # +2 because index starts at 0 and we have header row
                                "errors": error_messages
                            }
                            errors.append(error_info)
                        
                        # Update progress
                        progress_bar.progress((index + 1) / total_rows)
                
                # Display validation results
                if errors:
                    st.error(f"Encontrados {len(errors)} erros de validação:")
                    
                    # Create an expander for errors to avoid cluttering the UI
                    with st.expander("Ver detalhes dos erros"):
                        for error in errors:
                            st.warning(f"Linha {error['row']}: {'; '.join(error['errors'])}")
                    
                    st.warning("Corrija os erros no ficheiro e tente novamente.")
                    
                    # Show records with errors vs. valid records
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Registos Válidos", len(records))
                    with col2:
                        st.metric("Registos com Erros", len(errors))
                        
                elif len(records) == 0:
                    st.warning("Não foram encontrados registos válidos para importar.")
                else:
                    # All data is valid, proceed with import
                    with st.spinner(f"A importar {len(records)} registos..."):
                        try:
                            upload_function(records)
                            st.success(f"{len(records)} registos importados com sucesso!")
                            
                            # Display summary
                            st.metric("Total de Registos Processados", len(records))
                        except Exception as e:
                            st.error(f"Erro ao importar dados: {str(e)}")
                
        except Exception as e:
            st.error(f"Erro ao processar o ficheiro: {str(e)}")
            logger.exception("Error in bulk import")

def get_sample_csv_template(field_names: List[str], field_display_names: Dict[str, str] = None) -> str:
    """
    Generate a sample CSV template with headers based on the required field names.
    
    Args:
        field_names: List of field names for the entity
        field_display_names: Dictionary mapping field names to display names
        
    Returns:
        CSV content as a string
    """
    if field_display_names is None:
        field_display_names = {field: field for field in field_names}
    
    header_row = ",".join([field_display_names.get(field, field) for field in field_names])
    sample_row = ",".join([""] * len(field_names))
    
    return f"{header_row}\n{sample_row}"