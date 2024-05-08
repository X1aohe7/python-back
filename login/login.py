from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块

import mysql.connector

login = Blueprint('login', __name__)


#获取数据库连接
def get_db_connection():

    # 如果连接不存在，则创建一个新的连接

    db_connection = mysql.connector.connect(
            host="47.108.105.205",
            user="root",
            password="root",
            database="flask"
    )
    return db_connection

#用户登录
@login.route('/login',methods=['POST'])
def userLogin():
    username = request.form['username']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "SELECT user.userId,user.username,user.userType,user.shopName,user.customerName FROM user WHERE username=%s and password=%s"
    cursor.execute(sql_query, (username,password))

    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)

