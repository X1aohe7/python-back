from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Item, OrderDetail, Orders, User

business = Blueprint('business', __name__)


@business.route('/business/getItems', methods=['GET'])
def getItems():
    userId = request.args.get('userId', type=int)
    items = Item.query.filter_by(userId=userId, isDeleted=0).all()
    res = [item.__dict__ for item in items]
    for r in res:
        r.pop('_sa_instance_state', None)  # Remove SQLAlchemy instance state
    return jsonify(res)


@business.route('/business/createItem', methods=['POST'])
def createItem():
    data = request.form
    item = Item(
        userId=data.get("userId"),
        itemName=data.get('itemName'),
        description=data.get('description'),
        price=data.get('price'),
        avatar=data.get('avatar')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item created successfully"})


@business.route('/business/changeStatus', methods=['POST'])
def changeStatus():
    userId = request.form["userId"]
    itemId = request.form['itemId']
    status = request.form['status']
    item = Item.query.filter_by(userId=userId, itemId=itemId).first()
    if item:
        item.status = status
        db.session.commit()
        return jsonify({"message": "Item status changed successfully"})
    return jsonify({"error": "Item not found"}), 404


@business.route('/business/deleteItem', methods=['POST'])
def deleteItem():
    userId = request.form.get('userId', type=int)
    itemId = request.form.get('itemId', type=int)
    item = Item.query.filter_by(userId=userId, itemId=itemId).first()
    if item:
        item.isDeleted = 1
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"})
    return jsonify({"error": "Item not found"}), 404


@business.route('/business/getOrderList', methods=['GET'])
def getOrderList():
    businessId = request.args.get('businessId', type=int)
    orders = Orders.query.filter_by(businessId=businessId).filter(Orders.customerStatus != 0,
                                                                  Orders.customerStatus != 3,
                                                                  Orders.totalPrice != 0).all()
    res = []
    for order in orders:
        order_dict = order.__dict__
        order_dict.pop('_sa_instance_state', None)
        user = User.query.get(order.customerId)
        order_dict['customerName'] = user.customerName
        res.append(order_dict)
    return jsonify(res)


@business.route('/business/getOrderDetail', methods=['GET'])
def getOrderDetail():
    orderId = request.args.get('orderId', type=int)

    # 使用 SQLAlchemy 查询订单详情信息
    order_details = OrderDetail.query.filter_by(orderId=orderId).all()
    items = []
    for detail in order_details:
        item = Item.query.get(detail.itemId).__dict__  # 获取订单详情中的商品信息
        item.pop('_sa_instance_state', None)  # 移除 SQLAlchemy 实例状态
        item['quantity'] = detail.quantity  # 添加商品数量字段
        items.append(item)

    # 查询订单本身的信息
    order = Orders.query.get(orderId)
    order_dict = {
        'orderId': order.orderId,
        'customerId': order.customerId,
        'businessId': order.businessId,
        'totalPrice': order.totalPrice,
        'customerStatus': order.customerStatus,
        'businessStatus': order.businessStatus
    }

    # 返回 JSON 格式的订单详细信息，包括订单信息和商品信息列表
    return jsonify(orderDetail=items, order=order_dict)


@business.route('/business/confirm', methods=['POST'])
def confirm():
    orderId = request.form.get('orderId', type=int)
    order = Orders.query.get(orderId)
    if order:
        order.businessStatus = 1
        db.session.commit()
        return jsonify("Order confirmed successfully")
    return jsonify({"error": "Order not found"}), 404


@business.route('/business/refund', methods=['POST'])
def refund():
    orderId = request.form.get('orderId', type=int)
    order = Orders.query.get(orderId)
    if order:
        order.customerStatus = 2
        order.businessStatus = 2
        db.session.commit()
        return jsonify("Order refunded successfully")
    return jsonify({"error": "Order not found"}), 404


@business.route('/business/updateBusinessInfo', methods=['POST'])
def updateBusinessInfo():
    userId = request.form.get('userId', type=int)
    shopName = request.form.get('shopName', type=str)
    avatar = request.form.get('avatar', type=str)
    user = User.query.get(userId)
    if user:
        user.shopName = shopName
        user.avatar = avatar
        db.session.commit()
        return jsonify("Business info updated successfully")
    return jsonify({"error": "User not found"}), 404


@business.route('/business/updatePassword', methods=['POST'])
def updatePassword():
    userId = request.form.get('userId', type=int)
    oldPassword = request.form.get('oldPassword', type=str)
    newPassword = request.form.get('newPassword', type=str)

    user = User.query.get(userId)
    if user and check_password_hash(user.password, oldPassword):
        user.password = generate_password_hash(newPassword)
        db.session.commit()
        return jsonify("Password updated successfully")
    return jsonify({'error': 'Incorrect old password or user not found'}), 400
