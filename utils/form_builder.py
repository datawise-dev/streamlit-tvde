import streamlit as st
from typing import Callable

class FormBuilder:
    def __init__(self, form_name="my_form", title=None):
        """
        Initialize a new form builder.
        
        Args:
            form_name (str): Unique identifier for the form.
            title (str, optional): Title to display at the top of the form.
        """
        self.form_name = form_name
        self.title = title
        self.items = []       # List of items
        self.data = {}
        self.post_submit_callbacks = []
        self.errors = []       # List to store error messages
        
    def create_section(self, title, description=None):
        """
        Add a new section to the form.
        
        Args:
            title (str): Title of the section
            description (str, optional): Description text for the section
            
        Returns:
            FormBuilder: self (for method chaining)
        """
        self.items.append({
            'item_type': 'section',
            'title': title,
            'description': description
        })
        return self
    
    def create_field(self, key, label, type, required=False, validator=None, **kwargs):
        """
        Add a field to the form.
        
        Args:
            key (str): Unique identifier for the field
            label (str): Label for the field
            type (str): Type of field (text, number, select, multiselect, checkbox, textarea)
            required (bool): Whether the field is required
            validator (callable, optional): Function to validate the field value
                                            Should return True if valid, or an error message string if invalid.
            **kwargs: Additional arguments specific to the field type.
                - text: default (str)
                - number: min_value (float), max_value (float), step (float), default (float)
                - select: options (list), default (any)
                - multiselect: options (list), default (list)
                - checkbox: default (bool)
                - textarea: default (str)
            
        Returns:
            FormBuilder: self (for method chaining).
        """
        field = {
            'item_type': 'field',
            'key': key,
            'label': label,
            'type': type,
            'required': required,  # Required appears directly in the field.
            'options': kwargs,     # Additional arguments for the field.
            'validator': validator
        }
        self.items.append(field)
        return self
    
    def create_columns(self, num_columns=2):
        """
        Start a new row with multiple columns.
        
        Args:
            num_columns (int): Number of columns to create
            
        Returns:
            FormBuilder: self (for method chaining)
        """
        self.items.append({
            'item_type': 'column_group_start',
            'num_columns': num_columns
        })
        return self
    
    def end_columns(self):
        """
        End the current multi-column layout.
        
        Returns:
            FormBuilder: self (for method chaining)
        """
        self.items.append({
            'item_type': 'column_group_end'
        })
        return self
    
    def create_submit_button(self, label="Submit", use_full_width=False):
        """
        Add a submit button to the form.
        
        Args:
            label (str): Button text
            use_full_width (bool): Whether the button should take full width
            
        Returns:
            bool: True if the form was submitted
        """
        return st.form_submit_button(label, use_container_width=use_full_width)
    
    def render(self, existing_data=None):
        """
        Render the form in the Streamlit app.
        
        Args:
            existing_data (dict, optional): Dictionary with existing data to pre-fill the form
            
        Returns:
            dict: Form values if submitted, None otherwise
        """
        if existing_data is None:
            existing_data = {}
            
        if self.title:
            st.title(self.title)
        
        # Clear previous errors
        self.errors = []
        # Reset values dictionary
        # self.data = {} ??
        clear_on_submit = existing_data is None
            
        with st.form(key=self.form_name, clear_on_submit=clear_on_submit):
            cols = None
            col_idx = 0
            num_cols = 0
            for item in self.items:
    
                item_type = item['item_type']

                if item_type == 'section':
                    title = item['title']
                    description = item['description']

                    if title:
                        st.subheader(title)
                    if description:
                        st.markdown(description)
                
                if item_type == 'column_group_start':
                    # Determine number of columns from the marker
                    num_cols = item.get('num_columns', 2)
                    cols = st.columns(num_cols)
                    col_idx = 0

                if item_type == 'column_group_end' or col_idx == num_cols:
                    cols = None
                    col_idx = 0
                    num_cols = 0

                if item_type == 'field':
                    if cols:
                        with cols[col_idx]:
                            self._render_field(item, existing_data)
                        col_idx += 1

                    else: # outsite columns
                        self._render_field(item, existing_data)
            
            # Add submit button
            submitted = self.create_submit_button(
                label="Atualizar" if existing_data else "Adicionar",
                use_full_width=True)
            
            if submitted:
                # Validate all fields
                self._validate_all_fields()
                
                # Display error messages at the end of the form
                if self.errors:
                    self._display_errors()
                    return False, self.data
                else:
                    try:
                        # Execute post-submit callbacks
                        for callback, kwargs in self.post_submit_callbacks:
                            callback(self.data, **kwargs)
                        
                        return True, self.data
                    except Exception as e:
                        st.error(f"Erro ao processar dados: {str(e)}")
                        return False, self.data

            return False, self.data
        
    def add_post_submit_callback(self, callback: Callable, **callback_kwargs):
        """
        Add a callback to be executed after successful form submission.
        
        Args:
            callback: Function to be called after submission
            **callback_kwargs: Additional arguments to pass to the callback
            
        Returns:
            EnhancedFormBuilder: self (for method chaining)
        """
        self.post_submit_callbacks.append((callback, callback_kwargs))
        return self
    
    def _render_field(self, field, existing_data):
        """
        Render a single field based on its type.
        
        Args:
            field (dict): Field definition
            existing_data (dict): Dictionary with existing data for pre-filling
        """
        field_type = field['type']
        key = field['key']
        label = field['label']
        required = field.get('required', False)
        options = field['options'].copy()  # Copy to avoid modifying the original
        
        # If existing data exists for this field, set the default value if not already provided
        if key in existing_data and 'default' not in options:
            options['default'] = existing_data[key]

        st_key = f"{self.form_name}_{key}"
        
        if field_type == 'text':
            self.data[key] = self._create_text_input(st_key, label, required=required, **options)
        elif field_type == 'number':
            self.data[key] = self._create_number_input(st_key, label, required=required, **options)
        elif field_type == 'date':
            self.data[key] = self._create_date_input(st_key, label, required=required, **options)
        elif field_type == 'select':
            self.data[key] = self._create_select(st_key, label, required=required, **options)
        elif field_type == 'multiselect':
            self.data[key] = self._create_multiselect(st_key, label, **options)
        elif field_type == 'checkbox':
            self.data[key] = self._create_checkbox(st_key, label, **options)
        elif field_type == 'textarea':
            self.data[key] = self._create_text_area(st_key, label, required=required, **options)
        else:
            raise ValueError(f"field_type '{field_type}' does not exist")
        
    def _display_errors(self):
        # Display error messages at the end of the form
        num_errors = len(self.errors)
        st.error(f"Encontrados {num_errors} erros de validação. Corrija os erros e tente novamente.")
        
        # Expandable container for error details
        with st.expander("Ver detalhes dos erros"):
            for error in self.errors:
                st.warning(error)
        
    def _validate_all_fields(self):
        """
        Validate all field items and collect error messages.
        """
        for item in self.items:
            if item['item_type'] == 'field':
                self._validate_field(item)

    def _validate_field(self, field):
        key = field['key']
        value = self.data.get(key)
        if field.get('required', False) and (value is None or (isinstance(value, str) and value.strip() == "")):
            self.errors.append(f"{field['label']}: This field is required.")
            return
        if field.get('validator'):
            try:
                is_valid, error_message = field['validator'](value)
                if not is_valid:
                    self.errors.append(f"{field['label']}: {error_message}")
            except Exception as e:
                self.errors.append(f"{field['label']}: Validation error ({str(e)})")
    
    def clear(self):
        """
        Clear all values in the form.
        
        Returns:
            FormBuilder: self (for method chaining)
        """
        # This isn't directly supported in Streamlit, but we can reset the internal state
        self.data = {}
        self.errors = []
        # To truly clear form values, users would need to use st.session_state
        return self

    
    def _create_text_input(self, key, label, required=False, default="", **kwargs):
        """
        Add a text input field to the form.
        """
        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        value = st.text_input(
            label=label,
            key=key,
            value=default,
            **kwargs
        )
        return value
    
    def _create_number_input(self, key, label, min_value=None, max_value=None, 
                             step=1, required=False, default=None, **kwargs):
        """
        Add a number input field to the form.
        """
        if default is None:
            default = min_value if min_value is not None else 0.0

        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        value = st.number_input(
            label=label,
            key=key,
            min_value=min_value,
            max_value=max_value,
            step=step,
            value=float(default),
            **kwargs
        )
        return value
    
    def _create_date_input(self, key, label, required=False, default=None, **kwargs):
        """
        Add a date input field to the form.
        """

        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        value = st.date_input(
            label=label,
            key=key,
            value=default,
            **kwargs
        )
        return value
    
    def _create_select(self, key, label, options, required=False, default=None, **kwargs):
        """
        Add a select/dropdown field to the form.
        """
        # If options is empty, set it to a list with an empty string
        if not options:
            options = [""]

        # Sets the index based on the default value if provided
        if default is not None and default in options:
            index = options.index(default)
        else:
            index = 0

        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        value = st.selectbox(
            label=label,
            key=key,
            options=options,
            index=index,
            **kwargs
        )
        return value
    
    def _create_multiselect(self, key, label, options, default=None, **kwargs):
        """
        Add a multiselect field to the form.
        """
        default = default or []
        value = st.multiselect(
            label=label,
            key=key,
            options=options,
            default=default,
            **kwargs
        )
        return value
    
    def _create_checkbox(self, key, label, default=False, **kwargs):
        """
        Add a checkbox field to the form.
        """
        value = st.checkbox(
            label=label,
            key=key,
            value=default,
            **kwargs
        )
        return value
    
    def _create_text_area(self, key, label, required=False, default="", **kwargs):
        """
        Add a text area field to the form.
        """
        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        value = st.text_area(
            label=label,
            key=key,
            value=default,
            **kwargs
        )
        return value
