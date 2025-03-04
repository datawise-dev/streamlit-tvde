import streamlit as st


"""Display the FAQ section."""
st.title("Frequently Asked Questions")

# Using expanders for each FAQ item
with st.expander("How do I add new revenue data?"):
    st.write("""
        You can add revenue data in two ways:
        1. Using the Manual Entry form in the Revenue Management section
        2. Uploading a CSV file with multiple entries
        
        For manual entry, ensure all required fields are filled correctly. 
        For CSV upload, make sure your file contains all necessary columns and data is in the correct format.
    """)

with st.expander("What file format is supported for data upload?"):
    st.write("""
        The application currently supports CSV (Comma-Separated Values) files. 
        The system provides a flexible column mapping feature that allows you to match your CSV columns 
        with the required fields, even if they have different names.
    """)

with st.expander("How can I edit or delete existing entries?"):
    st.write("""
        You can manage existing entries in the 'View Data' tab of the Revenue Management section:
        - Use the filters to find specific entries
        - Select individual rows or all filtered data for deletion
        - Note that deletions are permanent and cannot be undone
        
        Currently, direct editing of entries is not supported. To correct an entry, 
        you would need to delete the incorrect entry and add a new one.
    """)

with st.expander("What should I do if I encounter an error?"):
    st.write("""
        If you encounter an error:
        1. Check that all required fields are filled correctly
        2. Verify your database connection is active
        3. Ensure date ranges are valid
        4. For CSV uploads, confirm your file is properly formatted
        
        If problems persist, please contact your system administrator with 
        the error message displayed on the screen.
    """)

with st.expander("How are the calculations performed?"):
    st.write("""
        The application performs several calculations automatically:
        - Total revenue is calculated from the gross revenue entries
        - Commission amounts are calculated based on the percentage provided
        - Summary statistics include totals for trips and kilometers
        - Averages are calculated for commission rates
        
        All calculations are performed in real-time when viewing the data.
    """)

# Additional helpful information
st.subheader("Need More Help?")
st.write("""
    This FAQ section covers the most common questions about using the Revenue Management System. 
    For additional assistance or to report technical issues, please contact your system administrator 
    or refer to the system documentation.
""")