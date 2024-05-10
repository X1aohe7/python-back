import mysql.connector
#获取数据库连接
def get_db_connection():

    # 如果连接不存在，则创建一个新的连接

    db_connection = mysql.connector.connect(
            host="47.108.105.205",
            user="root",
            password="hjdhjd",
            database="flask"
    )
    return db_connection