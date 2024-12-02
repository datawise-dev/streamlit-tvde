import re
from typing import Dict, List

def normalize_column_name(column_name: str) -> str:
    """Normalize column names by converting to lowercase and removing special characters."""
    return re.sub(r'[^a-z0-9]', '', column_name.lower())

def get_standard_columns() -> List[str]:
    """Get list of standard column names."""
    return [
        'start_date', 'end_date', 'driver_name', 'license_plate',
        'platform', 'gross_revenue', 'commission_percentage', 'tip',
        'num_travels', 'num_kilometers'
    ]

def map_columns(df_columns: List[str]) -> Dict[str, str]:
    """Map DataFrame columns to standard column names."""
    standard_cols = get_standard_columns()
    normalized_cols = {normalize_column_name(col): col for col in df_columns}
    
    col_mapping = {}
    for std_col in standard_cols:
        normalized_std = normalize_column_name(std_col)
        if normalized_std in normalized_cols:
            col_mapping[normalized_cols[normalized_std]] = std_col
    
    return col_mapping

def validate_revenue_data(data: Dict) -> tuple[bool, str]:
    """Validate revenue data before insertion."""
    if not data['driver_name'] or not data['license_plate']:
        return False, "Driver name and license plate are required"
    
    if data['end_date'] < data['start_date']:
        return False, "End date cannot be before start date"
        
    return True, ""