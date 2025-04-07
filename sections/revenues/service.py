import pandas as pd
from typing import Dict, Optional
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error

class RevenueService(BaseService):
    """
    Service for managing revenue data.
    Inherits common CRUD operations from BaseService and extends with calendar functionality.
    """
    table_name = 'revenue'
    primary_key = 'id'
    default_order_by = 'created_at DESC'

    @classmethod
    @handle_service_error("Erro ao obter registo de receita")
    def get(cls, record_id: int) -> Optional[Dict]:
        """
        Get a single revenue record by ID with additional information about driver and car.
        
        Args:
            record_id: ID of the revenue record
            
        Returns:
            Dictionary with revenue data including driver and car details, or None if not found
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        r.*, 
                        d.display_name AS driver_name,
                        c.license_plate,
                        c.brand AS car_brand,
                        c.model AS car_model
                    FROM revenue r
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    LEFT JOIN cars c ON r.car_id = c.id
                    WHERE r.id = %s
                """
                cur.execute(query, (record_id,))
                result = cur.fetchone()
                
                if not result:
                    return None
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cur.description]
                
                # Create dictionary from column names and values
                return dict(zip(columns, result))

    @classmethod
    @handle_service_error("Erro ao carregar dados de receitas")
    def get_many(cls, conditions: Dict = None, order_by: str = None) -> pd.DataFrame:
        """
        Load all revenue records with additional information about drivers and cars.
        
        Args:
            conditions: Dictionary of column-value pairs for WHERE clause
            order_by: Column name to order by
            
        Returns:
            DataFrame with revenue data including driver and car details
        """
        # Base query with JOINs
        query = """
            SELECT 
                r.*, 
                d.display_name AS driver_name,
                c.license_plate,
                c.brand AS car_brand,
                c.model AS car_model
            FROM revenue r
            LEFT JOIN drivers d ON r.driver_id = d.id
            LEFT JOIN cars c ON r.car_id = c.id
        """
        params = []
        
        # Add WHERE clause if conditions provided
        if conditions:
            where_clauses = []
            for col, val in conditions.items():
                # Check if column is in the revenue table or in joined tables
                if col.startswith('driver_'):
                    # For driver fields, modify the column reference
                    where_clauses.append(f"d.{col[7:]} = %s")
                elif col.startswith('car_'):
                    # For car fields, modify the column reference
                    where_clauses.append(f"c.{col[4:]} = %s")
                else:
                    # For revenue fields, use as is
                    where_clauses.append(f"r.{col} = %s")
                params.append(val)
            
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add ORDER BY clause
        order_by = order_by or cls.default_order_by
        if order_by:
            # Check if order by column has a table prefix
            if '.' not in order_by:
                query += f" ORDER BY r.{order_by}"
            else:
                query += f" ORDER BY {order_by}"
        
        # Execute query using pandas
        engine = get_db_engine()
        return pd.read_sql_query(query, engine, params=tuple(params) if params else None)
