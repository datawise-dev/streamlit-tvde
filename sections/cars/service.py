import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error

class CarService(BaseService):
    """
    Service for managing car data.
    Uses standard operations from BaseService.
    """
    table_name = 'cars'
    primary_key = 'id'
    default_order_by = 'license_plate'
    
    # Standard methods inherited from BaseService:
    # insert(data)
    # update(record_id, data)
    # delete(record_id)
    # get(record_id)
    # get_many(conditions, order_by)
    
    # Car-specific methods
    
    @classmethod
    @handle_service_error("Error getting license plates")
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
        
        df = pd.read_sql_query(query, engine)
        return list(df.itertuples(index=False, name=None))
    
    @classmethod
    @handle_service_error("Error getting active cars")
    def get_active_cars(cls) -> pd.DataFrame:
        """
        Get all active cars.
        
        Returns:
            DataFrame containing data for active cars only
        """
        return cls.get_many(conditions={'is_active': True})
    
    @classmethod
    @handle_service_error("Error getting car statistics")
    def get_summary(cls) -> Dict:
        """
        Get statistics about cars.
        
        Returns:
            Dictionary with statistics
        """
        engine = get_db_engine()
        stats = {}
        
        # Total cars
        query = "SELECT COUNT(*) FROM cars"
        df = pd.read_sql_query(query, engine)
        stats['total_cars'] = df.iloc[0, 0]
        
        # Cars by category
        query = "SELECT category, COUNT(*) FROM cars GROUP BY category"
        df = pd.read_sql_query(query, engine)
        stats['cars_by_category'] = df.set_index('category').to_dict()['count']
        
        return stats
