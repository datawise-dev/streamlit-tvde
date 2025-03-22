from typing import Dict, List, Tuple, Optional
import pandas as pd
from psycopg2.extras import execute_values
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
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
            raise Exception(f"Dados inválidos: {', '.join(errors)}")
            
        # Proceed with insertion
        return cls.insert(data)

    @classmethod
    @handle_service_error("Erro ao atualizar dados de receita")
    def update_revenue(cls, revenue_id: int, data: Dict) -> bool:
        """
        Update a revenue record with validation.
        
        Args:
            revenue_id: ID of the revenue to update
            data: Dictionary containing revenue data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data before update
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise Exception(f"Dados inválidos: {', '.join(errors)}")
            
        # Proceed with update
        return cls.update(revenue_id, data)
            
    @classmethod
    @handle_service_error("Erro ao obter registo de receita")
    def get_revenue(cls, revenue_id: int) -> Optional[Dict]:
        """
        Get a revenue record by ID.
        
        Args:
            revenue_id: ID of the revenue to retrieve
            
        Returns:
            Dictionary with revenue data or None if not found
            
        Raises:
            Exception: If the query fails
        """
        return cls.get(revenue_id)
        
    @classmethod
    @handle_service_error("Erro ao eliminar registo de receita")
    def delete_revenue(cls, revenue_id: int) -> bool:
        """
        Delete a revenue record by ID.
        
        Args:
            revenue_id: ID of the revenue to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        return cls.delete(revenue_id)

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
                raise Exception(f"Dados inválidos no registo {i+1}: {', '.join(errors)}")
                
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
            raise Exception(f"Erro ao inserir dados em massa: {str(e)}")

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
