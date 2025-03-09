import streamlit as st
import inspect
import os

def page_init():
    """
    Initialize a page by loading stored query parameters if available.
    This should be called at the top of every page that might receive query parameters.
    
    Returns:
        True if query parameters were applied, False otherwise
    """
    # Get the current script path
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    script_path = os.path.relpath(filename).replace('\\', '/')
    
    # Check if there are stored parameters for this path
    if 'stored_query_params' in st.session_state:
        stored = st.session_state.stored_query_params
        
        # Check if the stored parameters are for this page
        if stored['target_page'] == script_path:
            # Apply stored parameters
            for key, value in stored['params'].items():
                st.query_params[key] = value
            
            # Clean up
            del st.session_state.stored_query_params
            return True
            
    return False