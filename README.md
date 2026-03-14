💰 SpendiQ — Smart Family Finance Management System
> Smart Spending Starts Here
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
---
📋 Table of Contents
About the Project
Features
Technology Stack
Machine Learning Models
Project Structure
Installation
Database Setup
Running the App
Deployment
Screenshots
Contributors
---
📖 About the Project
SpendiQ is a web-based intelligent family finance management system built using Python and Streamlit. It helps families track their income and expenses, analyze spending patterns, predict future expenses using machine learning, set financial goals, manage bill reminders and generate professional PDF reports.
The system is designed to be simple, intelligent and user-friendly so that every family member can use it without any financial or technical expertise.
---
✨ Features
🔐 Secure Login & Registration with SHA-256 password encryption
📂 Bank Statement Upload with automatic transaction categorization
📊 Interactive Dashboard with Plotly charts and visualizations
🤖 ML-Powered Predictions using 5 different algorithms
💰 Budget Planner with real-time spending alerts
🎯 Financial Goal Tracking with progress visualization
🔔 Bill Reminder System with urgency classification
💡 Savings Calculator with goal timeline chart
📅 Month vs Month Comparison for expense analysis
📄 PDF Report Generation with professional formatting
📧 Automated Welcome Email on registration
👤 Profile & Security Management
---
🛠️ Technology Stack
Component	Technology
Frontend	Streamlit
Backend	Python 3.12
Database	MySQL
Data Processing	Pandas, NumPy
Visualization	Plotly
Machine Learning	Scikit-learn, Statsmodels
Security	SHA-256 Hashing
Report Generation	ReportLab
Email	Python SMTP
Model Storage	Pickle
Development Tool	VS Code
---
🤖 Machine Learning Models
Algorithm	Purpose
Linear Regression	Predict future monthly expenses
Decision Tree Regression	Non-linear spending pattern prediction
ARIMA	Time series expense forecasting
K-Means Clustering	Spending behavior pattern analysis
Isolation Forest	Unusual transaction detection
---
📁 Project Structure
```
spendiq/
│
├── .streamlit/
│     └── config.toml          ← Theme configuration
│
├── pages/
│     ├── login.py             ← Login & Register page
│     ├── finance.py           ← Main finance page with tabs
│     ├── report.py            ← PDF report generation
│     └── profile.py           ← User profile & security
│
├── utils/
│     └── db.py                ← Database connection
│
├── data/                      ← Uploaded CSV files stored here
│
├── models/                    ← Trained ML models stored here
│     ├── lr_model.pkl
│     ├── dt_model.pkl
│     └── kmeans_model.pkl
│
├── app.py                     ← Main entry point
├── requirements.txt           ← Python dependencies
└── README.md                  ← Project documentation
```
---
⚙️ Installation
Prerequisites
Python 3.12 or higher
MySQL (XAMPP or online)
VS Code or any editor
Git
Step 1: Clone the Repository
```bash
git clone https://github.com/your_username/spendiq.git
cd spendiq
```
Step 2: Install Dependencies
```bash
pip install streamlit pandas numpy matplotlib plotly scikit-learn mysql-connector-python pymysql pdfplumber openpyxl statsmodels reportlab sqlalchemy
```
---
🗄️ Database Setup
Create MySQL Database and Tables
Run the following SQL in your MySQL (phpMyAdmin or MySQL Workbench):
```sql
CREATE DATABASE family_finance;
USE family_finance;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    family_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    family_id VARCHAR(50),
    date DATE,
    description VARCHAR(255),
    amount DECIMAL(10,2),
    type ENUM('income', 'expense'),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    category VARCHAR(100),
    budget_amount DECIMAL(10,2),
    month VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    goal_name VARCHAR(100),
    target_amount DECIMAL(10,2),
    saved_amount DECIMAL(10,2) DEFAULT 0,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    bill_name VARCHAR(100),
    amount DECIMAL(10,2),
    due_date INT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE family_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    username VARCHAR(100),
    email VARCHAR(100),
    role ENUM('admin', 'member') DEFAULT 'member',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
Update Database Connection
Open `utils/db.py` and update with your database credentials:
```python
import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",        # or your online host
        user="root",             # your username
        password="",             # your password
        database="family_finance",
        port=3306
    )
    return connection
```
---
▶️ Running the App
```bash
python -m streamlit run app.py
```
Open your browser and go to:
```
http://localhost:8501
```
---
🚀 Deployment
SpendiQ is deployed on Streamlit Cloud with a free online MySQL database.
Steps to Deploy:
1. Push to GitHub:
```bash
git add .
git commit -m "Deploy SpendiQ"
git push origin main
```
2. Deploy on Streamlit Cloud:
Go to `https://streamlit.io/cloud`
Sign in with GitHub
Click New App
Select your repository
Set main file as `app.py`
Click Deploy
Live URL:
```
https://spendiq.streamlit.app
```
---
📊 CSV Format for Bank Statement Upload
Your CSV file must have exactly these three columns:
```
Date,Description,Amount
2026-02-01,Salary Credit,50000
2026-02-02,Swiggy Food Order,-450
2026-02-03,Electricity Bill,-1200
2026-02-04,Amazon Shopping,-2300
```
Date format: YYYY-MM-DD
Amount positive for income, negative for expense
---
🎯 How to Use SpendiQ
Register with your name, email, password and Family ID
Login to your account
Upload your bank statement CSV file
View Dashboard to see your financial summary
Check Smart Insights for ML predictions and alerts
Set Budget limits for each spending category
Add Goals and track your savings progress
Add Bills to never miss a payment
Use Calculator to plan your savings journey
Compare months to track improvement
Download Report as a PDF for records
---
👥 User Roles
SpendiQ supports family-based access where multiple members can share financial data:
All members with the same Family ID share transactions
Each member has their own login credentials
Any member can upload statements and view shared data
---
🔐 Security Features
Passwords encrypted using SHA-256 hashing
No plain text passwords stored in database
Session-based authentication using Streamlit session state
Confirmation required for sensitive operations like data deletion
---
📦 Requirements
```
streamlit
pandas
numpy
matplotlib
plotly
scikit-learn
mysql-connector-python
pymysql
pdfplumber
openpyxl
statsmodels
reportlab
sqlalchemy
```
---
🐛 Common Issues & Solutions
Issue	Solution
Database connection error	Check credentials in db.py
Module not found	Run pip install -r requirements.txt
CSV upload error	Make sure CSV has Date, Description, Amount columns
PDF not generating	Install reportlab using pip install reportlab
Predictions not showing	Upload at least 2 months of data
---
🎓 Project Information
Project Title: SpendiQ — Smart Family Finance Management System
Technology: Python, Streamlit, MySQL, Machine Learning
Type: BTech Final Year Project
Domain: Finance Technology (FinTech)
ML Algorithms: Linear Regression, Decision Tree, ARIMA, K-Means, Isolation Forest
---
📧 Contact
For any queries or issues please contact through GitHub issues.
---
📄 License
This project is licensed under the MIT License.
---
<div align="center">
  <b>💰 SpendiQ — Smart Spending Starts Here</b>
</div>
