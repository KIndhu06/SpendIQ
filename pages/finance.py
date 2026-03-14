import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.db import get_connection
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="My Finances",
    page_icon="💼",
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

family_id = st.session_state['user'][4]
user = st.session_state['user']

# ══════════════════════════════════════
# DATABASE FUNCTIONS
# ══════════════════════════════════════

def get_transactions(family_id):
    conn = get_connection()
    query = """
        SELECT date, description, amount, type, category
        FROM transactions WHERE family_id = %s
        ORDER BY date DESC
    """
    df = pd.read_sql(query, conn, params=(family_id,))
    conn.close()
    return df

def save_transactions(df, user_id, family_id):
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        desc = str(row['Description']).lower()
        if any(w in desc for w in ['salary','income','credit','deposit']):
            trans_type, category = 'income', 'Income'
        elif any(w in desc for w in ['food','restaurant','swiggy','zomato','grocery']):
            trans_type, category = 'expense', 'Food'
        elif any(w in desc for w in ['rent','house','maintenance']):
            trans_type, category = 'expense', 'Rent'
        elif any(w in desc for w in ['electricity','water','bill','utility','phone','netflix']):
            trans_type, category = 'expense', 'Utilities'
        elif any(w in desc for w in ['medical','hospital','pharmacy','medicine']):
            trans_type, category = 'expense', 'Medical'
        elif any(w in desc for w in ['school','college','education','fees']):
            trans_type, category = 'expense', 'Education'
        elif any(w in desc for w in ['shopping','amazon','flipkart','clothes','myntra']):
            trans_type, category = 'expense', 'Shopping'
        elif any(w in desc for w in ['travel','uber','ola','petrol','fuel']):
            trans_type, category = 'expense', 'Travel'
        else:
            trans_type, category = 'expense', 'Others'
        cursor.execute(
            """INSERT INTO transactions
            (user_id, family_id, date, description, amount, type, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, family_id, row['Date'], row['Description'],
             abs(float(row['Amount'])), trans_type, category)
        )
    conn.commit()
    conn.close()

def get_goals(family_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM goals WHERE family_id = %s",
        conn, params=(family_id,)
    )
    conn.close()
    return df

def save_goal(family_id, name, target, saved, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO goals
        (family_id, goal_name, target_amount, saved_amount, target_date)
        VALUES (%s, %s, %s, %s, %s)""",
        (family_id, name, target, saved, date)
    )
    conn.commit()
    conn.close()

def update_goal(goal_id, saved_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET saved_amount = %s WHERE id = %s",
        (saved_amount, goal_id)
    )
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = %s", (goal_id,))
    conn.commit()
    conn.close()

def get_bills(family_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM bills WHERE family_id = %s",
        conn, params=(family_id,)
    )
    conn.close()
    return df

