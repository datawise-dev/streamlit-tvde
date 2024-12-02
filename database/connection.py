import psycopg2
from contextlib import contextmanager
from config.database import DB_CONFIG

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()