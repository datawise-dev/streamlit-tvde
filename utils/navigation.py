import streamlit as st
from urllib.parse import urlparse, parse_qs
import inspect
import os

def switch_page(url):
    """
    Custom switch page that supports query parameters by storing them in session state.
    
    Args:
        url: Target URL with optional query parameters (e.g., "views/driver.py?id=123")

    Returns:
    """
    # Parse the URL to separate path and query parameters
    parsed_url = urlparse(url)
    base_path = parsed_url.path
    
    # Extract query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Store query parameters in session state if present
    if query_params:
        # Convert query parameters to the right format (lists to single values when possible)
        query_dict = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        st.session_state.stored_query_params = {
            'target_page': base_path,
            'params': query_dict
        }
    
    # Create switch page without query parameters
    st.switch_page(base_path)

def check_query_params():
    """
    Check if there are stored query parameters for the current page and apply them.
    This should be called at the beginning of each page that might receive query parameters.
    
    Returns:
        True if query parameters were applied, False otherwise
    """
    if 'stored_query_params' in st.session_state:
        stored = st.session_state.stored_query_params
        
        # Get the caller's filename using inspect
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        script_path = os.path.relpath(filename).replace('\\', '/')
        
        # Check if the stored parameters are for the current page
        if stored['target_page'] == script_path:
            # Apply stored parameters to current page's query params
            for key, value in stored['params'].items():
                st.query_params[key] = value
            
            # Clean up to avoid reapplying on refresh
            del st.session_state.stored_query_params
            return True
    
    return False
