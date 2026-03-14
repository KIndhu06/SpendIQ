import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db import get_connection
from datetime import datetime

if 'logged_in' not in st.session_state:
    st.switch_page("pages/login.py")

def get_categories(family_id):
    default_categories = [
        'Food', 'Rent', 'Utilities', 'Medical',
        'Education', 'Shopping', 'Travel', 'Others'
    ]
    conn = get_connection()
    query = """
        SELECT DISTINCT category
        FROM transactions
        WHERE family_id = %s AND type = 'expense'
    """
    df = pd.read_sql(query, conn, params=(family_id,))
    conn.close()
    extra = df['category'].tolist()
    return sorted(list(set(default_categories + extra)))

def save_budget(family_id, category, amount, month):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id FROM budgets
            WHERE family_id = %s AND category = %s AND month = %s""",
            (family_id, category, month)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """UPDATE budgets SET budget_amount = %s
                WHERE family_id = %s AND category = %s AND month = %s""",
                (amount, family_id, category, month)
            )
        else:
            cursor.execute(
                """INSERT INTO budgets (family_id, category, budget_amount, month)
                VALUES (%s, %s, %s, %s)""",
                (family_id, category, amount, month)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving budget: {e}")
        return False

def get_budgets(family_id, month):
    try:
        conn = get_connection()
        query = """
            SELECT category, budget_amount
            FROM budgets
            WHERE family_id = %s AND month = %s
        """
        df = pd.read_sql(query, conn, params=(family_id, month))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def get_actual_spending(family_id, month):
    try:
        conn = get_connection()
        query = """
            SELECT category, SUM(amount) as spent
            FROM transactions
            WHERE family_id = %s
            AND type = 'expense'
            AND DATE_FORMAT(date, '%%Y-%%m') = %s
            GROUP BY category
        """
        df = pd.read_sql(query, conn, params=(family_id, month))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

st.title("💰 Budget Planner")
st.write(f"Welcome, **{st.session_state['user'][1]}**!")

st.info("""
📋 **How to use:**
Set a spending limit for each category every month.
We will show you how much you have spent vs your limit
and alert you when you are close to or over budget!
""")

family_id = st.session_state['user'][4]

st.write("---")
st.subheader("📅 Select Month to Plan")
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Year", list(range(2023, 2027)), index=3)
with col2:
    selected_month = st.selectbox(
        "Month",
        ["01","02","03","04","05","06","07","08","09","10","11","12"],
        index=datetime.now().month - 1
    )

month_str = f"{selected_year}-{selected_month}"
st.info(f"📅 Planning budget for: **{month_str}**")

st.write("---")
st.subheader("⚙️ Set Your Spending Limit")

categories = get_categories(family_id)
categories.append("Custom Category")

col1, col2 = st.columns(2)
with col1:
    selected_category = st.selectbox("Select Category", categories)
    if selected_category == "Custom Category":
        selected_category = st.text_input("Enter Category Name")
with col2:
    budget_amount = st.number_input(
        "Spending Limit (₹)",
        min_value=0.0, value=1000.0, step=100.0
    )

if st.button("💾 Save Spending Limit", use_container_width=True):
    if selected_category and budget_amount > 0:
        success = save_budget(family_id, selected_category, budget_amount, month_str)
        if success:
            st.success(f"✅ Spending limit saved! You can spend up to ₹{budget_amount:,.2f} on {selected_category}")
            st.rerun()
    else:
        st.error("❌ Please select a category and enter an amount!")

st.write("---")
st.subheader(f"📊 How Are You Doing This Month? — {month_str}")

budgets_df = get_budgets(family_id, month_str)
actual_df = get_actual_spending(family_id, month_str)

if budgets_df.empty:
    st.info("📌 No spending limits set for this month yet. Set your limits above!")
else:
    merged_df = budgets_df.merge(actual_df, on='category', how='left')
    merged_df['spent'] = merged_df['spent'].fillna(0)
    merged_df['remaining'] = merged_df['budget_amount'] - merged_df['spent']
    merged_df['percentage'] = (
        merged_df['spent'] / merged_df['budget_amount'] * 100
    ).round(1)

    total_budget = merged_df['budget_amount'].sum()
    total_spent = merged_df['spent'].sum()
    total_remaining = total_budget - total_spent

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Total Spending Limit", f"₹{total_budget:,.2f}")
    with col2:
        st.metric("💸 Total Spent So Far", f"₹{total_spent:,.2f}")
    with col3:
        st.metric(
            "💰 Remaining to Spend",
            f"₹{total_remaining:,.2f}",
            delta=f"{'Under Limit ✅' if total_remaining >= 0 else 'Over Limit ❌'}"
        )

    st.write("---")
    st.subheader("📈 Spending Progress")
    for _, row in merged_df.iterrows():
        pct = min(float(row['percentage']), 100)
        if row['percentage'] > 100:
            st.error(
                f"🔴 **{row['category']}** — "
                f"You spent ₹{row['spent']:,.2f} out of ₹{row['budget_amount']:,.2f} limit. "
                f"**OVER by ₹{abs(row['remaining']):,.2f}! Please stop spending on this!**"
            )
        elif row['percentage'] > 80:
            st.warning(
                f"🟡 **{row['category']}** — "
                f"You spent ₹{row['spent']:,.2f} out of ₹{row['budget_amount']:,.2f} limit. "
                f"⚠️ {row['percentage']}% used. Be careful!"
            )
        else:
            st.success(
                f"🟢 **{row['category']}** — "
                f"You spent ₹{row['spent']:,.2f} out of ₹{row['budget_amount']:,.2f} limit. "
                f"({row['percentage']}% used. Good job!)"
            )
        st.progress(int(pct))

    st.write("---")
    st.subheader("📊 Budget vs Actual Chart")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Your Limit', x=merged_df['category'],
        y=merged_df['budget_amount'], marker_color='#3498db'
    ))
    fig.add_trace(go.Bar(
        name='Amount Spent', x=merged_df['category'],
        y=merged_df['spent'], marker_color='#e74c3c'
    ))
    fig.update_layout(
        barmode='group',
        title='Your Spending Limit vs Actual Spending',
        xaxis_title='Category',
        yaxis_title='Amount (₹)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    if total_spent > 0:
        st.subheader("🥧 Where is Your Money Going?")
        fig_pie = px.pie(
            merged_df, values='spent', names='category',
            title='Your Spending Distribution This Month',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.write("---")
    st.subheader("📋 Full Budget Summary")
    display_df = merged_df.copy()
    display_df.columns = [
        'Category', 'Your Limit (₹)',
        'Amount Spent (₹)', 'Remaining (₹)', 'Used %'
    ]
    st.dataframe(display_df, use_container_width=True)

st.write("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")