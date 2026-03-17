import pymysql

def get_connection():
    connection = pymysql.connect(
        host="mysql-48c3837-kindhunagamani-fce3.h.aivencloud.com",
        user="avnadmin",
        password="YOUR_PASSWORD_HERE",
        database="defaultdb",
        port=23940,
        ssl={"ssl_mode": "REQUIRED"}
    )
    return connection