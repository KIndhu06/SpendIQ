import pymysql

def get_connection():
    connection = pymysql.connect(
        host="mysql-48c3837-kindhunagamani-fce3.h.aivencloud.com",
        user="avnadmin",
        password="AVNS_hlTqrVhPxEdd4Xi4tiN",
        database="defaultdb",
        port=23940,
        ssl={"ssl_mode": "REQUIRED"}
    )
    return connection
```

Replace `YOUR_PASSWORD_HERE` with your actual Aiven password! ✅

---

## 🟢 Step 2: Update `requirements.txt`

Replace everything with:
```
streamlit
pandas
numpy
plotly
scikit-learn
pymysql
statsmodels
reportlab
sqlalchemy
openpyxl
pdfplumber
cryptography