import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine

class CarService:
    @staticmethod
    def insert_car(data: Dict) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO cars (
                            license_plate, brand, model, acquisition_cost,
                            acquisition_date, category, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        data['license_plate'], data['brand'], data['model'],
                        data['acquisition_cost'], data['acquisition_date'],
                        data['category'], data.get('is_active', True)
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error inserting car: {str(e)}")

    @staticmethod
    def update_car(car_id: int, data: Dict) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE cars 
                        SET license_plate = %s, brand = %s, model = %s,
                            acquisition_cost = %s, acquisition_date = %s,
                            category = %s, is_active = %s
                        WHERE id = %s
                    ''', (
                        data['license_plate'], data['brand'], data['model'],
                        data['acquisition_cost'], data['acquisition_date'],
                        data['category'], data.get('is_active', True), car_id
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error updating car: {str(e)}")

    @staticmethod
    def delete_car(car_id: int) -> bool:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting car: {str(e)}")

    @staticmethod
    def load_cars() -> pd.DataFrame:
        query = """
            SELECT 
                id, license_plate, brand, model, 
                acquisition_cost, acquisition_date, category, 
                COALESCE(is_active, TRUE) as is_active
            FROM cars 
            ORDER BY acquisition_date DESC
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)
    
    @staticmethod
    def get_all_license_plates() -> List[Tuple]:
        """
        Get all available license plates from the cars table using pandas.
        
        Returns:
            List of tuples containing (id, license_plate, brand, model) for each car
        """
        engine = get_db_engine()
        query = """
            SELECT id, license_plate, brand, model 
            FROM cars 
            WHERE COALESCE(is_active, TRUE) = TRUE
            ORDER BY license_plate
        """
        
        try:
            # Read the data into a DataFrame
            df = pd.read_sql_query(query, engine)
            
            # Convert DataFrame to list of tuples for compatibility with existing code
            return list(df.itertuples(index=False, name=None))
        
        except Exception as e:
            raise Exception(f"Error fetching license plates: {str(e)}")

    @staticmethod
    def get_car(car_id: int) -> Dict:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, license_plate, brand, model, 
                           acquisition_cost, acquisition_date, category,
                           COALESCE(is_active, TRUE) as is_active
                    FROM cars WHERE id = %s
                """, (car_id,))
                result = cur.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'license_plate': result[1],
                        'brand': result[2],
                        'model': result[3],
                        'acquisition_cost': result[4],
                        'acquisition_date': result[5],
                        'category': result[6],
                        'is_active': result[7]
                    }
                return None
