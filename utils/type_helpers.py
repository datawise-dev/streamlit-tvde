from datetime import datetime, date
import pandas as pd
from typing import Any, Optional


def date_to_iso8601(value: Any) -> Optional[str]:
    """
    Converts a date/datetime value to ISO8601 string format.
    
    Args:
        value: The date value to convert (datetime, date, pd.Timestamp, or string)
        
    Returns:
        Formatted date string in ISO8601 format or None if conversion fails
    """
    if pd.isna(value) or value is None:
        return None
    
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(value, date):
        # For date objects, add zero time
        return value.strftime('%Y-%m-%dT00:00:00')
    elif isinstance(value, str):
        # Try to parse the string as a date if it's not already in ISO format
        if 'T' not in value and len(value) >= 10:
            try:
                parsed_date = pd.to_datetime(value)
                return parsed_date.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                # Return the original string if it can't be parsed
                return value
        # Return as is if it appears to be already in the right format
        return value
    else:
        # Return None for unsupported types
        return None
