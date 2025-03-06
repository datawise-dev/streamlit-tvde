import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService
from utils.error_handlers import handle_service_error
from utils.validators import validate_data, get_driver_validators

class DriverService(BaseService):
    """
    Service for managing driver data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'drivers'
    primary_key = 'id'
    default_order_by = 'display_name'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate driver data using the validation system.
        
        Args:
            data: Dictionary containing driver data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_driver_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Erro ao inserir motorista")
    def insert_driver(cls, data: Dict) -> bool:
        """
        Insert a new driver with enhanced information.
        Validates uniqueness constraints before insertion.
        
        Args:
            data: Dictionary containing driver data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate the data
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
        
        # Check if display_name or nif already exists
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM drivers WHERE display_name = %s OR nif = %s",
                    (data['display_name'], data['nif'])
                )
                result = cur.fetchone()
                if result:
                    raise ValueError("Já existe um motorista com o mesmo Nome ou NIF")
        
        # If validation passes, use the base class insert method
        return cls.insert(data)

    @classmethod
    @handle_service_error("Erro ao atualizar motorista")
    def update_driver(cls, driver_id: int, data: Dict) -> bool:
        """
        Update driver information with enhanced fields.
        Validates uniqueness constraints before update.
        
        Args:
            driver_id: ID of the driver to update
            data: Dictionary containing driver data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
        
        # Check if display_name or nif already exists for other drivers
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM drivers WHERE (display_name = %s OR nif = %s) AND id != %s",
                    (data['display_name'], data['nif'], driver_id)
                )
                result = cur.fetchone()
                if result:
                    raise ValueError("Já existe outro motorista com o mesmo Nome ou NIF")
        
        # If validation passes, use the base class update method
        return cls.update(driver_id, data)

    @classmethod
    @handle_service_error("Erro ao eliminar motorista")
    def delete_driver(cls, driver_id: int) -> bool:
        """
        Delete a driver by ID.
        
        Args:
            driver_id: ID of the driver to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        # Use the base class delete method
        return cls.delete(driver_id)
        
    @classmethod
    @handle_service_error("Erro ao obter lista de motoristas")
    def get_all_drivers(cls) -> List[Tuple[int, str]]:
        """
        Get all drivers using pandas.
        
        Returns:
            List of tuples containing (id, display_name) for each driver
            
        Raises:
            Exception: If query error occurs
        """
        # Using SQLAlchemy engine for pandas operations
        engine = get_db_engine()
        
        # Construct the query using SQL for clarity
        query = """
            SELECT id, display_name 
            FROM drivers 
            ORDER BY display_name
        """
        
        # Read the data into a DataFrame
        df = pd.read_sql_query(query, engine)
        
        # Convert DataFrame to list of tuples for compatibility with existing code
        return list(df.itertuples(index=False, name=None))

    @classmethod
    @handle_service_error("Erro ao carregar dados de motoristas")
    def load_drivers(cls) -> pd.DataFrame:
        """
        Load all drivers with enhanced information.
        
        Returns:
            DataFrame containing driver data
            
        Raises:
            Exception: If query error occurs
        """
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

    @classmethod
    @handle_service_error("Erro ao obter motorista")
    def get_driver(cls, driver_id: int) -> Dict:
        """
        Get a driver's complete information by ID.
        
        Args:
            driver_id: ID of the driver to retrieve
            
        Returns:
            Dictionary containing driver data or None if not found
            
        Raises:
            Exception: If query error occurs
        """
        # Use the base class get method
        return cls.get(driver_id)
        
    @classmethod
    @handle_service_error("Erro ao obter motoristas ativos")
    def get_active_drivers(cls, start_date: str, end_date: str) -> List[Tuple]:
        """
        Get all active drivers for a specific date range.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            List of tuples containing (id, display_name) for each active driver
            
        Raises:
            Exception: If query error occurs
        """
        # Custom implementation for specific business logic
        query = """
            SELECT id, display_name 
            FROM drivers 
            WHERE is_active = TRUE
            ORDER BY display_name
        """
        
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine)
        
        # Convert DataFrame to list of tuples
        return list(df.itertuples(index=False, name=None))
