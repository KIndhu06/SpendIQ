import pymysql
import streamlit as st

def get_connection():
    connection = pymysql.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"],
        ssl_verify_cert=False,
        ssl_verify_identity=False
    )
    return connection
