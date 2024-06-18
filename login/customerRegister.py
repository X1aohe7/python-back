from flask import Blueprint, jsonify, request  # 引入 request 模块
from werkzeug.security import generate_password_hash, check_password_hash
from db.db import get_db_connection  # 获取数据库连接

customerRegister = Blueprint('customerRegister', __name__)

@customerRegister.route('/customerRegister', methods=['POST'])
def customer_register():
    data = request.form
    username = data.get('username')
    customerName = data.get('customerName')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    # 验证输入数据
    if not username or not password or not confirmPassword:
        return jsonify({'message': '用户名、客户名和密码不能为空'}), 400

    if password != confirmPassword:
        return jsonify({'message': '两次输入的密码不一致'}), 400

    # 哈希密码
    hashed_password = generate_password_hash(password)

    # 获取数据库连接
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    # 使用参数化查询来避免 SQL 注入
    insert_query = "INSERT INTO user (username, customerName, password, userType) VALUES (%s, %s, %s, %s)"
    insert_data = (username, customerName, hashed_password, 0)
    cursor.execute(insert_query, insert_data)

    db_connection.commit()
    cursor.close()
    db_connection.close()

    return jsonify({'message': '注册成功', 'success': True}), 200
