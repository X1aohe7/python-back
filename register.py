from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from models import db, User

register = Blueprint('register', __name__)

@register.route('/customerRegister', methods=['POST'])
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

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400

    # 哈希密码
    hashed_password = generate_password_hash(password)

    # 创建新用户
    new_user = User(username=username, customerName=customerName, password=hashed_password, userType=0)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'success': True}), 200

@register.route('/businessRegister', methods=['POST'])
def business_register():
    data = request.form
    username = data.get('username')
    shopName = data.get('shopName')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    # 验证输入数据
    if not username or not password or not confirmPassword:
        return jsonify({'message': '用户名、商店名和密码不能为空'}), 400

    if password != confirmPassword:
        return jsonify({'message': '两次输入的密码不一致'}), 400

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400

    # 哈希密码
    hashed_password = generate_password_hash(password)

    # 创建新用户
    new_user = User(username=username, shopName=shopName, password=hashed_password, userType=1)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'success': True}), 200
