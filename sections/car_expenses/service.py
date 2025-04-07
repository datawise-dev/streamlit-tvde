import pandas as pd
from typing import Dict
from database.connection import get_db_connection, get_db_engine
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error


class CarExpenseService(BaseService):
    """
    Service for managing car expense data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'car_expenses'
    primary_key = 'id'
    default_order_by = 'start_date DESC'

    @classmethod
    @handle_service_error("Error updating car expense")
    def update(cls, expense_id: int, data: Dict) -> bool:
        """
        Update an existing car expense record with validation.
        
        Args:
            expense_id: ID of the expense to update
            data: Dictionary containing car expense data
            
        Returns:
            True if successful
            
        Raises:
            Exception: If validation fails or update error occurs
        """
        # Add updated_at field to the data
        data_copy = data.copy()
        data_copy['updated_at'] = 'CURRENT_TIMESTAMP'
        
        # Use the base class update method
        return super().update(expense_id, data_copy)
    
    @classmethod
    @handle_service_error("Error getting car expense")
    def get(cls, expense_id: int) -> Dict:
        """
        Get a specific car expense record by ID, including car info.
        This method needs custom implementation due to the JOIN with cars table.
        
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
                        e.id, e.car_id, e.expense_type, e.start_date, e.end_date,
                        e.amount, e.vat, e.description, e.created_at, e.updated_at,
                        c.license_plate, c.brand, c.model
                    FROM car_expenses e
                    JOIN cars c ON e.car_id = c.id
                    WHERE e.id = %s
                """, (expense_id,))
                result = cur.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'car_id': result[1],
                        'expense_type': result[2],
                        'start_date': result[3],
                        'end_date': result[4],
                        'amount': float(result[5]),
                        'vat': float(result[6]) if result[6] is not None else None,
                        'description': result[7],
                        'created_at': result[8],
                        'updated_at': result[9],
                        'license_plate': result[10],
                        'car_name': f"{result[11]} {result[12]}"  # brand + model
                    }
        return None
    
    @classmethod
    @handle_service_error("Error loading car expenses")
    def get_many(cls) -> pd.DataFrame:
        """
        Load all car expense records with car details.
        Custom implementation needed due to JOIN and calculations.
        
        Returns:
            DataFrame containing expense data
            
        Raises:
            Exception: If query error occurs
        """
        query = """
            SELECT 
                e.id, e.car_id, e.expense_type, e.start_date, e.end_date,
                e.amount, e.vat, e.description, e.created_at, e.updated_at,
                c.license_plate, c.brand, c.model
            FROM car_expenses e
            JOIN cars c ON e.car_id = c.id
            ORDER BY e.start_date DESC
        """
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine)
        
        # Calculate total with VAT if applicable
        if not df.empty:
            # Calculate the VAT amount where VAT is not null
            df['vat_amount'] = df['amount'] * df['vat'].fillna(0) / 100
            df['total_with_vat'] = (df['amount'] + df['vat_amount']).round(2)
            
            # Create a car_name column combining brand and model
            df['car_name'] = df['brand'] + ' ' + df['model']
            
        return df
    
    @classmethod
    @handle_service_error("Error getting expense summary by car")
    def get_summary_by_car(cls, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get a summary of car expenses grouped by car within a date range.
        
        Args:
            start_date: Optional start date for filtering (format: 'YYYY-MM-DD')
            end_date: Optional end date for filtering (format: 'YYYY-MM-DD')
            
        Returns:
            Dictionary containing expense summary data by car
            
        Raises:
            Exception: If query error occurs
        """
        params = []
        query = """
            SELECT 
                c.license_plate, 
                c.brand, 
                c.model,
                SUM(e.amount) as total_amount, 
                COUNT(*) as expense_count
            FROM car_expenses e
            JOIN cars c ON e.car_id = c.id
            WHERE 1=1
        """
        
        if start_date:
            query += " AND e.start_date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND (e.end_date IS NULL OR e.end_date <= %s)"
            params.append(end_date)
            
        query += " GROUP BY c.license_plate, c.brand, c.model ORDER BY total_amount DESC"
        
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine, params=params)
        
        # Convert to a more usable format
        result = {
            'total': df['total_amount'].sum() if not df.empty else 0,
            'by_car': {}
        }
        
        for _, row in df.iterrows():
            car_key = row['license_plate']
            result['by_car'][car_key] = {
                'license_plate': row['license_plate'],
                'brand': row['brand'],
                'model': row['model'],
                'total_amount': float(row['total_amount']),
                'expense_count': int(row['expense_count'])
            }
        
        return result

    @classmethod
    @handle_service_error("Error getting expense summary by month")
    def get_monthly_summary(cls, year: int = None) -> Dict:
        """
        Get a summary of car expenses by month for a specific year.
        
        Args:
            year: The year to get monthly data for (defaults to current year)
            
        Returns:
            Dictionary containing monthly expense data
            
        Raises:
            Exception: If query error occurs
        """
        from datetime import datetime
        
        # Default to current year if not specified
        if year is None:
            year = datetime.now().year
            
        query = """
            SELECT 
                EXTRACT(MONTH FROM start_date) as month,
                expense_type,
                SUM(amount) as total_amount
            FROM car_expenses
            WHERE EXTRACT(YEAR FROM start_date) = %s
            GROUP BY month, expense_type
            ORDER BY month, expense_type
        """
        
        engine = get_db_engine()
        df = pd.read_sql_query(query, engine, params=(year,))
        
        # Initialize result with all months
        months = list(range(1, 13))
        result = {
            'year': year,
            'total': 0,
            'by_month': {month: {'total': 0, 'by_type': {}} for month in months}
        }
        
        # Fill in the data
        if not df.empty:
            result['total'] = df['total_amount'].sum()
            
            for _, row in df.iterrows():
                month = int(row['month'])
                expense_type = row['expense_type']
                amount = float(row['total_amount'])
                
                # Add to month total
                result['by_month'][month]['total'] += amount
                
                # Add to expense type within month
                if expense_type not in result['by_month'][month]['by_type']:
                    result['by_month'][month]['by_type'][expense_type] = 0
                    
                result['by_month'][month]['by_type'][expense_type] += amount
                
        return result