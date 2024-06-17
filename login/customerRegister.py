from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块
from db.db import get_db_connection # 获取数据库连接
import mysql.connector

customerRegister = Blueprint('customerRegister', __name__)

@customerRegister.route('/customerRegister', methods=['POST'])
def customer_register():
    data = request.form
    print(data)
    username = data.get('username')
    customerName = data.get('customerName')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')
    print(username, customerName, password, confirmPassword)
    # 验证输入数据
    if not username or not password or not confirmPassword:
        print('1')
        return jsonify({'message': '用户名、客户名和密码不能为空'}), 400

    if password != confirmPassword:
        print('2')
        return jsonify({'message': '两次输入的密码不一致'}), 400

    # 获取数据库连接
    db_connection = get_db_connection()

    cursor = db_connection.cursor()
    # 使用参数化查询来避免 SQL 注入
    insert_query = "INSERT INTO user (username, customerName, password, userType) VALUES (%s, %s, %s, %s)"
    insert_data = (username, customerName, password, 0)
    cursor.execute(insert_query, insert_data)

    db_connection.commit()
    cursor.close()
    db_connection.close()

    return jsonify({'message': '注册成功', 'success': True}), 200