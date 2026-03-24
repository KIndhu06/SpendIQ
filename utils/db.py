import pymysql
import streamlit as st

def get_connection():
    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"]["port"]),
            ssl={"fake_flag_to_enable_ssl": True},
            connect_timeout=10
        )
        return connection
    except Exception as e:
        st.error(f"DB Connection failed: {e}")
        raise
