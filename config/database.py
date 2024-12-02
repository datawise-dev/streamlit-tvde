import streamlit as st

#DB_CONFIG = {
#    'dbname': st.secrets.get("DB_NAME", "revenue_db"),
#    'user': st.secrets.get("DB_USER", "postgres"),
#    'password': st.secrets.get("DB_PASSWORD", ""),
#    'host': st.secrets.get("DB_HOST", "localhost"),
#    'port': st.secrets.get("DB_PORT", "5432")
#}

# Database connection parameters
DB_CONFIG = {
    'dbname': "core", #st.secrets.get("DB_NAME", "revenue_db"),
    'user': "jpceia", #st.secrets.get("DB_USER", "postgres"),
    'password': "gS7dzT2eNpJU", #st.secrets.get("DB_PASSWORD", ""),
    'host': "ep-fancy-tree-a2etcj4n-pooler.eu-central-1.aws.neon.tech", #st.secrets.get("DB_HOST", "localhost"),
    'port': 5432 #st.secrets.get("DB_PORT", "5432")
}
