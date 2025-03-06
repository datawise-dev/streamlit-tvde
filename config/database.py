import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    'dbname': os.getenv("DB_NAME") or st.secrets.get("DB_NAME", "revenue_db"),
    'user': os.getenv("DB_USER") or st.secrets.get("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD") or st.secrets.get("DB_PASSWORD", ""),
    'host': os.getenv("DB_HOST") or st.secrets.get("DB_HOST", "localhost"),
    'port': os.getenv("DB_PORT") or st.secrets.get("DB_PORT", "5432")
}
