from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from models import db, Item, OrderDetail, Orders, User, Cart, Comment

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
    # orderId = request.form.get('orderId', type=int)
    customerId = request.form.get('customerId', type=int)
    businessId = request.form.get('businessId', type=int)
    itemId = request.form.get('itemId', type=int)
    quantity = request.form.get('quantity', type=int)
    print(request.form)
    # Validate input
    if customerId is None or businessId is None or itemId is None or quantity is None:
        return jsonify({'message': 'Missing or invalid input'}), 400

    # 查找购物车中的项
    cart_item = Cart.query.filter_by(customerId=customerId, businessId=businessId, itemId=itemId).first()

    if quantity > 0:
        # 如果数量大于0，更新购物车或创建新的购物车项
        if cart_item:
            cart_item.quantity = quantity
        else:
            cart_item = Cart(customerId=customerId, businessId=businessId, itemId=itemId, quantity=quantity)
            db.session.add(cart_item)
    elif quantity == 0:
        # 如果数量为0，删除购物车项
        if cart_item:
            db.session.delete(cart_item)

    try:
        db.session.commit()
        print("ok")

        return jsonify({'message': '操作成功'}), 200
    except Exception as e:
        db.session.rollback()
        print("error")

        return jsonify({'message': f'操作失败: {str(e)}'}), 500

@customer.route('/customer/getCartList', methods=['GET'])
def getCartList():
    customerId = request.args.get('customerId', type=int)

    # 验证输入
    if customerId is None:
        return jsonify({'message': 'Missing or invalid customerId'}), 400

    # 查询购物车列表
    cart_list = Cart.query.filter_by(customerId=customerId).all()

    # 构建返回数据
    business_dict = {}
    for cart_item in cart_list:
        item = Item.query.get(cart_item.itemId)
        business = User.query.get(cart_item.businessId)

        if business.userId not in business_dict:
            business_dict[business.userId] = {
                'businessId': business.userId,
                'businessName': business.shopName,
                'cartItems': [],
                'totalPrice': 0.0  # 初始化总价
            }

        item_price = item.price if item else 0
        item_total_price = item_price * cart_item.quantity

        business_dict[business.userId]['cartItems'].append({
            'cartId': cart_item.cartId,
            'itemId': cart_item.itemId,
            'itemName': item.itemName if item else None,
            'itemDescription': item.description if item else None,
            'itemPrice': item_price,
            'quantity': cart_item.quantity,
            'itemTotalPrice': item_total_price  # 添加每个商品的总价
        })

        # 累加每个商品的总价到商家的总价
        business_dict[business.userId]['totalPrice'] += item_total_price

    # 将字典转换为列表以保持一致性
    result = list(business_dict.values())

    return jsonify(result), 200

@customer.route('/customer/getCartListByBusinessId', methods=['GET'])
def getCartListByBusinessId():
    customerId = request.args.get('customerId', type=int)
    businessId = request.args.get('businessId', type=int)

    # 验证输入
    if customerId is None or businessId is None:
        return jsonify({'message': 'Missing or invalid customerId or businessId'}), 400

    # 查询购物车列表
    cart_list = Cart.query.filter_by(customerId=customerId,businessId=businessId).all()

    # 构建返回数据
    cart_items = []
    for cart_item in cart_list:
        item = Item.query.get(cart_item.itemId)
        business = User.query.get(cart_item.businessId)

        cart_items.append({
            'cartId': cart_item.cartId,
            'itemId': cart_item.itemId,
            'itemName': item.itemName if item else None,
            'avatar': item.avatar if item else None,
            'itemDescription': item.description if item else None,
            'itemPrice': item.price if item else None,
            'quantity': cart_item.quantity,
            'businessId': cart_item.businessId,
            'businessName': business.shopName if business else None,
        })

    return jsonify({'cartItems': cart_items}), 200




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
            "businessId":order.businessId,
            "shopName": order.business.shopName,
            "totalPrice": order.totalPrice,
            "customerStatus": order.customerStatus,
            "businessStatus": order.businessStatus,
            # "orderDetails": []
        }

        # 遍历订单的详细信息并添加到订单字典中
        # for detail in order_details:
        #     item = Item.query.get(detail.itemId)
        #     order_detail_dict = {
        #         "itemId": item.itemId,
        #         "itemName": item.itemName,
        #         "quantity": detail.quantity,
        #         "price": item.price
        #     }
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


