import pandas as pd
from typing import Dict, List, Optional
from database.connection import get_db_connection, get_db_engine
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

class HRExpenseService:
    @staticmethod
    def insert_expense(data: Dict) -> bool:
        """Insert a new HR expense record."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO hr_expenses (
                            driver_id, start_date, end_date, payment_date,
                            base_salary, working_days, meal_allowance_per_day, 
                            other_benefits, notes
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (
                        data['driver_id'], data['start_date'], data['end_date'],
                        data['payment_date'], data['base_salary'], data['working_days'],
                        data['meal_allowance_per_day'],
                        data.get('other_benefits', 0), data.get('notes', '')
                    ))
                    result = cur.fetchone()
                conn.commit()
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error inserting HR expense: {str(e)}")
    
    @staticmethod
    def update_expense(expense_id: int, data: Dict) -> bool:
        """Update an existing HR expense record."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE hr_expenses 
                        SET driver_id = %s, start_date = %s, end_date = %s, 
                            payment_date = %s, base_salary = %s, working_days = %s,
                            meal_allowance_per_day = %s, other_benefits = %s, 
                            notes = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    ''', (
                        data['driver_id'], data['start_date'], data['end_date'],
                        data['payment_date'], data['base_salary'], data['working_days'],
                        data['meal_allowance_per_day'],
                        data.get('other_benefits', 0), data.get('notes', ''),
                        expense_id
                    ))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error updating HR expense: {str(e)}")
    
    @staticmethod
    def delete_expense(expense_id: int) -> bool:
        """Delete an HR expense record."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM hr_expenses WHERE id = %s", (expense_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting HR expense: {str(e)}")
    
    @staticmethod
    def get_expense(expense_id: int) -> Dict:
        """Get a specific HR expense record by ID."""
        try:
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
        except Exception as e:
            raise Exception(f"Error getting HR expense: {str(e)}")
    
    @staticmethod
    def load_expenses() -> pd.DataFrame:
        """Load all HR expense records with driver names."""
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
        
        # Calcular o subsídio de alimentação total
        if not df.empty:
            df['meal_allowance_total'] = (df['working_days'] * df['meal_allowance_per_day']).round(2)
            df['total_expense'] = (df['base_salary'] + df['meal_allowance_total'] + df['other_benefits']).round(2)
            
        return df
    
    @staticmethod
    def get_working_days(year: int, month: int) -> int:
        """Calculate the number of working days in a month (excluding weekends)."""
        # Get the number of days in the month
        num_days = calendar.monthrange(year, month)[1]
        
        # Count working days (Monday to Friday)
        working_days = 0
        for day in range(1, num_days + 1):
            weekday = calendar.weekday(year, month, day)
            if weekday < 5:  # 0-4 represent Monday to Friday
                working_days += 1
                
        return working_days
    
    @staticmethod
    def get_next_month_dates() -> tuple:
        """Get default start and end dates for the next month."""
        today = date.today()
        first_day_next_month = date(today.year, today.month, 1) + relativedelta(months=1)
        last_day_next_month = date(
            first_day_next_month.year, 
            first_day_next_month.month, 
            calendar.monthrange(first_day_next_month.year, first_day_next_month.month)[1]
        )
        return first_day_next_month, last_day_next_month