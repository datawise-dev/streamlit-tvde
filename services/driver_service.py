import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine

class DriverService:
    @staticmethod
    def insert_driver(data: Dict) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO drivers (
                            name, nif, base_salary, start_date, end_date
                        ) VALUES (%s, %s, %s, %s, %s)
                    ''', (
                        data['name'], data['nif'], data['base_salary'],
                        data['start_date'], data['end_date']
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error inserting driver: {str(e)}")

    @staticmethod
    def update_driver(driver_id: int, data: Dict) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE drivers 
                        SET name = %s, nif = %s, base_salary = %s, 
                            start_date = %s, end_date = %s
                        WHERE id = %s
                    ''', (
                        data['name'], data['nif'], data['base_salary'],
                        data['start_date'], data['end_date'], driver_id
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error updating driver: {str(e)}")

    @staticmethod
    def delete_driver(driver_id: int) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting driver: {str(e)}")
        
    @staticmethod
    def get_active_drivers(start_date: str, end_date: str = None) -> List[Tuple[int, str]]:
        """
        Get all drivers active during the specified period using pandas.
        
        A driver is considered active if:
        - Their start_date is before or on the period's end date
        - Their end_date is either NULL or after the period's start date
        
        Returns:
            List of tuples containing (id, name) for each active driver
        """
        # Using SQLAlchemy engine for pandas operations
        engine = get_db_engine()
        
        # Construct the query using SQL for clarity
        query = f"""
            SELECT id, name 
            FROM drivers 
            WHERE start_date <= '{end_date or start_date}'
            AND (end_date IS NULL OR end_date >= '{start_date}')
            ORDER BY name
        """
        
        try:
            # Read the data into a DataFrame
            df = pd.read_sql_query(query, engine)
            
            # Convert DataFrame to list of tuples for compatibility with existing code
            return list(df.itertuples(index=False, name=None))
        
        except Exception as e:
            raise Exception(f"Error fetching active drivers: {str(e)}")

    @staticmethod
    def load_drivers() -> pd.DataFrame:
        query = """
            SELECT 
                id, name, nif, base_salary, 
                start_date, end_date
            FROM drivers 
            ORDER BY name
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)

    @staticmethod
    def get_driver(driver_id: int) -> Dict:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, nif, base_salary, start_date, end_date
                    FROM drivers WHERE id = %s
                """, (driver_id,))
                result = cur.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'nif': result[2],
                        'base_salary': result[3],
                        'start_date': result[4],
                        'end_date': result[5]
                    }
                return None