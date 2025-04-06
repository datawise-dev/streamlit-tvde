import streamlit as st
import pandas as pd
import tempfile
import os
from typing import Dict, List, Callable, Tuple, Optional, Any
from utils.error_handlers import handle_streamlit_error
from typing import Dict, List, Callable, Any, Type, Tuple
from utils.base_service import BaseService
from utils.entity_import import create_generic_uploader, create_record_validator


def load_file(uploaded_file) -> Optional[Tuple[pd.DataFrame, List[str]]]:
    """
    Load data from an uploaded file into a pandas DataFrame.
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        
    Returns:
        Tuple containing (DataFrame with file data, list of sheet names if Excel) or None if an error occurs
    """
    tmp_filepath = None
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_filepath = tmp_file.name

        # Read the file based on its extension
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(tmp_filepath)
            sheet_names = []  # CSV files don't have sheets
        else:  # Excel file
            # First, get the available sheet names
            excel_file = pd.ExcelFile(tmp_filepath)
            sheet_names = excel_file.sheet_names
            
            # By default, read the first sheet
            df = pd.read_excel(excel_file, sheet_name=0)
            excel_file.close()  # Explicitly close the Excel file

        return df, sheet_names
        
    except Exception as e:
        st.error(f"Erro ao processar o ficheiro: {str(e)}")
        print("Error loading file")
        return None
        
    finally:
        # Ensure the temporary file is removed with error handling
        if tmp_filepath and os.path.exists(tmp_filepath):
            try:
                os.unlink(tmp_filepath)
            except Exception as e:
                print(f"Could not delete temporary file {tmp_filepath}: {str(e)}")
                # On Windows, sometimes files can't be deleted immediately
                # Schedule for deletion on program exit
                import atexit
                atexit.register(lambda file=tmp_filepath: os.path.exists(file) and os.remove(file))


def display_data_preview(df: pd.DataFrame, rows: int = 10) -> None:
    """
    Display a preview of the DataFrame.
    
    Args:
        df: DataFrame to preview
        rows: Number of rows to show in the preview
    """
    st.subheader("Pré-visualização dos Dados")
    st.dataframe(df.head(rows), hide_index=True)


