from typing import Dict, List, Tuple
import pandas as pd
from psycopg2.extras import execute_values
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService
from utils.validators import validate_data, get_revenue_validators
from utils.error_handlers import handle_service_error

class RevenueService(BaseService):
    """
    Service for managing revenue data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'revenue'
    primary_key = 'id'
    default_order_by = 'created_at DESC'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate revenue data using the validation system.
        
        Args:
            data: Dictionary containing revenue data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_revenue_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Erro ao inserir dados de receita")
    def insert_revenue_data(cls, data: Dict) -> bool:
        """
        Insert single revenue record into database.
        Includes validation before insertion.
        
        Args:
            data: Dictionary containing revenue data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate the data before insertion
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise Exception(f"Invalid data: {', '.join(errors)}")
            
        # Proceed with insertion
        return cls.insert(data)

    @classmethod
    @handle_service_error("Erro ao inserir múltiplos dados de receita")
    def bulk_insert_revenue_data(cls, data_list: List[Dict]) -> bool:
        """
        Insert multiple revenue records into database.
        Includes validation of each record before insertion.
        
        Args:
            data_list: List of dictionaries containing revenue data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate all records first
        for i, data in enumerate(data_list):
            is_valid, errors = cls.validate(data)
            if not is_valid:
                raise Exception(f"Invalid data in record {i+1}: {', '.join(errors)}")
                
        # Proceed with bulk insertion
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    columns = [
                        'start_date', 'end_date', 'driver_name', 'license_plate',
                        'platform', 'gross_revenue', 'commission_percentage',
                        'tip', 'num_travels', 'num_kilometers'
                    ]
                    values = [[record[col] for col in columns] for record in data_list]
                    
                    execute_values(cur, f'''
                        INSERT INTO {cls.table_name} (
                            {', '.join(columns)}
                        ) VALUES %s
                    ''', values)
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error bulk inserting data: {str(e)}")

    @classmethod
    @handle_service_error("Erro ao carregar dados de receita")
    def load_data(cls) -> pd.DataFrame:
        """Load all data from database."""
        query = f"""
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
            FROM {cls.table_name} 
            ORDER BY created_at DESC
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)

    @classmethod
    @handle_service_error("Erro ao eliminar registos")
    def delete_records(cls, ids: List[int]) -> bool:
        """Delete specified records from database."""
        return cls.delete_many(ids)
