import pymysql

conn = pymysql.connect(
    host="mysql-48c3837-kindhunagamani-fce3.h.aivencloud.com",
    user="avnadmin",
    password="AVNS_hlTqrVhPxEdd4Xi4tiN",
    database="defaultdb",
    port=23940,
    ssl={"ssl_mode": "REQUIRED"}
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    family_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
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
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    category VARCHAR(100),
    budget_amount DECIMAL(10,2),
    month VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    goal_name VARCHAR(100),
    target_amount DECIMAL(10,2),
    saved_amount DECIMAL(10,2) DEFAULT 0,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id VARCHAR(50),
    bill_name VARCHAR(100),
    amount DECIMAL(10,2),
    due_date INT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ All tables created successfully!")