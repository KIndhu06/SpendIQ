import streamlit as st
import pandas as pd
from utils.db import get_connection
import hashlib

st.set_page_config(
    page_title="SpendIQ",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.switch_page("pages/login.py")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_family_members(family_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT username, email, created_at FROM users WHERE family_id = %s",
        conn, params=(family_id,)
    )
    conn.close()
    return df

def update_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s WHERE id = %s",
        (hash_password(new_password), user_id)
    )
    conn.commit()
    conn.close()

def get_user_stats(family_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM transactions WHERE family_id = %s", (family_id,))
    total_transactions = cursor.fetchone()[0]
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE family_id = %s AND type = 'income'",
        (family_id,))
    total_income = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE family_id = %s AND type = 'expense'",
        (family_id,))
    total_expense = cursor.fetchone()[0] or 0
    conn.close()
    return total_transactions, total_income, total_expense

user_id = st.session_state['user'][0]
family_id = st.session_state['user'][4]

st.title("👤 My Profile")
st.write(f"Welcome, **{st.session_state['user'][1]}**!")

st.write("---")
st.subheader("📋 Your Account Details")
col1, col2 = st.columns(2)
with col1:
    st.info(f"👤 **Name:** {st.session_state['user'][1]}")
    st.info(f"📧 **Email:** {st.session_state['user'][2]}")
with col2:
    st.info(f"👨‍👩‍👧 **Family ID:** {st.session_state['user'][4]}")
    st.info(f"📅 **Joined:** {st.session_state['user'][5]}")

st.write("---")
st.subheader("📊 Your Account Statistics")
total_transactions, total_income, total_expense = get_user_stats(family_id)
savings = total_income - total_expense

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📝 Transactions", total_transactions)
with col2:
    st.metric("💰 Total Income", f"₹{total_income:,.2f}")
with col3:
    st.metric("💸 Total Expense", f"₹{total_expense:,.2f}")
with col4:
    st.metric("🏦 Total Savings", f"₹{savings:,.2f}")

st.write("---")
st.subheader("👨‍👩‍👧 Family Members")
family_df = get_family_members(family_id)
if not family_df.empty:
    st.dataframe(family_df, use_container_width=True)
else:
    st.info("No other family members found.")

st.write("---")
st.subheader("🔐 Change Password")
with st.expander("Click to change your password"):
    current_pass = st.text_input("Current Password", type="password", key="curr_pass")
    new_pass = st.text_input("New Password", type="password", key="new_pass")
    confirm_pass = st.text_input("Confirm New Password", type="password", key="conf_pass")
    if st.button("🔄 Update Password"):
        if not current_pass or not new_pass or not confirm_pass:
            st.error("❌ Please fill all fields!")
        elif new_pass != confirm_pass:
            st.error("❌ Passwords do not match!")
        elif len(new_pass) < 6:
            st.error("❌ Password must be at least 6 characters!")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND password = %s",
                (user_id, hash_password(current_pass))
            )
            user = cursor.fetchone()
            conn.close()
            if user:
                update_password(user_id, new_pass)
                st.success("✅ Password updated!")
            else:
                st.error("❌ Current password is incorrect!")

st.write("---")
st.subheader("🗑️ Danger Zone")
with st.expander("⚠️ Delete All My Transactions"):
    st.warning("This will permanently delete all your transactions!")
    confirm_delete = st.text_input("Type DELETE to confirm")
    if st.button("🗑️ Delete All Transactions", type="primary"):
        if confirm_delete == "DELETE":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM transactions WHERE family_id = %s", (family_id,))
            conn.commit()
            conn.close()
            st.success("✅ All transactions deleted!")
        else:
            st.error("❌ Please type DELETE to confirm!")

st.write("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("💼 My Finances", use_container_width=True):
        st.switch_page("pages/finance.py")