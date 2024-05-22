from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块
from db.db import get_db_connection # 获取数据库连接
import mysql.connector

customer = Blueprint('customer', __name__)


@customer.route('/customer/getAllShop',methods=['GET'])
def getAllShop():


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "SELECT user.userId,user.shopName FROM user WHERE userType=1"
    cursor.execute(sql_query)

    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)

@customer.route('/customer/getItems',methods=['GET'])
def getItems():
    userId = request.args.get('userId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "SELECT * FROM item WHERE userId=%s and isDeleted=0 and status=1"
    cursor.execute(sql_query, (userId,))

    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)

@customer.route('/customer/getOrder',methods=['POST'])
def getOrder():
    customerId = request.form.get('customerId', type=int)
    businessId=request.form.get('businessId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "select * from orders where customerId=%s and businessId=%s and customerStatus=0"
    cursor.execute(sql_query1, (customerId,businessId))

    # 获取查询结果
    res = cursor.fetchall()

    if res==[]:
        sql_query2="insert into orders (customerId,businessId) values (%s,%s)"
        cursor.execute(sql_query2, (customerId, businessId))
        connection.commit()
    # sql_query1 = "select * from orders where customerId=%s and businessId=%s"
    cursor.execute(sql_query1, (customerId, businessId))
    res = cursor.fetchall()
    # print(res[0].get('orderId'))
    orderId=res[0].get('orderId')
    sql_query3=" select * from orderDetail where orderId=%s"
    cursor.execute(sql_query3,(orderId,))
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res=res,orderId=orderId)

@customer.route('/customer/changeQuantity',methods=['POST'])
def changeQuantity():
    orderId = request.form.get('orderId', type=int)
    itemId = request.form.get('itemId', type=int)
    quantity = request.form.get('quantity', type=int)
    price = request.form.get('price', type=float)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "select * from orderDetail where orderId=%s and itemId=%s"
    cursor.execute(sql_query1, (orderId, itemId))

    # 获取查询结果
    res = cursor.fetchall()

    if res == []:
        sql_query2 = "insert into orderDetail (orderId,itemId,quantity) values (%s,%s,1)"
        cursor.execute(sql_query2, (orderId, itemId))
        connection.commit()
        oldQuantity=0
    else:
        sql_query4 = "select quantity from orderDetail where orderId=%s and itemId=%s"
        cursor.execute(sql_query4, (orderId,itemId))
        res = cursor.fetchall()
        oldQuantity=res[0].get("quantity")
        sql_query3 = "UPDATE orderDetail SET quantity = %s WHERE orderId = %s AND itemId = %s"
        cursor.execute(sql_query3, (quantity, orderId, itemId))

    sql_query5=  "UPDATE orders SET totalPrice = totalPrice+%s WHERE orderId = %s"
    change=(quantity-oldQuantity)*price
    cursor.execute(sql_query5, (change,orderId))
    connection.commit()



    cursor.close()
    connection.close()
    return jsonify("item added successfully")

@customer.route('/customer/getOrderList',methods=['GET'])
def getOrderList():
    customerId = request.args.get('customerId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "select orders.*,user.shopName from orders,user where orders.businessId=user.userId and customerId=%s"
    cursor.execute(sql_query1, (customerId,))
    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)

@customer.route('/customer/getOrderDetail',methods=['GET'])
def getOrderDetail():
    # customerId = request.args.get('customerId', type=int)
    orderId = request.args.get('orderId', type=int)
    # print(request.values)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "select * from orderDetail,item where orderDetail.itemId=item.itemId and orderDetail.orderId=%s"
    sql_query2 = "select * from orders where orders.orderId=%s"
    cursor.execute(sql_query1, (orderId,))
    # 获取查询结果
    res = cursor.fetchall()
    cursor.execute(sql_query2, (orderId,))
    order = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(orderDetail=res,order=order)

@customer.route('/customer/pay',methods=['POST'])
def pay():
    orderId = request.form.get('orderId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "update orders set customerStatus=1 where orderId=%s"
    cursor.execute(sql_query1, (orderId,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify("pay successfully")

@customer.route('/customer/cancel',methods=['POST'])
def cancel():
    orderId = request.form.get('orderId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "update orders set customerStatus=3 where orderId=%s"
    cursor.execute(sql_query1, (orderId,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify("canceled successfully")


@customer.route('/customer/searchBusiness',methods=['GET'])
def searchBusiness():
    key = request.args.get('key', type=str)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "SELECT userId, shopName FROM user WHERE userType=1 AND shopName LIKE %s"
    like_key = f"%{key}%"  # 模糊匹配关键字

    cursor.execute(sql_query, (like_key,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    # 将结果以 JSON 格式返回
    return jsonify(results)

@customer.route('/customer/updateCustomerInfo',methods=['POST'])
def updateCustomerInfo():
    userId = request.form.get('userId', type=int)
    customerName = request.form.get('customerName', type=str)
    avatar = request.form.get('avatar', type=str)
    print(userId,customerName,avatar)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "update user set customerName=%s,avatar=%s where userId=%s"
    cursor.execute(sql_query, (customerName,avatar,userId))
    connection.commit()
    cursor.close()
    connection.close()

    # 将结果以 JSON 格式返回
    return jsonify("update successfully")

@customer.route('/customer/updatePassword',methods=['POST'])
def updatePassword():
    userId = request.form.get('userId', type=int)
    oldPassword = request.form.get('oldPassword', type=str)
    newPassword = request.form.get('newPassword', type=str)
    print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql="select password from user where userId=%s"
    cursor.execute(sql, (userId,))
    results = cursor.fetchall()
    # print(results)
    password=results[0].get("password")
    if(oldPassword != password):
        return jsonify({'error': '旧密码不正确'}), 400
    # 构建 SQL 查询语句
    sql_query = "update user set password=%s where userId=%s"
    cursor.execute(sql_query, (newPassword,userId))
    connection.commit()
    cursor.close()
    connection.close()

    # 将结果以 JSON 格式返回
    return jsonify("update successfully")