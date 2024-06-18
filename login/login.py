from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块
from db.db import get_db_connection # 获取数据库连接
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

login = Blueprint('login', __name__)



#用户登录
@login.route('/login',methods=['POST'])
def userLogin():
    username = request.form['username']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql_query = "SELECT userId, username, password, userType, shopName, customerName, avatar FROM user WHERE username=%s"
    cursor.execute(sql_query, (username,))

    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user and check_password_hash(user['password'], password):
        user.pop('password')  # 不返回密码
        return jsonify(user)
    else:
        return jsonify({'message': '用户名或密码错误'}), 401


# if __name__ == '__main__':
#     # 原始密码
#     password = "123456"
#
#     # 使用 bcrypt 加密密码
#     hashed_password = generate_password_hash(password)
#
#     # 打印加密后的密码
#     print("Hashed password:", hashed_password)
#
#     # 验证密码
#     is_valid = check_password_hash(hashed_password, password)
#     print("Password is valid:", is_valid)