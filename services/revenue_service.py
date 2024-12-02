from typing import Dict, List
import pandas as pd
from psycopg2.extras import execute_values
from database.connection import get_db_connection, get_db_engine

class RevenueService:
    @staticmethod
    def insert_revenue_data(data: Dict) -> bool:
        """Insert single revenue record into database."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO revenue (
                            start_date, end_date, driver_name, license_plate,
                            platform, gross_revenue, commission_percentage,
                            tip, num_travels, num_kilometers
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        data['start_date'], data['end_date'], data['driver_name'],
                        data['license_plate'], data['platform'], data['gross_revenue'],
                        data['commission_percentage'], data['tip'],
                        data['num_travels'], data['num_kilometers']
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error inserting data: {str(e)}")

    @staticmethod
    def bulk_insert_revenue_data(data_list: List[Dict]) -> bool:
        """Insert multiple revenue records into database."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    columns = [
                        'start_date', 'end_date', 'driver_name', 'license_plate',
                        'platform', 'gross_revenue', 'commission_percentage',
                        'tip', 'num_travels', 'num_kilometers'
                    ]
                    values = [[record[col] for col in columns] for record in data_list]
                    
                    execute_values(cur, '''
                        INSERT INTO revenue (
                            start_date, end_date, driver_name, license_plate,
                            platform, gross_revenue, commission_percentage,
                            tip, num_travels, num_kilometers
                        ) VALUES %s
                    ''', values)
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error bulk inserting data: {str(e)}")

    @staticmethod
    def load_data() -> pd.DataFrame:
        """Load all data from database."""
        query = """
            SELECT 
                id, 
                start_date, 
                end_date, 
                driver_name, 
                license_plate, 
                platform, 
                gross_revenue, 
                commission_percentage, 
                tip, 
                num_travels, 
                num_kilometers,
                created_at
            FROM revenue 
            ORDER BY created_at DESC
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)

    @staticmethod
    def delete_records(ids: List[int]) -> bool:
        """Delete specified records from database."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM revenue WHERE id = ANY(%s)",
                        (ids,)
                    )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting records: {str(e)}")