def column_mapping_ui(
    file_columns: List[str], 
    fields_config: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Create UI for mapping file columns to standard fields.
    
    Args:
        file_columns: List of column names from the uploaded file
        fields_config: List of field configurations with key, display_name, etc.
        
    Returns:
        Dictionary mapping standard fields to file columns
    """
    st.subheader("Mapeamento de Colunas")
    st.write("Associe as colunas do seu ficheiro aos campos necessários:")
    
    column_mapping = {}

    # Create two-column layout for each field mapping
    for field_def in fields_config:
        field = field_def.get('key')
        display_name = field_def.get('label', field)
        required = field_def.get('required', False)

        # Try to find a matching column automatically
        default_index = 0
        for i, col in enumerate(file_columns):
            col_formatted = str(col).lower().replace(" ", "_")
            field_formatted = field.lower().replace(" ", "_")
            name_formatted = display_name.lower().replace(" ", "_")

            if col_formatted in [field_formatted, name_formatted]:
                default_index = i
                break

        required_marker = " *" if required else ""
        selected_column = st.selectbox(
            label=f"{display_name}{required_marker}",
            options=file_columns,
            index=default_index,
            key=f"mapping_{field}",
        )

        if selected_column != "-- Não Mapear --":
            column_mapping[field] = selected_column

    return column_mapping


def validate_mapping(
    column_mapping: Dict[str, str], 
    fields_config: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields have been mapped.
    
    Args:
        column_mapping: Dictionary mapping standard fields to file columns
        fields_config: List of field configurations with key, display_name, etc.
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    # Get required fields
    required_fields = [field_def.get('key') for field_def in fields_config 
                       if field_def.get('required', False)]
    
    # Validate that all required fields are mapped
    missing_required_fields = [
        field for field in required_fields if field not in column_mapping
    ]
    
    if missing_required_fields:
        # Convert field names to display names for error message
        missing_field_names = [
            next((field_def.get('display_name', field) 
                 for field_def in fields_config if field_def.get('key') == field), field)
            for field in missing_required_fields
        ]
        return False, missing_field_names
    
    return True, []


def process_row(
    row: pd.Series, 
    column_mapping: Dict[str, str],
    fields_config: List[Dict[str, Any]],
    index: int
) -> Dict[str, any]:
    """
    Process a single row of data from the DataFrame.
    
    Args:
        row: Pandas Series representing a single row of data
        column_mapping: Dictionary mapping standard fields to file columns
        fields_config: List of field configurations
        index: Row index for error reporting
        
    Returns:
        Dictionary containing processed field values
    """
    record = {}

    # Create a lookup dictionary for field definitions
    field_defs = {}
    
    for field_def in fields_config:
        if 'key' in field_def:
            key = field_def.get('key')
            field_defs[key] = field_def
    
    # Map the columns to fields with type conversion
    for field, column in column_mapping.items():
        # Skip if the column doesn't exist in the row
        if column not in row:
            continue
            
        # Skip if the value is missing
        if pd.isna(row[column]):
            record[field] = None
            continue
            
        value = row[column]
        field_def = field_defs.get(field, {})
        field_type = field_def.get('type', 'text')  # Default to text if type not found
        
        # Convert the value based on the field type
        if field_type == 'number':
            # Keep as numeric
            record[field] = float(value) if '.' in str(value) else int(value)
        
        elif field_type in ['date', 'datetime']:
            # Handle date conversion
            if isinstance(value, str):
                date_obj = pd.to_datetime(value)
                record[field] = date_obj.strftime("%Y-%m-%d")
            elif pd.notna(value):
                # Handle pandas Timestamp or datetime
                record[field] = value.strftime("%Y-%m-%d")
            else:
                record[field] = None
        
        elif field_type == 'checkbox' or field_type == 'toggle':
            # Convert to boolean
            if isinstance(value, bool):
                record[field] = value
            elif isinstance(value, (int, float)):
                record[field] = bool(value)
            elif isinstance(value, str):
                record[field] = value.lower() in ['true', 'yes', '1', 'sim', 'verdadeiro']
            else:
                record[field] = bool(value)
        
        elif field_type == 'select':
            # Get options and format_func
            options = field_def.get('options', {})
            select_options = options.get('options', [])
            format_func = options.get('format_func')
            
            if format_func:
                # Create a reverse mapping: display value -> option value
                # This is the key part - we're creating the reverse of what format_func does
                reverse_mapping = {}
                
                for option in select_options:
                    # Apply format_func to get display value
                    display_value = format_func(option)
                    # Store mapping with case insensitive option
                    reverse_mapping[str(display_value).lower()] = option
                
                # Try to find a match for the input value
                value_str = str(value).lower()
                if value_str in reverse_mapping:
                    record[field] = reverse_mapping[value_str]
                else:
                    # No match found - this will likely fail validation later
                    print(f"Warning: No match found for '{value}' in field {field}")
                    record[field] = None
            else:
                # No format_func or options - just use the value directly
                record[field] = value
        
        else:
            # For text, textarea, etc. - convert to string
            record[field] = str(value)
            # Remove trailing ".0" from numeric strings (common Excel artifact)
            if record[field].endswith('.0') and field_type not in ['number']:
                record[field] = record[field][:-2]
    
    # Apply default values for fields not in the record
    for field, field_def in field_defs.items():
        default_value = field_def.get('default_value', field_def.get('default'))
        if (field not in record or record[field] is None) and default_value is not None:
            record[field] = default_value

    return record


def validate_and_process_data(
    df: pd.DataFrame,
    column_mapping: Dict[str, str],
    fields_config: List[Dict[str, Any]]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate and process all data rows.
    
    Args:
        df: DataFrame containing the data to process
        column_mapping: Dictionary mapping standard fields to file columns
        fields_config: List of field configurations with key, display_name, validators, etc.
        
    Returns:
        Tuple of (valid_records, error_records)
    """
    valid_records = []
    error_records = []

    record_validator = create_record_validator(fields_config)

    with st.spinner("A validar dados..."):

        for index, row in df.iterrows():
            # Process the row
            record = process_row(row, column_mapping, fields_config, index)                
            
            # Validate the record
            is_valid, error_messages = record_validator(record)

            if is_valid:
                valid_records.append(record)
            else:
                error_info = {
                    "row": index + 2,  # +2 because index starts at 0 and we have header row
                    "errors": error_messages,
                }
                error_records.append(error_info)
            
    return valid_records, error_records


def display_validation_results(valid_records: List[Dict], error_records: List[Dict]) -> bool:
    """
    Display validation results and return whether to proceed with import.
    
    Args:
        valid_records: List of valid data records
        error_records: List of records with validation errors
        
    Returns:
        Boolean indicating whether to proceed with import
    """
    if error_records:
        st.error(f"Encontrados {len(error_records)} erros de validação:")

        # Create an expander for errors to avoid cluttering the UI
        with st.expander("Ver detalhes dos erros"):
            for error in error_records:
                st.warning(f"Linha {error['row']}: {'; '.join(error['errors'])}")

        st.warning("Corrija os erros no ficheiro e tente novamente.")

        # Show records with errors vs. valid records
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Registos Válidos", len(valid_records))
        with col2:
            st.metric("Registos com Erros", len(error_records))
            
        return False
    
    elif len(valid_records) == 0:
        st.warning("Não foram encontrados registos válidos para importar.")
        return False
    
    return True


def import_data(valid_records: List[Dict], upload_function: Callable) -> bool:
    """
    Import validated records using the provided upload function.
    
    Args:
        valid_records: List of valid data records
        upload_function: Function that uploads validated data
        
    Returns:
        Boolean indicating whether import was successful
    """
    with st.spinner(f"A importar {len(valid_records)} registos..."):
        try:
            upload_function(valid_records)
            st.success(f"{len(valid_records)} registos importados com sucesso!")

            # Display summary
            st.metric("Total de Registos Processados", len(valid_records))
            return True
        except Exception as e:
            st.error(f"Erro ao importar dados: {str(e)}")
            return False


def select_sheet_ui(sheet_names: List[str]) -> int:
    """
    Create UI for selecting a sheet from an Excel file with multiple sheets.
    
    Args:
        sheet_names: List of sheet names from the uploaded Excel file
        
    Returns:
        Index of the selected sheet
    """
    if not sheet_names:
        return 0  # Default to first sheet if no sheet names provided
    
    # Create a selection box for the user to choose a sheet
    sheet_options = [f"{i+1}: {name}" for i, name in enumerate(sheet_names)]
    selected_sheet = st.selectbox(
        "Selecione a folha do Excel:",
        options=sheet_options,
        index=0,
        help="Escolha a folha que contém os dados que deseja importar."
    )
    
    # Extract the index from the selected option
    selected_index = int(selected_sheet.split(':')[0]) - 1
    return selected_index


def load_excel_sheet(uploaded_file, sheet_index: int = 0) -> pd.DataFrame:
    """
    Load a specific sheet from an Excel file.
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        sheet_index: Index of the sheet to load
        
    Returns:
        DataFrame containing the sheet data or None if an error occurs
    """
    tmp_filepath = None
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_filepath = tmp_file.name

        # Read the specified sheet using ExcelFile to ensure proper closing
        with pd.ExcelFile(tmp_filepath) as excel_file:
            df = pd.read_excel(excel_file, sheet_name=sheet_index)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar a folha selecionada: {str(e)}")
        print("Error loading Excel sheet")
        return None
        
    finally:
        # Ensure the temporary file is removed with error handling
        if tmp_filepath and os.path.exists(tmp_filepath):
            try:
                os.unlink(tmp_filepath)
            except Exception as e:
                print(f"Could not delete temporary file {tmp_filepath}: {str(e)}")
                # Schedule for deletion on program exit
                import atexit
                atexit.register(lambda file=tmp_filepath: os.path.exists(file) and os.remove(file))


@handle_streamlit_error()
def bulk_import_component(
    entity_name: str,
    fields_config: List[Dict[str, Any]],
    upload_function: Callable,
):
    """
    Reusable component for bulk import across different entities.

    Args:
        entity_name: Name of the entity being imported (e.g., "receitas", "motoristas")
        fields_config: List of field configurations with key, display_name, validators, etc.
        upload_function: Function that uploads validated data
    """
    # Extract standard fields from fields_config
    st.subheader(f"Importação em Massa de {entity_name.capitalize()}")

    css = """
    .stFileUploaderFile {
        display: none;
    }
    """
    # or `visibility: hidden;`

    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader(
        f"Carregue um ficheiro CSV ou Excel com os dados de {entity_name}",
        type=["csv", "xlsx", "xls"],
        help=f"O ficheiro deve conter colunas correspondentes aos campos necessários para {entity_name}.",
    )

    if uploaded_file is not None:
        # Load the file initially to get sheet names if it's an Excel file
        result = load_file(uploaded_file)
        if result is None:
            return
            
        df, sheet_names = result
        
        # For Excel files with multiple sheets, show sheet selection
        if uploaded_file.name.endswith(('.xlsx', '.xls')) and len(sheet_names) > 1:
            # st.info(f"O ficheiro Excel carregado contém {len(sheet_names)} folhas.")
            selected_sheet_index = select_sheet_ui(sheet_names)
            
            # Load the selected sheet
            df = load_excel_sheet(uploaded_file, selected_sheet_index)
            if df is None:
                return
                
            # st.success(f"Folha '{sheet_names[selected_sheet_index]}' selecionada e carregada.")
            
        # Display data preview
        display_data_preview(df)
        
        # Set up column mapping
        file_columns = ["-- Não Mapear --"] + list(df.columns)
        column_mapping = column_mapping_ui(file_columns, fields_config)
        
        # Process button
        if st.button("Processar e Importar Dados", use_container_width=True):
            # Validate mapping
            is_valid, missing_fields = validate_mapping(column_mapping, fields_config)
            if not is_valid:
                st.error(f"Campos obrigatórios não mapeados: {', '.join(missing_fields)}")
                return
                
            # Process and validate data
            valid_records, error_records = validate_and_process_data(
                df, column_mapping, fields_config
            )
            
            # Display validation results
            proceed = display_validation_results(valid_records, error_records)
            
            # Import data if validation passed
            if proceed:
                import_data(valid_records, upload_function)


def get_sample_csv_template(
    field_names: List[str], field_display_names: Dict[str, str] = None
) -> str:
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

    header_row = ",".join(
        [field_display_names.get(field, field) for field in field_names]
    )
    sample_row = ",".join([""] * len(field_names))

    return f"{header_row}\n{sample_row}"

def entity_bulk_import_tab(
    entity_name: str,
    service_class: Type[BaseService],
    fields_config: List[Dict[str, Any]],
    help_content: Dict[str, str] = None,
):
    """
    Renders a bulk import tab for an entity type.

    Args:
        entity_name: Name of the entity (e.g., "cars", "drivers")
        service_class: The service class for the entity
        fields_config: List of field configurations with key, display_name, validators, etc.
        help_content: Optional help content to display in expanders
    """
    # Create validator and uploader functions
    uploader = create_generic_uploader(service_class)

    # Use the bulk import component
    with st.container(border=1):
        bulk_import_component(
            entity_name=entity_name,
            fields_config=fields_config,
            upload_function=uploader,
        )

    # Display help content if provided
    if help_content:
        for title, content in help_content.items():
            with st.expander(title):
                st.info(content)
