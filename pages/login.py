import streamlit as st
from utils.db import get_connection
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(
    page_title="SpendIQ",
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
    </style>
""", unsafe_allow_html=True)

SENDER_EMAIL = "kondapaturimani@gmail.com"
APP_PASSWORD = "evey kuei rqpb qdtu"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_welcome_email(username, receiver_email):
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white;
                    border-radius: 10px; overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #2C3E50, #3498DB);
                        padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">💰 SpendIQ </h1>
                <p style="color: #BDC3C7; margin: 5px 0;">Welcome to the Family!</p>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #2C3E50;">Hello {username}! 👋</h2>
                <p style="color: #7F8C8D;">Your account has been created successfully!</p>
                <ul style="color: #2C3E50;">
                    <li>📂 Upload your bank statements</li>
                    <li>📊 View your financial dashboard</li>
                    <li>🤖 Get smart financial insights</li>
                    <li>💰 Plan your family budget</li>
                    <li>🎯 Set and track financial goals</li>
                    <li>🔔 Never miss a bill payment</li>
                </ul>
            </div>
            <div style="background: #2C3E50; padding: 20px; text-align: center;">
                <p style="color: #BDC3C7; margin: 0; font-size: 12px;">
                    Family Finance Tracker | Secure & Private
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎉 Welcome to SpendIQ !"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

def register_user(username, email, password, family_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password, family_id) VALUES (%s, %s, %s, %s)",
        (username, email, hash_password(password), family_id)
    )
    conn.commit()
    conn.close()
    send_welcome_email(username, email)

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user

st.markdown("""
    <div style="text-align:center; padding: 20px;">
        <h1>💰 Family Finance Tracker</h1>
        <p style="color: #7F8C8D;">Manage your family finances smartly!</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

with tab1:
    st.subheader("🔐 Login to Your Account")
    email = st.text_input("Email Address", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login", use_container_width=True):
        if email and password:
            user = login_user(email, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user'] = user
                st.success(f"Welcome back, {user[1]}! ✅")
                st.switch_page("app.py")
            else:
                st.error("Invalid email or password ❌")
        else:
            st.error("Please fill all fields!")

with tab2:
    st.subheader("📝 Create New Account")
    username = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email Address", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_pass")
    family_id = st.text_input("Family ID (e.g. FAM001)", key="reg_fam")
    st.caption("💡 All family members should use the same Family ID")
    if st.button("Register", use_container_width=True):
        if username and email and password and family_id:
            try:
                register_user(username, email, password, family_id)
                st.success("Account created successfully! ✅ Please login.")
            except:
                st.error("Email already exists! ❌")
        else:
            st.error("Please fill all fields! ❌")