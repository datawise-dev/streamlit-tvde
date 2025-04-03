import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
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
    @handle_service_error("Erro ao inserir motorista")
    def insert(cls, data: Dict) -> bool:
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
    def update(cls, driver_id: int, data: Dict) -> bool:
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
