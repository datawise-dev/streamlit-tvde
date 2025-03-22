import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error
from utils.validators import validate_data, get_ga_expense_validators


class GAExpenseService(BaseService):
    """
    Service for managing G&A (General and Administrative) expense data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'ga_expenses'
    primary_key = 'id'
    default_order_by = 'start_date DESC'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate G&A expense data using the validation system.
        
        Args:
            data: Dictionary containing G&A expense data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_ga_expense_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Error inserting G&A expense")
    def insert_ga_expense(cls, data: Dict) -> bool:
        """
        Insert a new G&A expense record with validation.
        
        Args:
            data: Dictionary containing G&A expense data
            
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
    @handle_service_error("Error updating G&A expense")
    def update_ga_expense(cls, ga_expense_id: int, data: Dict) -> bool:
        """
        Update an existing G&A expense record with validation.
        
        Args:
            ga_expense_id: ID of the G&A expense to update
            data: Dictionary containing G&A expense data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data before update
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid data: {', '.join(errors)}")
            
        return cls.update(ga_expense_id, data)

    @classmethod
    @handle_service_error("Error deleting G&A expense")
    def delete_ga_expense(cls, ga_expense_id: int) -> bool:
        """
        Delete a G&A expense record.
        
        Args:
            ga_expense_id: ID of the G&A expense to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        return cls.delete(ga_expense_id)

    @classmethod
    @handle_service_error("Error loading G&A expenses")
    def load_ga_expenses(cls) -> pd.DataFrame:
        """
        Load all G&A expense records.
        
        Returns:
            DataFrame containing G&A expense data
            
        Raises:
            Exception: If query error occurs
        """
        query = """
            SELECT 
                id, expense_type, start_date, end_date, payment_date,
                amount, vat, description, created_at
            FROM ga_expenses
            ORDER BY start_date DESC
        """
        engine = get_db_engine()
        return pd.read_sql_query(query, engine)
    
    @classmethod
    @handle_service_error("Error getting G&A expense")
    def get_ga_expense(cls, ga_expense_id: int) -> Dict:
        """
        Get a G&A expense's complete information by ID.
        
        Args:
            ga_expense_id: ID of the G&A expense to retrieve
            
        Returns:
            Dictionary containing G&A expense data or None if not found
            
        Raises:
            Exception: If query error occurs
        """
        return cls.get(ga_expense_id)

    @classmethod
    @handle_service_error("Error getting expense summary")
    def get_expense_summary(cls, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get a summary of G&A expenses by type within a date range.
        
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
            SELECT 
                expense_type, 
                SUM(amount) as total_amount, 
                SUM(amount * (1 + COALESCE(vat, 0)/100)) as total_with_vat,
                COUNT(*) as count
            FROM ga_expenses
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
            'total_with_vat': df['total_with_vat'].sum() if not df.empty else 0,
            'by_type': df.set_index('expense_type')[['total_amount', 'total_with_vat', 'count']].to_dict('index') if not df.empty else {}
        }
        
        return result