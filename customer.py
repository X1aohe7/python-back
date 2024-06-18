from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Item, OrderDetail, Orders, User

customer = Blueprint('customer', __name__)


@customer.route('/customer/getAllShop', methods=['GET'])
def getAllShop():
    shops = User.query.filter_by(userType=1).all()
    res = [{"userId": shop.userId, "shopName": shop.shopName, "avatar": shop.avatar} for shop in shops]
    return jsonify(res)


@customer.route('/customer/getItems', methods=['GET'])
def getItems():
    userId = request.args.get('userId', type=int)
    items = Item.query.filter_by(userId=userId, isDeleted=0, status=1).all()
    res = [item.__dict__ for item in items]
    for r in res:
        r.pop('_sa_instance_state', None)  # Remove SQLAlchemy instance state
    return jsonify(res)


@customer.route('/customer/getOrder', methods=['POST'])
def getOrder():
    customerId = request.form.get('customerId', type=int)
    businessId = request.form.get('businessId', type=int)
    order = Orders.query.filter_by(customerId=customerId, businessId=businessId, customerStatus=0).first()

    if not order:
        order = Orders(customerId=customerId, businessId=businessId)
        db.session.add(order)
        db.session.commit()

    order_details = OrderDetail.query.filter_by(orderId=order.orderId).all()
    res = [detail.__dict__ for detail in order_details]
    for r in res:
        r.pop('_sa_instance_state', None)
    return jsonify(res=res, orderId=order.orderId)


@customer.route('/customer/changeQuantity', methods=['POST'])
def changeQuantity():
    orderId = request.form.get('orderId', type=int)
    itemId = request.form.get('itemId', type=int)
    quantity = request.form.get('quantity', type=int)
    price = request.form.get('price', type=float)

    order_detail = OrderDetail.query.filter_by(orderId=orderId, itemId=itemId).first()
    oldQuantity = order_detail.quantity if order_detail else 0

    if order_detail:
        order_detail.quantity = quantity
    else:
        order_detail = OrderDetail(orderId=orderId, itemId=itemId, quantity=quantity)
        db.session.add(order_detail)

    change = (quantity - oldQuantity) * price
    order = Orders.query.get(orderId)
    order.totalPrice += change

    db.session.commit()

    return jsonify("item quantity changed successfully")


@customer.route('/customer/getOrderList', methods=['GET'])
def getOrderList():
    customerId = request.args.get('customerId', type=int)

    # 查询订单列表，过滤出符合条件的订单
    orders = Orders.query.filter(Orders.customerId == customerId, Orders.totalPrice != 0).all()

    # 准备存储订单详细信息的列表
    order_list = []

    for order in orders:
        # 查询订单的详细信息
        order_details = OrderDetail.query.filter_by(orderId=order.orderId).all()

        # 构建订单的详细信息字典
        order_dict = {
            "orderId": order.orderId,
            "shopName": order.business.shopName,
            "totalPrice": order.totalPrice,
            "customerStatus": order.customerStatus,
            "businessStatus": order.businessStatus,
            # "orderDetails": []
        }

        # 遍历订单的详细信息并添加到订单字典中
        for detail in order_details:
            item = Item.query.get(detail.itemId)
            order_detail_dict = {
                "itemId": item.itemId,
                "itemName": item.itemName,
                "quantity": detail.quantity,
                "price": item.price
            }
            # order_dict["orderDetails"].append(order_detail_dict)

        # 将订单字典添加到订单列表中
        order_list.append(order_dict)

    return jsonify(order_list)


@customer.route('/customer/getOrderDetail', methods=['GET'])
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


@customer.route('/customer/pay', methods=['POST'])
def pay():
    orderId = request.form.get('orderId', type=int)
    order = Orders.query.get(orderId)
    if order:
        order.customerStatus = 1
        db.session.commit()
        return jsonify("pay successfully")
    return jsonify({"error": "Order not found"}), 404


@customer.route('/customer/cancel', methods=['POST'])
def cancel():
    orderId = request.form.get('orderId', type=int)
    order = Orders.query.get(orderId)
    if order:
        order.customerStatus = 3
        db.session.commit()
        return jsonify("canceled successfully")
    return jsonify({"error": "Order not found"}), 404


@customer.route('/customer/searchBusiness', methods=['GET'])
def searchBusiness():
    key = request.args.get('key', type=str)
    shops = User.query.filter(User.userType == 1, User.shopName.like(f"%{key}%")).all()
    res = [{"userId": shop.userId, "shopName": shop.shopName} for shop in shops]
    return jsonify(res)


@customer.route('/customer/updateCustomerInfo', methods=['POST'])
def updateCustomerInfo():
    userId = request.form.get('userId', type=int)
    customerName = request.form.get('customerName', type=str)
    avatar = request.form.get('avatar', type=str)
    user = User.query.get(userId)
    if user:
        user.customerName = customerName
        user.avatar = avatar
        db.session.commit()
        return jsonify("update successfully")
    return jsonify({"error": "User not found"}), 404


@customer.route('/customer/updatePassword', methods=['POST'])
def updatePassword():
    userId = request.form.get('userId', type=int)
    oldPassword = request.form.get('oldPassword', type=str)
    newPassword = request.form.get('newPassword', type=str)

    user = User.query.get(userId)
    if user and check_password_hash(user.password, oldPassword):
        user.password = generate_password_hash(newPassword)
        db.session.commit()
        return jsonify("update successfully")
    return jsonify({'error': '旧密码不正确或用户不存在'}), 400