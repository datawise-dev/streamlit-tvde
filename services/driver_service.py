import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine

class DriverService:
    @staticmethod
    def insert_driver(data: Dict) -> bool:
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
                    
                    # If validation passes, insert the new driver
                    cur.execute('''
                        INSERT INTO drivers (
                            display_name, first_name, last_name, nif, 
                            address_line1, address_line2, postal_code, location
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        data['display_name'], data['first_name'], data['last_name'], data['nif'],
                        data['address_line1'], data.get('address_line2'), data['postal_code'], 
                        data['location']
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error inserting driver: {str(e)}")

    @staticmethod
    def update_driver(driver_id: int, data: Dict) -> bool:
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
                    
                    # If validation passes, update the driver
                    cur.execute('''
                        UPDATE drivers 
                        SET display_name = %s, first_name = %s, last_name = %s, nif = %s,
                            address_line1 = %s, address_line2 = %s, postal_code = %s, location = %s,
                            is_active = %s
                        WHERE id = %s
                    ''', (
                        data['display_name'], data['first_name'], data['last_name'], data['nif'],
                        data['address_line1'], data.get('address_line2'), data['postal_code'], 
                        data['location'], data.get('is_active', True), driver_id
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error updating driver: {str(e)}")

    @staticmethod
    def delete_driver(driver_id: int) -> bool:
        """Delete a driver by ID."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting driver: {str(e)}")
        
    @staticmethod
    def get_all_drivers() -> List[Tuple[int, str]]:
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

    @staticmethod
    def load_drivers() -> pd.DataFrame:
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

    @staticmethod
    def get_driver(driver_id: int) -> Dict:
        """Get a driver's complete information by ID."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, display_name, first_name, last_name, nif, 
                        address_line1, address_line2, postal_code, location,
                        is_active
                    FROM drivers 
                    WHERE id = %s
                """, (driver_id,))
                result = cur.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'display_name': result[1],
                        'first_name': result[2],
                        'last_name': result[3],
                        'nif': result[4],
                        'address_line1': result[5],
                        'address_line2': result[6],
                        'postal_code': result[7],
                        'location': result[8],
                        'is_active': result[9]
                    }
                return None