def save_bill(family_id, name, amount, due_date, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO bills
        (family_id, bill_name, amount, due_date, category)
        VALUES (%s, %s, %s, %s, %s)""",
        (family_id, name, amount, due_date, category)
    )
    conn.commit()
    conn.close()

def delete_bill(bill_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bills WHERE id = %s", (bill_id,))
    conn.commit()
    conn.close()

def arima_predict(data, steps=3):
    try:
        model = ARIMA(data, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps)
        return np.array(forecast)
    except:
        try:
            model = ARIMA(data, order=(1, 0, 0))
            fitted = model.fit()
            forecast = fitted.forecast(steps=steps)
            return np.array(forecast)
        except:
            return None

# ══════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════

st.title("💼 My Finances")
st.write(f"Welcome, **{user[1]}**!")

col_home, col_report, col_profile = st.columns(3)
with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
with col_report:
    if st.button("📄 Download Report", use_container_width=True):
        st.switch_page("pages/report.py")
with col_profile:
    if st.button("👤 My Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

st.write("---")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📂 Upload",
    "📊 Dashboard",
    "💰 Budget",
    "🤖 Smart Insights",
    "🎯 Goals",
    "🔔 Bills",
    "💡 Calculator",
    "📅 Compare"
])

df = get_transactions(family_id)

# ══════════════════════════════════════
# TAB 1 — UPLOAD
# ══════════════════════════════════════
with tab1:
    st.subheader("📂 Upload Your Bank Statement")
    st.info("📌 Your CSV must have these columns: **Date, Description, Amount**")

    sample_data = """Date,Description,Amount
2026-02-01,Salary Credit,50000
2026-02-02,Swiggy Food Order,-450
2026-02-03,Electricity Bill,-1200
2026-02-04,Amazon Shopping,-2300
2026-02-05,Uber Travel,-350
2026-02-06,School Fees,-5000
2026-02-07,Medical Pharmacy,-800"""

    st.download_button(
        "📥 Download Sample CSV",
        data=sample_data,
        file_name="sample.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        upload_df = pd.read_csv(save_path)
        st.subheader("📋 Preview")
        st.dataframe(upload_df, use_container_width=True)
        if all(c in upload_df.columns for c in ['Date','Description','Amount']):
            if st.button("✅ Save Transactions"):
                save_transactions(upload_df, user[0], family_id)
                st.success("✅ Saved successfully!")
                st.balloons()
        else:
            st.error("❌ CSV must have: Date, Description, Amount")

# ══════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════
with tab2:
    st.subheader("📊 Your Financial Dashboard")
    if df.empty:
        st.warning("⚠️ No transactions yet! Go to Upload tab first.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        total_income = df[df['type']=='income']['amount'].sum()
        total_expense = df[df['type']=='expense']['amount'].sum()
        total_savings = total_income - total_expense

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Income", f"₹{total_income:,.2f}")
        with col2:
            st.metric("💸 Total Expenses", f"₹{total_expense:,.2f}")
        with col3:
            st.metric("🏦 Total Savings", f"₹{total_savings:,.2f}",
                delta="Saving ✅" if total_savings >= 0 else "Overspending ❌")

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            expense_df_dash = df[df['type']=='expense']
            if not expense_df_dash.empty:
                cat_df = expense_df_dash.groupby(
                    'category')['amount'].sum().reset_index()
                fig = px.pie(cat_df, values='amount',
                    names='category',
                    title='Where is Your Money Going?',
                    color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            summary = pd.DataFrame({
                'Type': ['Income','Expenses','Savings'],
                'Amount': [total_income, total_expense, total_savings]
            })
            fig2 = px.bar(summary, x='Type', y='Amount',
                title='Income vs Expenses vs Savings',
                color='Type',
                color_discrete_map={
                    'Income':'#2ecc71',
                    'Expenses':'#e74c3c',
                    'Savings':'#3498db'})
            st.plotly_chart(fig2, use_container_width=True)

        trend = df.groupby(['date','type'])['amount'].sum().reset_index()
        fig3 = px.line(trend, x='date', y='amount', color='type',
            title='Your Spending Trend Over Time',
            color_discrete_map={
                'income':'#2ecc71','expense':'#e74c3c'})
        st.plotly_chart(fig3, use_container_width=True)

        if not expense_df_dash.empty:
            cat_bar = expense_df_dash.groupby(
                'category')['amount'].sum().reset_index()
            fig4 = px.bar(cat_bar, x='category', y='amount',
                title='Expenses by Category',
                color='category',
                color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("📋 Recent Transactions")
        st.dataframe(df.head(15), use_container_width=True)

# ══════════════════════════════════════
# TAB 3 — BUDGET
# ══════════════════════════════════════
with tab3:
    st.subheader("💰 Budget Planner")
    from datetime import datetime as dt
    col1, col2 = st.columns(2)
    with col1:
        sel_year = st.selectbox(
            "Year", list(range(2023,2027)), index=3, key="by")
    with col2:
        sel_month = st.selectbox("Month",
            ["01","02","03","04","05",
             "06","07","08","09","10","11","12"],
            index=dt.now().month-1, key="bm")
    month_str = f"{sel_year}-{sel_month}"

    default_cats = ['Food','Rent','Utilities','Medical',
                    'Education','Shopping','Travel','Others']
    col1, col2 = st.columns(2)
    with col1:
        sel_cat = st.selectbox("Category", default_cats, key="bc")
    with col2:
        budget_amt = st.number_input("Spending Limit (₹)",
            min_value=0.0, value=1000.0, step=100.0, key="ba")

    if st.button("💾 Save Limit", use_container_width=True):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM budgets WHERE family_id=%s AND category=%s AND month=%s",
            (family_id, sel_cat, month_str))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                "UPDATE budgets SET budget_amount=%s WHERE family_id=%s AND category=%s AND month=%s",
                (budget_amt, family_id, sel_cat, month_str))
        else:
            cursor.execute(
                "INSERT INTO budgets (family_id,category,budget_amount,month) VALUES (%s,%s,%s,%s)",
                (family_id, sel_cat, budget_amt, month_str))
        conn.commit()
        conn.close()
        st.success(f"✅ Limit saved! ₹{budget_amt:,.2f} for {sel_cat}")
        st.rerun()

    st.write("---")
    conn = get_connection()
    budgets_df = pd.read_sql(
        "SELECT category, budget_amount FROM budgets WHERE family_id=%s AND month=%s",
        conn, params=(family_id, month_str))
    actual_df = pd.read_sql(
        """SELECT category, SUM(amount) as spent FROM transactions
        WHERE family_id=%s AND type='expense'
        AND DATE_FORMAT(date,'%%Y-%%m')=%s GROUP BY category""",
        conn, params=(family_id, month_str))
    conn.close()

    if not budgets_df.empty:
        merged = budgets_df.merge(actual_df, on='category', how='left')
        merged['spent'] = merged['spent'].fillna(0)
        merged['remaining'] = merged['budget_amount'] - merged['spent']
        merged['pct'] = (
            merged['spent']/merged['budget_amount']*100).round(1)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Total Limit",
                f"₹{merged['budget_amount'].sum():,.2f}")
        with col2:
            st.metric("💸 Total Spent",
                f"₹{merged['spent'].sum():,.2f}")
        with col3:
            rem = merged['remaining'].sum()
            st.metric("💰 Remaining", f"₹{rem:,.2f}",
                delta="Under Limit ✅" if rem >= 0 else "Over Limit ❌")

        st.write("---")
        for _, row in merged.iterrows():
            pct = min(float(row['pct']), 100)
            if row['pct'] > 100:
                st.error(
                    f"🔴 **{row['category']}** — "
                    f"Spent ₹{row['spent']:,.2f} / "
                    f"Limit ₹{row['budget_amount']:,.2f} — "
                    f"OVER by ₹{abs(row['remaining']):,.2f}!")
            elif row['pct'] > 80:
                st.warning(
                    f"🟡 **{row['category']}** — "
                    f"Spent ₹{row['spent']:,.2f} / "
                    f"Limit ₹{row['budget_amount']:,.2f} — "
                    f"{row['pct']}% used!")
            else:
                st.success(
                    f"🟢 **{row['category']}** — "
                    f"Spent ₹{row['spent']:,.2f} / "
                    f"Limit ₹{row['budget_amount']:,.2f} — "
                    f"{row['pct']}% used")
            st.progress(int(pct))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Your Limit', x=merged['category'],
            y=merged['budget_amount'], marker_color='#3498db'))
        fig.add_trace(go.Bar(
            name='Spent', x=merged['category'],
            y=merged['spent'], marker_color='#e74c3c'))
        fig.update_layout(
            barmode='group',
            title='Budget vs Actual Spending')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📌 No limits set for this month yet!")

# ══════════════════════════════════════
# TAB 4 — SMART INSIGHTS
# ══════════════════════════════════════
with tab4:
    st.subheader("🤖 Smart Financial Insights")
    if df.empty:
        st.warning("⚠️ No transactions yet! Go to Upload tab first.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        expense_df = df[df['type']=='expense'].copy()
        income_df = df[df['type']=='income'].copy()
        total_income = income_df['amount'].sum()
        total_expense = expense_df['amount'].sum()
        savings = total_income - total_expense
        savings_rate = (savings/total_income*100) if total_income > 0 else 0

        # ── Financial Health Score ──
        st.subheader("🏆 Your Financial Health Score")
        if savings_rate >= 40:
            score, grade, msg, color = 90, "A+", "Excellent! Keep it up!", "🟢"
        elif savings_rate >= 30:
            score, grade, msg, color = 75, "A", "Good! Small improvements needed.", "🟢"
        elif savings_rate >= 20:
            score, grade, msg, color = 60, "B", "Average. Try reducing expenses.", "🟡"
        elif savings_rate >= 10:
            score, grade, msg, color = 40, "C", "Poor. Immediate action needed!", "🟠"
        else:
            score, grade, msg, color = 20, "D", "Critical! Spending more than earning!", "🔴"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏆 Health Score", f"{score}/100")
        with col2:
            st.metric("📊 Grade", grade)
        with col3:
            st.metric("💰 Savings Rate", f"{savings_rate:.1f}%")
        st.info(f"{color} **{msg}**")
        st.progress(score)

        st.write("---")

        # ── Expense Predictions ──
        st.subheader("📈 Your Predicted Expenses for Next 3 Months")

        expense_df['month'] = expense_df['date'].dt.to_period('M')
        monthly = expense_df.groupby(
            'month')['amount'].sum().reset_index()
        monthly['month_num'] = range(1, len(monthly)+1)

        if len(monthly) >= 2:
            X = monthly[['month_num']].values
            y = monthly['amount'].values

            lr_model = LinearRegression()
            lr_model.fit(X, y)
            os.makedirs("models", exist_ok=True)
            with open("models/lr_model.pkl","wb") as f:
                pickle.dump(lr_model, f)

            dt_model = DecisionTreeRegressor(max_depth=3)
            dt_model.fit(X, y)
            with open("models/dt_model.pkl","wb") as f:
                pickle.dump(dt_model, f)

            future = np.array(
                [[len(monthly)+i] for i in range(1,4)])
            lr_preds = lr_model.predict(future)

            col1, col2, col3 = st.columns(3)
            months_labels = ["Next Month","Month After","3rd Month"]
            for i, col in enumerate([col1, col2, col3]):
                with col:
                    pred = lr_preds[i]
                    st.metric(
                        f"📅 {months_labels[i]}",
                        f"₹{pred:,.2f}",
                        delta="⚠️ May go up!" if pred > total_expense
                        else "✅ May go down!"
                    )

            avg_pred = np.mean(lr_preds)
            st.write("---")
            st.subheader("💡 What Should You Do?")
            if avg_pred > total_expense:
                diff = avg_pred - total_expense
                st.error(f"""
                ⚠️ **Your expenses are likely to increase by ₹{diff:,.2f} next month!**

                Here is what you should do right now:
                - ✂️ Reduce Shopping by ₹{diff*0.3:,.2f}
                - ✂️ Cut down Food expenses by ₹{diff*0.2:,.2f}
                - ✂️ Save on Travel by ₹{diff*0.2:,.2f}
                - 💰 Your savings target this month: ₹{total_income*0.3:,.2f}
                """)
            else:
                diff = total_expense - avg_pred
                st.success(f"""
                ✅ **Great news! Your expenses are likely to decrease by ₹{diff:,.2f}!**

                Here is how to use the extra money wisely:
                - 🏦 Transfer ₹{diff*0.5:,.2f} to your savings account
                - 📈 Invest ₹{diff*0.3:,.2f} in fixed deposits
                - 🎯 Keep ₹{diff*0.2:,.2f} as emergency fund
                """)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, len(monthly)+1)), y=y,
                mode='lines+markers',
                name='Your Past Expenses',
                line=dict(color='#e74c3c', width=2)))
            fig.add_trace(go.Scatter(
                x=list(range(len(monthly)+1, len(monthly)+4)),
                y=lr_preds, mode='lines+markers',
                name='Predicted Expenses',
                line=dict(color='#3498db', width=2, dash='dash')))
            fig.update_layout(
                title='Your Expense Trend & Prediction',
                xaxis_title='Month',
                yaxis_title='Amount (₹)',
                hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📌 Upload at least 2 months of data to see predictions!")

        st.write("---")

        # ── ARIMA Forecast ──
        st.subheader("🔮 Future Expense Forecast")
        st.write("Based on your spending history, here is what we predict:")

        if len(monthly) >= 2:
            expense_values = monthly['amount'].values
            arima_forecast = arima_predict(expense_values, steps=3)

            if arima_forecast is not None:
                arima_forecast = np.array(arima_forecast)
                last_month = pd.Period(
                    str(monthly['month'].iloc[-1]), freq='M')
                future_months = [
                    str(last_month+i) for i in range(1,4)]

                col1, col2, col3 = st.columns(3)
                for i, col in enumerate([col1, col2, col3]):
                    with col:
                        val = max(0, float(arima_forecast[i]))
                        st.metric(
                            label=f"📅 {future_months[i]}",
                            value=f"₹{val:,.2f}",
                            delta="⚠️ May increase" if val > total_expense
                            else "✅ May decrease"
                        )

                fig_arima = go.Figure()
                fig_arima.add_trace(go.Scatter(
                    x=monthly['month'].astype(str).tolist(),
                    y=expense_values,
                    mode='lines+markers',
                    name='Your Past Expenses',
                    line=dict(color='#e74c3c', width=3)))
                fig_arima.add_trace(go.Scatter(
                    x=future_months,
                    y=[max(0, float(v)) for v in arima_forecast],
                    mode='lines+markers',
                    name='Forecasted Expenses',
                    line=dict(color='#9b59b6', width=3, dash='dash'),
                    marker=dict(size=10, symbol='star')))
                fig_arima.update_layout(
                    title='Your Expense History & Future Forecast',
                    xaxis_title='Month',
                    yaxis_title='Amount (₹)',
                    hovermode='x unified',
                    plot_bgcolor='white')
                st.plotly_chart(fig_arima, use_container_width=True)
            else:
                st.info("📌 Need more data for forecast!")

        st.write("---")

        # ── Spending Pattern ──
        st.subheader("🔍 Your Spending Pattern")
        st.write("Here is how your spending is grouped:")

        if len(expense_df) >= 3:
            cat_summary = expense_df.groupby(
                'category')['amount'].agg(
                ['sum','mean','count']).reset_index()
            cat_summary.columns = [
                'category','total','average','frequency']

            scaler = StandardScaler()
            X_cluster = scaler.fit_transform(
                cat_summary[['total','average','frequency']])
            kmeans = KMeans(
                n_clusters=min(3, len(cat_summary)),
                random_state=42, n_init=10)
            cat_summary['cluster'] = kmeans.fit_predict(
                X_cluster).astype(str)

            with open("models/kmeans_model.pkl","wb") as f:
                pickle.dump(kmeans, f)

            cluster_names = {
                '0': '🔴 High Spending',
                '1': '🟡 Medium Spending',
                '2': '🟢 Low Spending'
            }
            cat_summary['Spending Level'] = cat_summary[
                'cluster'].map(
                lambda x: cluster_names.get(x, f"Group {x}"))

            fig_k = px.scatter(
                cat_summary, x='total', y='frequency',
                color='Spending Level', size='average',
                hover_data=['category'],
                title='Your Spending Groups',
                labels={
                    'total':'Total Spent (₹)',
                    'frequency':'No. of Transactions'},
                color_discrete_map={
                    '🔴 High Spending':'#e74c3c',
                    '🟡 Medium Spending':'#f39c12',
                    '🟢 Low Spending':'#2ecc71'})
            st.plotly_chart(fig_k, use_container_width=True)

            display_df = cat_summary[[
                'category','total','average',
                'frequency','Spending Level']].copy()
            display_df.columns = [
                'Category','Total Spent (₹)',
                'Avg per Transaction (₹)',
                'No. of Transactions','Spending Level']
            st.dataframe(display_df, use_container_width=True)

        st.write("---")

        # ── Unusual Transactions ──
        st.subheader("⚠️ Unusual Transactions Check")
        st.write("We automatically scan for any suspicious spending:")

        if len(expense_df) >= 5:
            scaler2 = StandardScaler()
            X_a = scaler2.fit_transform(expense_df[['amount']])
            iso = IsolationForest(contamination=0.1, random_state=42)
            expense_df = expense_df.copy()
            expense_df['unusual'] = iso.fit_predict(X_a) == -1
            unusual = expense_df[expense_df['unusual']]
            normal = expense_df[~expense_df['unusual']]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Normal Transactions", len(normal))
            with col2:
                st.metric("⚠️ Unusual Transactions", len(unusual))

            fig_a = go.Figure()
            fig_a.add_trace(go.Scatter(
                x=normal['date'], y=normal['amount'],
                mode='markers', name='✅ Normal',
                marker=dict(color='#2ecc71', size=8)))
            fig_a.add_trace(go.Scatter(
                x=unusual['date'], y=unusual['amount'],
                mode='markers', name='⚠️ Unusual',
                marker=dict(
                    color='#e74c3c', size=14, symbol='star')))
            fig_a.update_layout(
                title='Your Transaction Activity',
                xaxis_title='Date',
                yaxis_title='Amount (₹)')
            st.plotly_chart(fig_a, use_container_width=True)

            if len(unusual) > 0:
                st.warning(
                    "⚠️ Please review these unusual transactions:")
                st.dataframe(
                    unusual[['date','description',
                              'amount','category']].rename(
                        columns={
                            'date':'Date',
                            'description':'Description',
                            'amount':'Amount (₹)',
                            'category':'Category'}),
                    use_container_width=True)
            else:
                st.success("✅ No unusual transactions found!")

        st.write("---")

        # ── Smart Spending Alerts ──
        st.subheader("🔔 Smart Spending Alerts")
        cat_totals = expense_df.groupby(
            'category')['amount'].sum().reset_index()
        for _, row in cat_totals.iterrows():
            pct = (row['amount']/total_income*100) \
                if total_income > 0 else 0
            if pct > 25:
                st.error(
                    f"🔴 **{row['category']}**: "
                    f"₹{row['amount']:,.2f} ({pct:.1f}% of income) "
                    f"— Too high! Reduce now.")
            elif pct > 15:
                st.warning(
                    f"🟡 **{row['category']}**: "
                    f"₹{row['amount']:,.2f} ({pct:.1f}% of income) "
                    f"— Getting high!")
            else:
                st.success(
                    f"🟢 **{row['category']}**: "
                    f"₹{row['amount']:,.2f} ({pct:.1f}% of income) "
                    f"— Good!")

        st.write("---")

        # ── Recommended Budget ──
        st.subheader("💡 Recommended Budget for You")
        st.write(
            f"Based on your income of **₹{total_income:,.2f}**, "
            f"here is how you should spend:")
        budget_rules = {
            "🏠 Rent": 0.30,
            "🍔 Food": 0.20,
            "📚 Education": 0.10,
            "🚗 Travel": 0.10,
            "🛒 Shopping": 0.10,
            "💊 Medical": 0.05,
            "💡 Utilities": 0.05,
            "🏦 Savings": 0.10,
        }
        rec_data = []
        for cat, pct in budget_rules.items():
            rec_data.append({
                'Category': cat,
                'Recommended %': f"{pct*100:.0f}%",
                'Use only this much': f"₹{total_income*pct:,.2f}"
            })
        st.dataframe(
            pd.DataFrame(rec_data), use_container_width=True)

# ══════════════════════════════════════
# TAB 5 — GOALS
# ══════════════════════════════════════
with tab5:
    st.subheader("🎯 Financial Goals")
    st.info("Set your savings goals and track your progress!")

    with st.expander("➕ Add New Goal"):
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input(
                "Goal Name (e.g. Vacation, New Phone)")
            target_amount = st.number_input(
                "Target Amount (₹)",
                min_value=0.0, value=10000.0, step=500.0)
        with col2:
            saved_amount = st.number_input(
                "Already Saved (₹)",
                min_value=0.0, value=0.0, step=500.0)
            target_date = st.date_input("Target Date")
        if st.button("🎯 Add Goal", use_container_width=True):
            if goal_name and target_amount > 0:
                save_goal(family_id, goal_name,
                         target_amount, saved_amount, target_date)
                st.success(f"✅ Goal '{goal_name}' added!")
                st.rerun()

    goals_df = get_goals(family_id)
    if goals_df.empty:
        st.info("📌 No goals yet! Add your first goal above.")
    else:
        for _, goal in goals_df.iterrows():
            pct = min(
                (goal['saved_amount']/goal['target_amount']*100)
                if goal['target_amount'] > 0 else 0, 100)
            remaining = goal['target_amount'] - goal['saved_amount']
            with st.container():
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"### 🎯 {goal['goal_name']}")
                    st.write(
                        f"Target: **₹{goal['target_amount']:,.2f}** | "
                        f"Saved: **₹{goal['saved_amount']:,.2f}** | "
                        f"Remaining: **₹{remaining:,.2f}**")
                    st.write(
                        f"📅 Target Date: **{goal['target_date']}**")
                    if pct >= 100:
                        st.success("🎉 Goal Achieved!")
                    elif pct >= 75:
                        st.info(f"Almost there! {pct:.1f}% complete")
                    else:
                        st.warning(
                            f"Keep going! {pct:.1f}% complete")
                    st.progress(int(pct))
                with col2:
                    new_saved = st.number_input(
                        "Update Saved (₹)",
                        min_value=0.0,
                        value=float(goal['saved_amount']),
                        key=f"g_{goal['id']}")
                    if st.button("💾 Update",
                                 key=f"ug_{goal['id']}"):
                        update_goal(goal['id'], new_saved)
                        st.success("✅ Updated!")
                        st.rerun()
                    if st.button("🗑️ Delete",
                                 key=f"dg_{goal['id']}"):
                        delete_goal(goal['id'])
                        st.rerun()
            st.write("---")

# ══════════════════════════════════════
# TAB 6 — BILLS
# ══════════════════════════════════════
with tab6:
    st.subheader("🔔 Bill Reminders")
    st.info("Add your monthly bills and never miss a payment!")

    with st.expander("➕ Add New Bill"):
        col1, col2 = st.columns(2)
        with col1:
            bill_name = st.text_input(
                "Bill Name (e.g. Electricity, Rent)")
            bill_amount = st.number_input(
                "Amount (₹)",
                min_value=0.0, value=500.0, step=100.0)
        with col2:
            bill_due = st.number_input(
                "Due Date (day of month)",
                min_value=1, max_value=31, value=1)
            bill_cat = st.selectbox("Category",
                ['Utilities','Rent','Education','Medical','Others'])
        if st.button("🔔 Add Bill", use_container_width=True):
            if bill_name and bill_amount > 0:
                save_bill(family_id, bill_name,
                         bill_amount, bill_due, bill_cat)
                st.success(f"✅ Bill '{bill_name}' added!")
                st.rerun()

    from datetime import datetime as dt2
    today = dt2.now().day
    bills_df = get_bills(family_id)

    if bills_df.empty:
        st.info("📌 No bills added yet!")
    else:
        overdue = bills_df[bills_df['due_date'] < today]
        due_soon = bills_df[
            (bills_df['due_date'] >= today) &
            (bills_df['due_date'] <= today+5)]
        upcoming = bills_df[bills_df['due_date'] > today+5]

        if not overdue.empty:
            st.error(f"🔴 {len(overdue)} Overdue Bills!")
            for _, bill in overdue.iterrows():
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(
                        f"🔴 **{bill['bill_name']}** — "
                        f"₹{bill['amount']:,.2f} — "
                        f"Was due day {bill['due_date']}")
                with col2:
                    if st.button("🗑️", key=f"db_{bill['id']}"):
                        delete_bill(bill['id'])
                        st.rerun()

        if not due_soon.empty:
            st.warning(f"🟡 {len(due_soon)} Bills Due Soon!")
            for _, bill in due_soon.iterrows():
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(
                        f"🟡 **{bill['bill_name']}** — "
                        f"₹{bill['amount']:,.2f} — "
                        f"Due in {bill['due_date']-today} days!")
                with col2:
                    if st.button("🗑️", key=f"ds_{bill['id']}"):
                        delete_bill(bill['id'])
                        st.rerun()

        if not upcoming.empty:
            st.success(f"🟢 {len(upcoming)} Upcoming Bills")
            for _, bill in upcoming.iterrows():
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(
                        f"🟢 **{bill['bill_name']}** — "
                        f"₹{bill['amount']:,.2f} — "
                        f"Due in {bill['due_date']-today} days")
                with col2:
                    if st.button("🗑️", key=f"du_{bill['id']}"):
                        delete_bill(bill['id'])
                        st.rerun()

        st.write("---")
        st.metric("💸 Total Monthly Bills",
                  f"₹{bills_df['amount'].sum():,.2f}")

# ══════════════════════════════════════
# TAB 7 — CALCULATOR
# ══════════════════════════════════════
with tab7:
    st.subheader("💡 Savings Calculator")
    st.info("Find out how long it takes to reach your savings goal!")

    col1, col2 = st.columns(2)
    with col1:
        calc_income = st.number_input(
            "Monthly Income (₹)",
            min_value=0.0, value=50000.0, step=1000.0)
        calc_expense = st.number_input(
            "Monthly Expenses (₹)",
            min_value=0.0, value=30000.0, step=1000.0)
    with col2:
        calc_goal = st.number_input(
            "Savings Goal (₹)",
            min_value=0.0, value=100000.0, step=5000.0)
        calc_existing = st.number_input(
            "Already Saved (₹)",
            min_value=0.0, value=0.0, step=1000.0)

    if st.button("💡 Calculate", use_container_width=True):
        monthly_savings = calc_income - calc_expense
        remaining_goal = calc_goal - calc_existing

        if monthly_savings <= 0:
            st.error(
                "❌ You are spending more than earning! "
                "Reduce expenses first.")
        else:
            months_needed = remaining_goal / monthly_savings
            years = int(months_needed // 12)
            months = int(months_needed % 12)
            time_str = (f"{years}y {months}m"
                       if years > 0 else f"{months} months")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Monthly Savings",
                          f"₹{monthly_savings:,.2f}")
            with col2:
                st.metric("🎯 Amount Remaining",
                          f"₹{remaining_goal:,.2f}")
            with col3:
                st.metric("⏳ Time to Goal", time_str)

            savings_rate = (monthly_savings/calc_income*100)
            if savings_rate >= 30:
                st.success(
                    f"✅ Great savings rate of {savings_rate:.1f}%! "
                    f"Goal in {time_str}!")
            else:
                st.warning(
                    f"🟡 Savings rate is {savings_rate:.1f}%. "
                    f"Save more to reach goal faster!")

            st.write("---")
            st.subheader("💡 Tips to Reach Goal Faster")
            tips_data = []
            for extra_pct in [10, 20, 30]:
                extra = calc_income * extra_pct / 100
                new_savings = monthly_savings + extra
                new_months = remaining_goal / new_savings
                new_y = int(new_months // 12)
                new_m = int(new_months % 12)
                time_saved = int(months_needed - new_months)
                tips_data.append({
                    'Save Extra': f"₹{extra:,.2f}/month",
                    'New Monthly Savings': f"₹{new_savings:,.2f}",
                    'Time to Goal': (f"{new_y}y {new_m}m"
                                    if new_y > 0
                                    else f"{new_m} months"),
                    'Months Saved': f"{time_saved} months faster!"
                })
            st.dataframe(
                pd.DataFrame(tips_data),
                use_container_width=True)

            months_list = list(range(1, int(months_needed)+2))
            savings_progress = [
                min(calc_existing + monthly_savings*m, calc_goal)
                for m in months_list]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months_list, y=savings_progress,
                mode='lines+markers',
                name='Savings Progress',
                line=dict(color='#2ecc71', width=3)))
            fig.add_hline(
                y=calc_goal, line_dash="dash",
                line_color="#e74c3c",
                annotation_text="🎯 Your Goal")
            fig.update_layout(
                title='Your Savings Journey',
                xaxis_title='Month Number',
                yaxis_title='Savings (₹)')
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════
# TAB 8 — COMPARE
# ══════════════════════════════════════
with tab8:
    st.subheader("📅 Month vs Month Comparison")
    st.info("Compare your spending between any two months!")

    if df.empty:
        st.warning("⚠️ No transactions yet!")
    else:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        available_months = sorted(
            df['month'].unique().tolist(), reverse=True)

        if len(available_months) < 2:
            st.warning(
                "⚠️ Need at least 2 months of data to compare!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                month1 = st.selectbox(
                    "First Month", available_months, index=0)
            with col2:
                month2 = st.selectbox(
                    "Second Month", available_months, index=1)

            if st.button("📊 Compare Now",
                        use_container_width=True):
                df1 = df[df['month']==month1]
                df2 = df[df['month']==month2]

                inc1 = df1[df1['type']=='income']['amount'].sum()
                exp1 = df1[df1['type']=='expense']['amount'].sum()
                sav1 = inc1 - exp1

                inc2 = df2[df2['type']=='income']['amount'].sum()
                exp2 = df2[df2['type']=='expense']['amount'].sum()
                sav2 = inc2 - exp2

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Income", f"₹{inc1:,.2f}",
                        delta=f"₹{inc1-inc2:,.2f} vs {month2}")
                with col2:
                    st.metric("💸 Expenses", f"₹{exp1:,.2f}",
                        delta=f"₹{exp1-exp2:,.2f} vs {month2}",
                        delta_color="inverse")
                with col3:
                    st.metric("🏦 Savings", f"₹{sav1:,.2f}",
                        delta=f"₹{sav1-sav2:,.2f} vs {month2}")

                st.write("---")
                if exp1 > exp2:
                    diff = exp1 - exp2
                    st.error(
                        f"⚠️ You spent **₹{diff:,.2f} MORE** "
                        f"in {month1} vs {month2}!")
                else:
                    diff = exp2 - exp1
                    st.success(
                        f"✅ You spent **₹{diff:,.2f} LESS** "
                        f"in {month1} vs {month2}!")

                comp_df = pd.DataFrame({
                    'Month': [month1,month1,month1,
                              month2,month2,month2],
                    'Type': ['Income','Expenses','Savings',
                             'Income','Expenses','Savings'],
                    'Amount': [inc1,exp1,sav1,inc2,exp2,sav2]
                })
                fig = px.bar(comp_df, x='Type', y='Amount',
                    color='Month', barmode='group',
                    title=f'Comparison: {month1} vs {month2}',
                    color_discrete_sequence=['#3498db','#e74c3c'])
                st.plotly_chart(fig, use_container_width=True)

                cat1 = df1[df1['type']=='expense'].groupby(
                    'category')['amount'].sum()
                cat2 = df2[df2['type']=='expense'].groupby(
                    'category')['amount'].sum()
                cat_comp = pd.DataFrame(
                    {month1:cat1, month2:cat2}
                ).fillna(0).reset_index()
                cat_comp.columns = ['Category', month1, month2]
                cat_comp['Difference'] = (
                    cat_comp[month1] - cat_comp[month2])
                cat_comp['Status'] = cat_comp['Difference'].apply(
                    lambda x: '⬆️ Increased'
                    if x > 0 else '⬇️ Decreased')

                fig2 = px.bar(
                    cat_comp.melt(
                        id_vars='Category',
                        value_vars=[month1,month2]),
                    x='Category', y='value',
                    color='variable', barmode='group',
                    title='Category Wise Comparison',
                    labels={
                        'value':'Amount (₹)',
                        'variable':'Month'})
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(cat_comp, use_container_width=True)

                most_inc = cat_comp.nlargest(1, 'Difference')
                if (not most_inc.empty and
                        most_inc.iloc[0]['Difference'] > 0):
                    st.warning(
                        f"⚠️ **{most_inc.iloc[0]['Category']}** "
                        f"increased most by "
                        f"₹{most_inc.iloc[0]['Difference']:,.2f} "
                        f"in {month1}. Reduce next month!")