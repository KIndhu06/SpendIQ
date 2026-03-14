import streamlit as st
from utils.db import get_connection
import pandas as pd

st.set_page_config(
    page_title="Family Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
        .welcome-header {
            background: linear-gradient(135deg, #2C3E50, #3498DB);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.switch_page("pages/login.py")
else:
    user = st.session_state['user']
    family_id = user[4]

    st.markdown(f"""
        <div class="welcome-header">
            <h1>💰 Family Finance Tracker</h1>
            <p style="font-size:18px; margin:0;">
                Welcome back, <b>{user[1]}</b>! 👋
            </p>
            <p style="font-size:14px; opacity:0.8; margin:5px 0 0 0;">
                Family ID: {user[4]}
            </p>
        </div>
    """, unsafe_allow_html=True)

    def get_summary(family_id):
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT type, SUM(amount) as total FROM transactions WHERE family_id=%s GROUP BY type",
                conn, params=(family_id,)
            )
            conn.close()
            return df
        except:
            return pd.DataFrame()

    summary_df = get_summary(family_id)
    if not summary_df.empty:
        income = summary_df[summary_df['type']=='income']['total'].sum()
        expense = summary_df[summary_df['type']=='expense']['total'].sum()
        savings = income - expense

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Income", f"₹{income:,.2f}")
        with col2:
            st.metric("💸 Total Expenses", f"₹{expense:,.2f}")
        with col3:
            st.metric("🏦 Savings", f"₹{savings:,.2f}",
                delta="Saving ✅" if savings >= 0 else "Overspending ❌")
    else:
        st.info("👆 Upload your first bank statement to see your summary!")

    st.write("---")
    st.subheader("📌 What would you like to do?")
    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💼 My Finances", use_container_width=True):
            st.switch_page("pages/finance.py")
    with col2:
        if st.button("📄 Download Report", use_container_width=True):
            st.switch_page("pages/report.py")
    with col3:
        if st.button("👤 My Profile", use_container_width=True):
            st.switch_page("pages/profile.py")

    st.write("")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")