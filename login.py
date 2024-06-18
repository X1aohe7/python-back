from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash
from models import db, User

login = Blueprint('login', __name__)

# 用户登录
@login.route('/login', methods=['POST'])
def userLogin():
    print(request.form)
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    print(check_password_hash(user.password, password))
    print(user.password)
    if user and check_password_hash(user.password, password):
        user_info = {
            'userId': user.userId,
            'username': user.username,
            'userType': user.userType,
            'shopName': user.shopName,
            'customerName': user.customerName,
            'avatar': user.avatar
        }
        return jsonify(user_info)
    else:
        return jsonify({'message': '用户名或密码错误'}), 401
