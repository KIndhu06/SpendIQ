import mysql.connector
import streamlit as st

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"]["port"]),
            connection_timeout=10
        )
        return connection
    except Exception as e:
        st.error(f"DB Connection failed: {e}")
        raise
