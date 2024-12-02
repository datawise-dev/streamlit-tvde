import psycopg2
from sqlalchemy import create_engine
from contextlib import contextmanager
from config.database import DB_CONFIG

@contextmanager
def get_db_connection():
    """Context manager for database connections using psycopg2."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_db_engine():
    """Get SQLAlchemy engine for pandas operations."""
    connection_string = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )
    return create_engine(connection_string)
