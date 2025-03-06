import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from services.base_service import BaseService
from utils.error_handlers import handle_service_error
from utils.validators import validate_data, get_car_expense_validators


class CarExpenseService(BaseService):
    """
    Service for managing car expense data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'car_expenses'
    primary_key = 'id'
    default_order_by = 'start_date DESC'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate car expense data using the validation system.
        
        Args:
            data: Dictionary containing car expense data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_car_expense_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Error inserting car expense")
    def insert_car_expense(cls, data: Dict) -> bool:
        """
        Insert a new car expense record with validation.
        
        Args:
            data: Dictionary containing car expense data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate the data before insertion
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid data: {', '.join(errors)}")
            
        return cls.insert(data)

    @classmethod
    @handle_service_error("Error updating car expense")
    def update_car_expense(cls, car_expense_id: int, data: Dict) -> bool:
        """
        Update an existing car expense record with validation.
        
        Args:
            car_expense_id: ID of the car expense to update
            data: Dictionary containing car expense data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data before update
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid data: {', '.join(errors)}")
            
        return cls.update(car_expense_id, data)

    @classmethod
    @handle_service_error("Error deleting car expense")
    def delete_car_expense(cls, car_expense_id: int) -> bool:
        """
        Delete a car expense record.
        
        Args:
            car_expense_id: ID of the car expense to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        return cls.delete(car_expense_id)

    @classmethod
    @handle_service_error("Error loading car expenses")
    def load_car_expenses(cls) -> pd.DataFrame:
        """
        Load all car expense records with car details.
        
        Returns:
            DataFrame containing car expense data
            
        Raises:
            Exception: If query error occurs
        """
        query = """
            SELECT 
                ce.id, ce.car_id, ce.expense_type, ce.start_date, ce.end_date, 
                ce.amount, ce.description, ce.created_at,
                c.license_plate, c.brand, c.model
            FROM car_expenses ce
            JOIN cars c ON ce.car_id = c.id
            ORDER BY ce.start_date DESC
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)
    
    @classmethod
    @handle_service_error("Error getting car expense")
    def get_car_expense(cls, car_expense_id: int) -> Dict:
        """
        Get a car expense's complete information by ID.
        
        Args:
            car_expense_id: ID of the car expense to retrieve
            
        Returns:
            Dictionary containing car expense data or None if not found
            
        Raises:
            Exception: If query error occurs
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        ce.id, ce.car_id, ce.expense_type, ce.start_date, ce.end_date, 
                        ce.amount, ce.description,
                        c.license_plate, c.brand, c.model
                    FROM car_expenses ce
                    JOIN cars c ON ce.car_id = c.id
                    WHERE ce.id = %s
                """, (car_expense_id,))
                result = cur.fetchone()
                
                if not result:
                    return None
                
                return {
                    'id': result[0],
                    'car_id': result[1],
                    'expense_type': result[2],
                    'start_date': result[3],
                    'end_date': result[4],
                    'amount': float(result[5]) if result[5] else 0.0,
                    'description': result[6],
                    'license_plate': result[7],
                    'brand': result[8],
                    'model': result[9]
                }

    @classmethod
    @handle_service_error("Error getting expenses for car")
    def get_expenses_for_car(cls, car_id: int) -> pd.DataFrame:
        """
        Get all expenses for a specific car.
        
        Args:
            car_id: ID of the car to get expenses for
            
        Returns:
            DataFrame containing car expense data
            
        Raises:
            Exception: If query error occurs
        """
        query = """
            SELECT 
                id, car_id, expense_type, start_date, end_date, 
                amount, description, created_at
            FROM car_expenses
            WHERE car_id = %s
            ORDER BY start_date DESC
        """
        
        engine = get_db_engine()
        return pd.read_sql_query(query, engine, params=[car_id])

    @classmethod
    @handle_service_error("Error getting expense summary")
    def get_expense_summary(cls, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get a summary of car expenses by type within a date range.
        
        Args:
            start_date: Optional start date for filtering (format: 'YYYY-MM-DD')
            end_date: Optional end date for filtering (format: 'YYYY-MM-DD')
            
        Returns:
            Dictionary containing expense summary data
            
        Raises:
            Exception: If query error occurs
        """
        params = []
        query = """
            SELECT expense_type, SUM(amount) as total_amount, COUNT(*) as count
            FROM car_expenses
            WHERE 1=1
        """
        
        if start_date:
            query += " AND start_date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND (end_date IS NULL OR end_date <= %s)"
            params.append(end_date)
            
        query += " GROUP BY expense_type ORDER BY total_amount DESC"
        
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine, params=params)
        
        # Convert to a more usable format
        result = {
            'total': df['total_amount'].sum() if not df.empty else 0,
            'by_type': df.set_index('expense_type')[['total_amount', 'count']].to_dict('index') if not df.empty else {}
        }
        
        return result