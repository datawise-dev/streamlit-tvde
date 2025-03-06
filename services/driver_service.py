import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService

class DriverService(BaseService):
    """
    Service for managing driver data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'drivers'
    primary_key = 'id'
    default_order_by = 'display_name'
    
    @classmethod
    def insert_driver(cls, data: Dict) -> bool:
        """
        Insert a new driver with enhanced information.
        Validates uniqueness constraints before insertion.
        """
        try:
            # First check if display_name or nif already exists
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM drivers WHERE display_name = %s OR nif = %s",
                        (data['display_name'], data['nif'])
                    )
                    result = cur.fetchone()
                    if result:
                        raise Exception("A driver with the same Display Name or NIF already exists")
            
            # If validation passes, use the base class insert method
            return cls.insert(data)
                    
        except Exception as e:
            raise Exception(f"Error inserting driver: {str(e)}")

    @classmethod
    def update_driver(cls, driver_id: int, data: Dict) -> bool:
        """
        Update driver information with enhanced fields.
        Validates uniqueness constraints before update.
        """
        try:
            # First check if display_name or nif already exists for other drivers
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM drivers WHERE (display_name = %s OR nif = %s) AND id != %s",
                        (data['display_name'], data['nif'], driver_id)
                    )
                    result = cur.fetchone()
                    if result:
                        raise Exception("Another driver with the same Display Name or NIF already exists")
            
            # If validation passes, use the base class update method
            return cls.update(driver_id, data)
                    
        except Exception as e:
            raise Exception(f"Error updating driver: {str(e)}")

    @classmethod
    def delete_driver(cls, driver_id: int) -> bool:
        """Delete a driver by ID."""
        # Use the base class delete method
        return cls.delete(driver_id)
        
    @classmethod
    def get_all_drivers(cls) -> List[Tuple[int, str]]:
        """
        Get all drivers using pandas.
        
        Returns:
            List of tuples containing (id, display_name) for each driver
        """
        # Using SQLAlchemy engine for pandas operations
        engine = get_db_engine()
        
        # Construct the query using SQL for clarity
        query = """
            SELECT id, display_name 
            FROM drivers 
            ORDER BY display_name
        """
        
        try:
            # Read the data into a DataFrame
            df = pd.read_sql_query(query, engine)
            
            # Convert DataFrame to list of tuples for compatibility with existing code
            return list(df.itertuples(index=False, name=None))
        
        except Exception as e:
            raise Exception(f"Error fetching drivers: {str(e)}")

    @classmethod
    def load_drivers(cls) -> pd.DataFrame:
        """Load all drivers with enhanced information."""
        query = """
            SELECT 
                id, display_name, first_name, last_name, nif, 
                address_line1, address_line2, postal_code, location, 
                is_active
            FROM drivers 
            ORDER BY display_name
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)

    @classmethod
    def get_driver(cls, driver_id: int) -> Dict:
        """Get a driver's complete information by ID."""
        # Use the base class get method
        return cls.get(driver_id)
        
    @classmethod
    def get_active_drivers(cls, start_date: str, end_date: str) -> List[Tuple]:
        """
        Get all active drivers for a specific date range.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            List of tuples containing (id, display_name) for each active driver
        """
        # Custom implementation for specific business logic
        query = """
            SELECT id, display_name 
            FROM drivers 
            WHERE is_active = TRUE
            ORDER BY display_name
        """
        
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine)
        
        # Convert DataFrame to list of tuples
        return list(df.itertuples(index=False, name=None))
