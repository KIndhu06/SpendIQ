import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.image(
            "https://img.icons8.com/emoji/96/money-bag-emoji.png",
            width=80
        )
        st.title("💰 Finance Tracker")
        if 'user' in st.session_state:
            st.write(f"👤 **{st.session_state['user'][1]}**")
            st.write(f"👨‍👩‍👧 Family ID: **{st.session_state['user'][4]}**")
        st.write("---")

        st.subheader("📌 Menu")
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
        if st.button("📂 Upload Statement", use_container_width=True):
            st.switch_page("pages/upload.py")
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
        if st.button("💰 Budget Planner", use_container_width=True):
            st.switch_page("pages/budget.py")
        if st.button("🤖 Smart Insights", use_container_width=True):
            st.switch_page("pages/predictions.py")
        if st.button("📈 Expense Forecast", use_container_width=True):
            st.switch_page("pages/arima.py")
        if st.button("🔍 Unusual Transactions", use_container_width=True):
            st.switch_page("pages/anomaly.py")
        if st.button("📄 Download Report", use_container_width=True):
            st.switch_page("pages/report.py")
        if st.button("📧 Email Alerts", use_container_width=True):
            st.switch_page("pages/email_alerts.py")
        if st.button("👤 My Profile", use_container_width=True):
            st.switch_page("pages/profile.py")
        st.write("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("pages/login.py")