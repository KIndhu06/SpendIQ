import pymysql

def get_connection():
    connection = pymysql.connect(
        host="mysql-48c3837-kindhunagamani-fce3.h.aivencloud.com",
        user="avnadmin",
        password="AVNS_hlTqrVhPxEdd4Xi4tiN",
        database="defaultdb",
        port=23940,
        ssl_verify_cert=False,
        ssl_verify_identity=False
    )
    return connection
