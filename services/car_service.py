import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService

class CarService(BaseService):
    """
    Service for managing car data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'cars'
    primary_key = 'id'
    default_order_by = 'license_plate'
    
    @classmethod
    def insert_car(cls, data: Dict) -> bool:
        """Insert a new car record."""
        # We could add custom validation here if needed
        return cls.insert(data)

    @classmethod
    def update_car(cls, car_id: int, data: Dict) -> bool:
        """Update an existing car record."""
        # We could add custom validation here if needed
        return cls.update(car_id, data)

    @classmethod
    def delete_car(cls, car_id: int) -> bool:
        """Delete a car record."""
        return cls.delete(car_id)

    @classmethod
    def load_cars(cls) -> pd.DataFrame:
        """Load all cars with enhanced information."""
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
    
    @classmethod
    def get_all_license_plates(cls) -> List[Tuple]:
        """
        Get all available license plates from the cars table.
        
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

    @classmethod
    def get_car(cls, car_id: int) -> Dict:
        """Get a car's complete information by ID."""
        return cls.get(car_id)
