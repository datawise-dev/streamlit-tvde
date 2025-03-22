import pandas as pd
from typing import Dict, List, Optional, Tuple
from database.connection import get_db_connection, get_db_engine
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error
from utils.validators import validate_data, get_hr_expense_validators

class HRExpenseService(BaseService):
    """
    Service for managing HR expenses.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'hr_expenses'
    primary_key = 'id'
    default_order_by = 'payment_date DESC'
    
    @classmethod
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate HR expense data using the validation system.
        
        Args:
            data: Dictionary containing HR expense data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        field_validators, cross_validators = get_hr_expense_validators()
        errors = validate_data(data, field_validators, cross_validators)
        return len(errors) == 0, errors
    
    @classmethod
    @handle_service_error("Erro ao inserir despesa")
    def insert_expense(cls, data: Dict) -> int:
        """
        Insert a new HR expense record with validation.
        
        Args:
            data: Dictionary containing HR expense data
            
        Returns:
            ID of the newly inserted record
            
        Raises:
            Exception: If validation fails or insertion error occurs
        """
        # Validate the data
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
            
        # Use the base class insert method
        return cls.insert(data)
    
    @classmethod
    @handle_service_error("Erro ao atualizar despesa")
    def update_expense(cls, expense_id: int, data: Dict) -> bool:
        """
        Update an existing HR expense record with validation.
        
        Args:
            expense_id: ID of the expense to update
            data: Dictionary containing HR expense data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Validate the data
        is_valid, errors = cls.validate(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
            
        # Add updated_at field to the data
        data_copy = data.copy()
        data_copy['updated_at'] = 'CURRENT_TIMESTAMP'
        
        # Use the base class update method
        return cls.update(expense_id, data_copy)
    
    @classmethod
    @handle_service_error("Erro ao eliminar despesa")
    def delete_expense(cls, expense_id: int) -> bool:
        """
        Delete an HR expense record.
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            True if successful
            
        Raises:
            Exception: If delete error occurs
        """
        # Use the base class delete method
        return cls.delete(expense_id)
    
    @classmethod
    @handle_service_error("Erro ao obter despesa")
    def get_expense(cls, expense_id: int) -> Dict:
        """
        Get a specific HR expense record by ID, including driver name.
        This method needs custom implementation due to the JOIN with drivers table.
        
        Args:
            expense_id: ID of the expense to retrieve
            
        Returns:
            Dictionary containing expense data or None if not found
            
        Raises:
            Exception: If query error occurs
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        e.id, e.driver_id, e.start_date, e.end_date, e.payment_date,
                        e.base_salary, e.working_days, e.meal_allowance_per_day, 
                        e.other_benefits, e.notes,
                        d.display_name as driver_name
                    FROM hr_expenses e
                    JOIN drivers d ON e.driver_id = d.id
                    WHERE e.id = %s
                """, (expense_id,))
                result = cur.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'driver_id': result[1],
                        'start_date': result[2],
                        'end_date': result[3],
                        'payment_date': result[4],
                        'base_salary': float(result[5]),
                        'working_days': result[6],
                        'meal_allowance_per_day': float(result[7]),
                        'other_benefits': float(result[8]),
                        'notes': result[9],
                        'driver_name': result[10]
                    }
        return None
    
    @classmethod
    @handle_service_error("Erro ao carregar despesas")
    def load_expenses(cls) -> pd.DataFrame:
        """
        Load all HR expense records with driver names.
        Custom implementation needed due to JOIN and calculations.
        
        Returns:
            DataFrame containing expense data
            
        Raises:
            Exception: If query error occurs
        """
        query = """
            SELECT 
                e.id, e.driver_id, e.start_date, e.end_date, e.payment_date,
                e.base_salary, e.working_days, e.meal_allowance_per_day, 
                e.other_benefits, e.notes,
                d.display_name as driver_name
            FROM hr_expenses e
            JOIN drivers d ON e.driver_id = d.id
            ORDER BY e.payment_date DESC
        """
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine)
        
        # Calculate meal allowance total and total expense
        if not df.empty:
            df['meal_allowance_total'] = (df['working_days'] * df['meal_allowance_per_day']).round(2)
            df['total_expense'] = (df['base_salary'] + df['meal_allowance_total'] + df['other_benefits']).round(2)
            
        return df
    
    @classmethod
    def get_working_days(cls, year: int, month: int) -> int:
        """
        Calculate the number of working days in a month (excluding weekends).
        
        Args:
            year: The year to calculate for
            month: The month to calculate for (1-12)
            
        Returns:
            Number of working days in the month
        """
        # Get the number of days in the month
        num_days = calendar.monthrange(year, month)[1]
        
        # Count working days (Monday to Friday)
        working_days = 0
        for day in range(1, num_days + 1):
            weekday = calendar.weekday(year, month, day)
            if weekday < 5:  # 0-4 represent Monday to Friday
                working_days += 1
                
        return working_days
    
    @classmethod
    def get_next_month_dates(cls) -> Tuple[date, date]:
        """
        Get default start and end dates for the next month.
        
        Returns:
            Tuple containing (first_day_of_next_month, last_day_of_next_month)
        """
        today = date.today()
        first_day_next_month = date(today.year, today.month, 1) + relativedelta(months=1)
        last_day_next_month = date(
            first_day_next_month.year, 
            first_day_next_month.month, 
            calendar.monthrange(first_day_next_month.year, first_day_next_month.month)[1]
        )
        return first_day_next_month, last_day_next_month
