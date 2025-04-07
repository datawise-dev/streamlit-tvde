import pandas as pd
from typing import Dict
from database.connection import get_db_engine
from utils.base_service import BaseService
from utils.error_handlers import handle_service_error


class GAExpenseService(BaseService):
    """
    Service for managing G&A (General and Administrative) expense data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'ga_expenses'
    primary_key = 'id'
    default_order_by = 'start_date DESC'

    @classmethod
    @handle_service_error("Error getting expense summary")
    def get_summary(cls, start_date: str = None, end_date: str = None) -> Dict:
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