# @customer.route('/customer/pay', methods=['POST'])
# def pay():
#     orderId = request.form.get('orderId', type=int)
#     order = Orders.query.get(orderId)
#     if order:
#         order.customerStatus = 1
#         db.session.commit()
#         return jsonify("pay successfully")
#     return jsonify({"error": "Order not found"}), 404

@customer.route('/customer/pay', methods=['POST'])
def pay():
    data = request.get_json()
    customerId = data.get('customerId')
    businessId = data.get('businessId')

    if customerId is None or businessId is None:
        return jsonify({'success': False, 'message': 'Missing or invalid input'}), 400

    try:
        # 查询购物车中的项
        cart_items = Cart.query.filter_by(customerId=customerId, businessId=businessId).all()

        if not cart_items:
            return jsonify({'success': False, 'message': '购物车为空'}), 400

        # 计算总价
        total_price = sum(item.item.price * item.quantity for item in cart_items)

        # 创建订单
        new_order = Orders(
            customerId=customerId,
            businessId=businessId,
            totalPrice=total_price,
            customerStatus=1,  # 标记为已支付
            businessStatus=0
        )
        db.session.add(new_order)
        db.session.flush()  # 获取新订单的 orderId

        # 创建订单明细
        for cart_item in cart_items:
            order_detail = OrderDetail(
                orderId=new_order.orderId,
                itemId=cart_item.itemId,
                quantity=cart_item.quantity
            )
            db.session.add(order_detail)

        # 清空购物车
        for cart_item in cart_items:
            db.session.delete(cart_item)

        db.session.commit()
        return jsonify({'success': True, 'message': '支付成功，订单已创建'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': f'支付失败: {str(e)}'}), 500

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
    res = [{"userId": shop.userId, "shopName": shop.shopName,"avatar": shop.avatar} for shop in shops]
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


@customer.route('/customer/comment', methods=['POST'])
def comment():
    try:
        data = request.form
        business_id = data.get('businessId')
        customer_id = data.get('customerId')
        order_id = data.get('orderId')
        star = data.get('star')
        description = data.get('description')

        # 检查所有字段是否存在
        if not all([business_id, customer_id, order_id, star, description]):
            return jsonify({'message': '请填写完整的表单信息'}), 400

        # 验证star是否在1到5之间
        rating = int(star)
        if rating < 1 or rating > 5:
            return jsonify({'message': '星级必须在1到5之间'}), 400

        # 创建并保存新评论
        new_comment = Comment(
            businessId=business_id,
            customerId=customer_id,
            orderId=order_id,
            description=description,
            star=star,
            timestamp=datetime.utcnow()
        )

        db.session.add(new_comment)

        # 更新订单的customerStatus为4 (已评价)
        order = Orders.query.get(order_id)
        if order:
            order.customerStatus = 4
            db.session.commit()
        else:
            db.session.rollback()
            return jsonify({'message': '订单不存在'}), 404

        return jsonify({'message': '评价成功'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '服务器错误', 'error': str(e)}), 500

@customer.route('/customer/getCommentByOrderId', methods=['GET'])
def getCommentByOrderId():
    try:
        data = request.args
        order_id = data.get('orderId')

        # 查询指定订单的唯一评论信息
        comment = Comment.query.filter_by(orderId=order_id).first()

        if not comment:
            return jsonify({'message': '未找到指定订单的评价信息'}), 404

        # 构造返回的评价信息
        comment_item = {
            'commentId': comment.commentId,
            'customerId': comment.customerId,
            'businessId': comment.businessId,
            'description': comment.description,
            'star': comment.star,
            'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify({'comment': comment_item}), 200

    except Exception as e:
        return jsonify({'message': '服务器错误', 'error': str(e)}), 500


@customer.route('/customer/getCommentsByBusinessId', methods=['GET'])
def getCommentsByBusinessId():
    try:
        data = request.args
        business_id = data.get('businessId')

        # 验证输入
        if business_id is None:
            return jsonify({'message': 'Missing or invalid businessId'}), 400

        # 查询指定商家的所有评论信息
        comments = Comment.query.filter_by(businessId=business_id).all()

        if not comments:
            return jsonify({'message': '未找到指定商家的评价信息'}), 404

        # 构造返回的评价信息列表
        comment_list = []
        for comment in comments:
            comment_item = {
                'commentId': comment.commentId,
                'customerId': comment.customerId,
                'businessId': comment.businessId,
                'description': comment.description,
                'star': comment.star,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            comment_list.append(comment_item)

        return jsonify({'comments': comment_list}), 200

    except Exception as e:
        return jsonify({'message': '服务器错误', 'error': str(e)}), 500
