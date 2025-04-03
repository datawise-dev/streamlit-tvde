import psycopg2
from sqlalchemy import create_engine
from contextlib import contextmanager
from config.database import DB_CONFIG
import logging
from utils.error_handlers import handle_database_error

@contextmanager
@handle_database_error()
def get_db_connection():
    """
    Context manager for database connections using psycopg2.
    Includes error handling for database operations.
    
    Yields:
        Connection: psycopg2 connection object
        
    Raises:
        Exception: If connection error occurs
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {str(e)}")
        raise Exception("Não foi possível estabelecer ligação à base de dados. Por favor, verifique as configurações e tente novamente.")

@handle_database_error()
def get_db_engine():
    """
    Get SQLAlchemy engine for pandas operations.
    Includes error handling for engine creation.
    
    Returns:
        Engine: SQLAlchemy engine object
        
    Raises:
        Exception: If engine creation error occurs
    """
    try:
        connection_string = (
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        )
        return create_engine(connection_string)
    except Exception as e:
        print(f"Error creating database engine: {str(e)}")
        raise Exception("Não foi possível criar o motor de base de dados. Por favor, verifique as configurações e tente novamente.")
