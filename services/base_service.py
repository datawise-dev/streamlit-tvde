from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from database.connection import get_db_connection, get_db_engine
from utils.error_handlers import handle_service_error, handle_database_error

class BaseService:
    """
    Base service class to provide common database operations.
    To be inherited by specific service classes.
    """
    # These should be overridden by child classes
    table_name = None
    primary_key = 'id'
    default_order_by = None
    
    @classmethod
    def _validate_configuration(cls):
        """Validate that required class attributes are set."""
        if cls.table_name is None:
            raise ValueError(f"{cls.__name__} must define table_name class attribute")
    
    @classmethod
    @handle_service_error("Erro ao inserir dados")
    def insert(cls, data: Dict) -> int:
        """
        Generic method to insert a record into the database.
        
        Args:
            data: Dictionary containing column names and values
            
        Returns:
            The ID of the newly inserted record
        
        Raises:
            Exception: If the insert operation fails
        """
        cls._validate_configuration()
        
        columns = list(data.keys())
        placeholders = ["%s"] * len(columns)
        values = [data[col] for col in columns]
        
        query = f"""
            INSERT INTO {cls.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING {cls.primary_key}
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                result = cur.fetchone()
            conn.commit()
        
        return result[0] if result else None
    
    @classmethod
    @handle_service_error("Erro ao atualizar dados")
    def update(cls, record_id: int, data: Dict) -> bool:
        """
        Generic method to update a record in the database.
        
        Args:
            record_id: The ID of the record to update
            data: Dictionary containing column names and values to update
            
        Returns:
            True if successful
            
        Raises:
            Exception: If the update operation fails
        """
        cls._validate_configuration()
        
        set_clauses = [f"{col} = %s" for col in data.keys()]
        values = list(data.values()) + [record_id]
        
        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(set_clauses)}
            WHERE {cls.primary_key} = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()
        
        return True
    
    @classmethod
    @handle_service_error("Erro ao eliminar registo")
    def delete(cls, record_id: int) -> bool:
        """
        Generic method to delete a record from the database.
        
        Args:
            record_id: The ID of the record to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If the delete operation fails
        """
        cls._validate_configuration()
        
        query = f"DELETE FROM {cls.table_name} WHERE {cls.primary_key} = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (record_id,))
            conn.commit()
        
        return True
    
    @classmethod
    @handle_service_error("Erro ao eliminar múltiplos registos")
    def delete_many(cls, record_ids: List[int]) -> bool:
        """
        Generic method to delete multiple records from the database.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If the delete operation fails
        """
        cls._validate_configuration()
        
        query = f"DELETE FROM {cls.table_name} WHERE {cls.primary_key} = ANY(%s)"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (record_ids,))
            conn.commit()
        
        return True
    
    @classmethod
    @handle_service_error("Erro ao obter registo")
    def get(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Generic method to get a single record by ID.
        
        Args:
            record_id: The ID of the record to retrieve
            
        Returns:
            Dictionary with record data or None if not found
            
        Raises:
            Exception: If the query fails
        """
        cls._validate_configuration()
        
        query = f"SELECT * FROM {cls.table_name} WHERE {cls.primary_key} = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (record_id,))
                result = cur.fetchone()
                
                if not result:
                    return None
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cur.description]
                
                # Create dictionary from column names and values
                return dict(zip(columns, result))
    
    @classmethod
    @handle_service_error("Erro ao carregar dados")
    def load_all(cls, conditions: Dict = None, order_by: str = None) -> pd.DataFrame:
        """
        Generic method to load all records that match certain conditions.
        
        Args:
            conditions: Dictionary of column-value pairs for WHERE clause
            order_by: Column name to order by
            
        Returns:
            Pandas DataFrame with results
            
        Raises:
            Exception: If the query fails
        """
        cls._validate_configuration()
        
        query = f"SELECT * FROM {cls.table_name}"
        params = []
        
        # Add WHERE clause if conditions provided
        if conditions:
            where_clauses = []
            for col, val in conditions.items():
                where_clauses.append(f"{col} = %s")
                params.append(val)
            
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add ORDER BY clause
        order_by = order_by or cls.default_order_by
        if order_by:
            query += f" ORDER BY {order_by}"
        
        # Execute query using pandas
        engine = get_db_engine()
        return pd.read_sql_query(query, engine, params=params)
