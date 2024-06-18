from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块
from db.db import get_db_connection # 获取数据库连接
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

businessRegister = Blueprint('businessRegister', __name__)

@businessRegister.route('/businessRegister', methods=['POST'])
def business_register():
    data = request.form
    username = data.get('username')
    shopName = data.get('shopName')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    if not username or not password or not confirmPassword:
        return jsonify({'message': '用户名、客户名和密码不能为空'}), 400

    if password != confirmPassword:
        return jsonify({'message': '两次输入的密码不一致'}), 400

    # 哈希密码
    hashed_password = generate_password_hash(password)

    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    insert_query = "INSERT INTO user (username, shopName, password, userType) VALUES (%s, %s, %s, %s)"
    insert_data = (username, shopName, hashed_password, 1)
    cursor.execute(insert_query, insert_data)

    db_connection.commit()
    cursor.close()
    db_connection.close()

    return jsonify({'message': '注册成功', 'success': True}), 200