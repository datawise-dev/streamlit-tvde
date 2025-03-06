import streamlit as st
from typing import Dict, Tuple, List, Callable, Any, Optional, Union

class AsyncDataLoader:
    """
    Utility class to handle asynchronous loading of data in Streamlit forms.
    Provides methods to:
    - Load data asynchronously
    - Render UI elements that depend on async loaded data
    - Manage multiple async data loads
    """
    
    @staticmethod
    def load_data(
        key: str, 
        load_function: Callable, 
        process_function: Optional[Callable] = None,
        *args, 
        **kwargs
    ) -> Tuple[bool, bool, Any]:
        """
        Load data asynchronously and store in session state.
        
        Args:
            key: Key for the session state
            load_function: Function to load the data
            process_function: Optional function to process the loaded data
            *args, **kwargs: Arguments to pass to the load function
            
        Returns:
            A tuple of (is_loaded, is_loading, data)
        """
        loading_key = f"{key}_loading"
        loaded_key = f"{key}_loaded"
        data_key = f"{key}_data"
        
        if loading_key not in st.session_state:
            st.session_state[loading_key] = False
            st.session_state[loaded_key] = False
            st.session_state[data_key] = None
        
        if not st.session_state[loaded_key] and not st.session_state[loading_key]:
            st.session_state[loading_key] = True
            
            with st.spinner(f"A carregar dados de {key}..."):
                try:
                    data = load_function(*args, **kwargs)
                    
                    # Process data if a processor function is provided
                    if process_function and data is not None:
                        data = process_function(data)
                        
                    st.session_state[data_key] = data
                    st.session_state[loaded_key] = True
                except Exception as e:
                    st.error(f"Erro ao carregar {key}: {str(e)}")
                    st.session_state[loaded_key] = True  # Prevent infinite loading
                    st.session_state[data_key] = None
                finally:
                    st.session_state[loading_key] = False
        
        return (
            st.session_state[loaded_key],
            st.session_state[loading_key],
            st.session_state[data_key]
        )
    
    @staticmethod
    def load_multiple(
        load_configs: List[Tuple[str, Callable, Optional[Callable], tuple, dict]]
    ) -> Tuple[bool, bool, Dict[str, Tuple[bool, bool, Any]]]:
        """
        Load multiple datasets asynchronously.
        
        Args:
            load_configs: List of tuples (key, load_function, process_function, args, kwargs)
            
        Returns:
            Tuple of (all_loaded, any_loading, results_dict)
        """
        all_loaded = True
        any_loading = False
        results = {}
        
        for config in load_configs:
            key, load_function, process_function, args, kwargs = config
            is_loaded, is_loading, data = AsyncDataLoader.load_data(
                key, load_function, process_function, *args, **kwargs
            )
            
            all_loaded = all_loaded and is_loaded
            any_loading = any_loading or is_loading
            results[key] = (is_loaded, is_loading, data)
        
        # Trigger rerun only once after all data is loaded
        needs_rerun = False
        if all_loaded and not any_loading:
            for key, (is_loaded, is_loading, data) in results.items():
                if f"{key}_first_loaded" not in st.session_state:
                    st.session_state[f"{key}_first_loaded"] = True
                    needs_rerun = True
            
            if needs_rerun:
                st.rerun()
        
        return all_loaded, any_loading, results
    
    @staticmethod
    def render_selectbox(
        key: str, 
        label: str,
        format_func: Optional[Callable] = None,
        empty_message: str = "Nenhuma opção disponível",
        loading_message: str = "A carregar...",
        *args, 
        **kwargs
    ) -> Any:
        """
        Render a selectbox with async loaded options.
        
        Args:
            key: Key for the data in session state
            label: Label for the selectbox
            format_func: Function to format the display values in the selectbox
            empty_message: Message to display when no options are available
            loading_message: Message to display while loading
            *args, **kwargs: Additional arguments for the selectbox
            
        Returns:
            The selected value
        """
        is_loaded = st.session_state.get(f"{key}_loaded", False)
        is_loading = st.session_state.get(f"{key}_loading", False)
        options = st.session_state.get(f"{key}_data", {})
        
        # Default format function if none provided
        if not format_func:
            format_func = lambda x: options.get(x, empty_message) if options else loading_message
        
        display_label = label + (f" ({loading_message})" if is_loading else "")
        
        return st.selectbox(
            display_label,
            options=[] if not is_loaded or not options else list(options.keys()),
            format_func=format_func,
            disabled=not is_loaded or not options,
            *args,
            **kwargs
        )
    
    @staticmethod
    def reset(keys: List[str]) -> None:
        """
        Reset the loading state for the given keys.
        
        Args:
            keys: List of keys to reset
        """
        for key in keys:
            if f"{key}_loading" in st.session_state:
                del st.session_state[f"{key}_loading"]
            if f"{key}_loaded" in st.session_state:
                del st.session_state[f"{key}_loaded"]
            if f"{key}_data" in st.session_state:
                del st.session_state[f"{key}_data"]
            if f"{key}_first_loaded" in st.session_state:
                del st.session_state[f"{key}_first_loaded"]


# Common data processors for reuse across forms

def process_drivers(drivers_data):
    """
    Process driver data for use in selectboxes.
    
    Args:
        drivers_data: List of tuples (id, display_name, ...)
        
    Returns:
        Dictionary mapping driver IDs to display names
    """
    if not drivers_data:
        return {}
    
    return {
        driver[0]: f"{driver[1]}" for driver in drivers_data
    }

def process_cars(cars_data):
    """
    Process car data for use in selectboxes.
    
    Args:
        cars_data: List of tuples (id, license_plate, brand, model)
        
    Returns:
        Dictionary mapping car IDs to formatted display strings
    """
    if not cars_data:
        return {}
    
    return {
        car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars_data
    }

def extract_license_plate(car_display):
    """
    Extract license plate from car display string.
    
    Args:
        car_display: String in format "XX-XX-XX (Brand Model)"
        
    Returns:
        License plate string
    """
    if not car_display:
        return ""
    
    return car_display.split(" ")[0]