import functools
import logging
import traceback
import psycopg2
from typing import Callable, Dict, Type, Any, Optional
import inspect

# Configure logging
logger = logging.getLogger(__name__)

# Map of exception types to friendly error messages
ERROR_MESSAGES = {
    psycopg2.errors.UniqueViolation: "Já existe um registo com este valor.",
    psycopg2.errors.ForeignKeyViolation: "Não é possível completar a operação porque este registo está referenciado por outros dados.",
    psycopg2.errors.NotNullViolation: "Um campo obrigatório não foi preenchido.",
    psycopg2.errors.CheckViolation: "Os dados fornecidos não respeitam as regras de validação.",
    ValueError: "Valor inválido fornecido.",
    TypeError: "Tipo de dados incorreto.",
    KeyError: "Chave não encontrada.",
    FileNotFoundError: "Ficheiro não encontrado."
    # Add more mappings as needed
}

def handle_error(
    error_message: str = "Ocorreu um erro ao processar o pedido.",
    log_traceback: bool = True,
    reraise: bool = False,
    exception_map: Optional[Dict[Type[Exception], str]] = None
):
    """
    Decorator for consistent error handling.
    
    Args:
        error_message: Default error message if no specific mapping exists
        log_traceback: Whether to log the full traceback
        reraise: Whether to re-raise the exception after handling
        exception_map: Additional mapping of exception types to error messages
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get the combined exception mappings
                combined_map = {**ERROR_MESSAGES}
                if exception_map:
                    combined_map.update(exception_map)
                
                # Get a friendly error message based on exception type
                friendly_message = error_message
                for exc_type, message in combined_map.items():
                    if isinstance(e, exc_type):
                        friendly_message = message
                        break
                
                # Add specific error details if available
                detailed_message = f"{friendly_message}"
                if hasattr(e, 'detail') and getattr(e, 'detail', None):
                    detailed_message += f" Detalhes: {e.detail}"
                elif str(e):
                    detailed_message += f" Detalhes: {str(e)}"
                
                # Determine the calling context (class.method_name)
                context = ""
                if args and hasattr(args[0], '__class__'):
                    context = f"{args[0].__class__.__name__}."
                context += func.__name__
                
                # Log the error
                if log_traceback:
                    logger.error(
                        f"Error in {context}: {detailed_message}",
                        exc_info=True
                    )
                else:
                    logger.error(f"Error in {context}: {detailed_message}")
                
                # Re-raise or return a standardized error response
                if reraise:
                    raise
                    
                return {
                    "success": False,
                    "error": friendly_message,
                    "details": str(e) if str(e) else None
                }
                
        return wrapper
    return decorator


def handle_service_error(error_message: str = "Erro no serviço"):
    """
    Specialized decorator for service-layer functions.
    Logs detailed errors and re-raises with friendly messages.
    
    Args:
        error_message: Prefix for error messages
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get class name if it's a method
                if args and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__
                    method_name = func.__name__
                    context = f"{class_name}.{method_name}"
                else:
                    context = func.__name__
                
                # Log with detailed traceback for diagnostics
                logger.error(
                    f"Service error in {context}: {str(e)}",
                    exc_info=True
                )
                
                # Check if it's a known exception type
                for exc_type, message in ERROR_MESSAGES.items():
                    if isinstance(e, exc_type):
                        raise type(e)(f"{message} {str(e)}")
                
                # For unknown exceptions, wrap with a generic message
                raise Exception(f"{error_message}: {str(e)}")
                
        return wrapper
    return decorator


def handle_streamlit_error():
    """
    Specialized decorator for Streamlit view functions.
    Catches exceptions and displays them using st.error().
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Import here to avoid circular imports
                import streamlit as st
                
                # Log the error with traceback
                logger.error(
                    f"UI error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                
                # Get a friendly error message
                friendly_message = "Ocorreu um erro ao processar o pedido."
                for exc_type, message in ERROR_MESSAGES.items():
                    if isinstance(e, exc_type):
                        friendly_message = message
                        break
                
                # Show error in the UI
                st.error(friendly_message)
                
                # Optionally show technical details in expander if in debug mode
                if getattr(st.session_state, 'debug_mode', False):
                    with st.expander("Detalhes técnicos do erro"):
                        st.code(traceback.format_exc())
                
        return wrapper
    return decorator


def handle_database_error():
    """
    Specialized decorator for database operations.
    Maps database-specific errors to friendly messages.
    
    Returns:
        Decorated function
    """
    # Database-specific error mappings
    db_error_map = {
        psycopg2.errors.UniqueViolation: "Este registo já existe na base de dados.",
        psycopg2.errors.ForeignKeyViolation: "Não foi possível completar a operação porque este registo está relacionado com outros dados.",
        psycopg2.errors.CheckViolation: "Os dados não respeitam as regras de validação da base de dados.",
        psycopg2.errors.NotNullViolation: "Um campo obrigatório não foi preenchido.",
        psycopg2.errors.ConnectionException: "Não foi possível conectar à base de dados. Por favor, tente novamente mais tarde.",
        psycopg2.errors.OperationalError: "Ocorreu um erro operacional na base de dados."
    }
    
    return handle_error(
        error_message="Erro na operação de base de dados",
        log_traceback=True,
        reraise=True,
        exception_map=db_error_map
    )