import pymysql
import ssl

def get_connection():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connection = pymysql.connect(
        host="mysql-48c3837-kindhunagamani-fce3.h.aivencloud.com",
        user="avnadmin",
        password="AVNS_hlTqrVhPxEdd4Xi4tiN",
        database="defaultdb",
        port=23940,
        ssl=ssl_context
    )
    return connection
