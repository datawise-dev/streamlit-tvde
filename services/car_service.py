import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService
from utils.error_handlers import handle_service_error
from utils.validators import validate_data, get_car_validators


class CarService(BaseService):
    """
    Service for managing car data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'cars'
    primary_key = 'id'
    default_order_by = 'license_plate'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate car data using the validation system.
        
        Args:
            data: Dictionary containing car data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_car_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Erro ao inserir carro")
    def insert_car(cls, data: Dict) -> bool:
        """
        Insert a new car record with validation.
        
        Args:
            data: Dictionary containing car data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate the data before insertion
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
            
        return cls.insert(data)

    @classmethod
    @handle_service_error("Erro ao atualizar carro")
    def update_car(cls, car_id: int, data: Dict) -> bool:
        """
        Update an existing car record with validation.
        
        Args:
            car_id: ID of the car to update
            data: Dictionary containing car data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data before update
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
            
        return cls.update(car_id, data)

    @classmethod
    @handle_service_error("Erro ao eliminar carro")
    def delete_car(cls, car_id: int) -> bool:
        """
        Delete a car record.
        
        Args:
            car_id: ID of the car to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        return cls.delete(car_id)

    @classmethod
    @handle_service_error("Erro ao carregar dados de carros")
    def load_cars(cls) -> pd.DataFrame:
        """
        Load all cars with enhanced information.
        
        Returns:
            DataFrame containing car data
            
        Raises:
            Exception: If query error occurs
        """
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
    @handle_service_error("Erro ao obter matrículas")
    def get_all_license_plates(cls) -> List[Tuple]:
        """
        Get all available license plates from the cars table.
        
        Returns:
            List of tuples containing (id, license_plate, brand, model) for each car
            
        Raises:
            Exception: If query error occurs
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
    @handle_service_error("Erro ao obter carro")
    def get_car(cls, car_id: int) -> Dict:
        """
        Get a car's complete information by ID.
        
        Args:
            car_id: ID of the car to retrieve
            
        Returns:
            Dictionary containing car data or None if not found
            
        Raises:
            Exception: If query error occurs
        """
        return cls.get(car_id)
