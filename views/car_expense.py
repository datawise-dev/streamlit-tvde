import streamlit as st
import time
from datetime import date
from services.car_expense_service import CarExpenseService
from services.car_service import CarService
from utils.error_handlers import handle_streamlit_error

@st.dialog("Delete Car Expense")
@handle_streamlit_error()
def delete_car_expense(expense_id):
    """Dialog to confirm deletion of a car expense record with error handling."""
    st.write("Please confirm that you want to delete this expense")
    if st.button("Confirm"):
        with st.spinner("Deleting Expense...", show_time=True):
            CarExpenseService.delete_car_expense(expense_id)
        st.success("Expense deleted")
        time.sleep(2)
        st.page_link("views/car_expenses.py")

@handle_streamlit_error()
def car_expense_form(existing_data=None):
    """Display form for adding or editing car expense data with error handling."""
    if existing_data is None:
        existing_data = dict()

    data = dict()

    # Create form for car expense data
    with st.form("car_expense_form", clear_on_submit=True):
        st.subheader("Expense Information")

        # Car selection
        try:
            cars = CarService.get_all_license_plates()
            if not cars:
                st.warning("No cars available in the system")
                car_options = {}
            else:
                # Create a dictionary for car selection
                car_options = {
                    car[0]: f"{car[1]} ({car[2]} {car[3]})" for car in cars
                }
            
            default_index = 0
            if existing_data.get('car_id') in car_options:
                default_index = list(car_options.keys()).index(existing_data.get('car_id'))
            
            car_id = st.selectbox(
                "Car *",
                options=list(car_options.keys()) if car_options else [],
                format_func=lambda x: car_options.get(x, "Select a car"),
                index=default_index,
                help="Select the car for this expense"
            )
            data["car_id"] = car_id
            
        except Exception as e:
            st.error(f"Error loading cars: {str(e)}")

        # Expense type selection
        expense_type_options = ["Credit", "Gasoline", "Tolls", "Repairs", "Washing"]
        default_type_index = 0
        if existing_data.get('expense_type') in expense_type_options:
            default_type_index = expense_type_options.index(existing_data.get('expense_type'))
        
        data["expense_type"] = st.selectbox(
            "Expense Type *",
            options=expense_type_options,
            index=default_type_index,
            help="Type of car expense"
        )

        # Date information
        col1, col2 = st.columns(2)
        
        with col1:
            data["start_date"] = st.date_input(
                "Start Date *",
                value=existing_data.get('start_date', date.today()),
                help="When the expense occurred or started"
            )
            
        with col2:
            data["end_date"] = st.date_input(
                "End Date",
                value=existing_data.get('end_date'),
                help="End date (if applicable, e.g., for credit payments)"
            ) if data["expense_type"] == "Credit" else None

        # Amount
        data["amount"] = st.number_input(
            "Amount (€) *",
            min_value=0.0,
            value=float(existing_data.get('amount', 0)),
            step=0.01,
            format="%.2f",
            help="Cost amount in euros"
        )

        # Description
        data["description"] = st.text_area(
            "Description",
            value=existing_data.get('description', ''),
            help="Additional details about the expense"
        )

        # Form submission
        st.markdown("**Required fields*")

        # Change button text based on mode
        button_text = "Update" if existing_data.get('id') else "Add"
        submit_button = st.form_submit_button(button_text, use_container_width=True)

        return submit_button, data


# Main page content
@handle_streamlit_error()
def main():
    """Main car expense form view with error handling."""
    
    # Set page title based on mode
    existing_data = None
    if "id" in st.query_params:
        try:
            expense_id = int(st.query_params["id"])
            # Get expense data
            existing_data = CarExpenseService.get_car_expense(expense_id)
            if not existing_data:
                st.error("Expense not found.")
                st.stop()
                
            col1, col2 = st.columns(2)
            
            with col1:
                st.title(f"Edit Car Expense")
                
            with col2:
                if st.button("Delete This Expense"):
                    delete_car_expense(expense_id)
        except Exception as e:
            st.error(f"Error loading expense information: {str(e)}")
            existing_data = None
    else:
        st.title("Add New Car Expense")

    # Show the form
    submit_button, expense_data = car_expense_form(existing_data)

    # Handle form submission
    if submit_button:
        # Required fields
        required_fields = ["car_id", "start_date", "expense_type", "amount"]

        # Convert dates to strings
        if isinstance(expense_data.get('start_date'), date):
            expense_data['start_date'] = expense_data['start_date'].strftime('%Y-%m-%d')
            
        if expense_data.get('end_date') and isinstance(expense_data.get('end_date'), date):
            expense_data['end_date'] = expense_data['end_date'].strftime('%Y-%m-%d')

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if not expense_data.get(field):
                missing_fields.append(field)
                
        if missing_fields:
            st.error(f"Missing required fields: {', '.join(missing_fields)}")
            st.stop()
        
        # Validate dates if end_date is provided
        if expense_data.get('end_date') and expense_data['end_date'] < expense_data['start_date']:
            st.error("End date cannot be before start date")
            st.stop()

        # Update or insert
        try:
            if existing_data and 'id' in existing_data:
                with st.spinner("Updating data..."):
                    CarExpenseService.update_car_expense(existing_data['id'], expense_data)
                st.success("Car expense updated successfully!")
                st.page_link("views/car_expenses.py", label="Back to Car Expenses List")
            else:
                with st.spinner("Adding data..."):
                    CarExpenseService.insert_car_expense(expense_data)
                st.success("Car expense added successfully!")
                time.sleep(2)
                st.rerun()
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")

    # Link to return to list
    st.page_link("views/car_expenses.py", label="Back to Car Expenses List", icon="⬅️")

# Execute the main function
main()
