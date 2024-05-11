from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块
from db.db import get_db_connection # 获取数据库连接


business = Blueprint('business', __name__)



@business.route('/business/getItems',methods=['GET'])
def getItems():
    userId = request.args.get('userId', type=int)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "SELECT * FROM item WHERE userId=%s and isDeleted=0"
    cursor.execute(sql_query, (userId,))

    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)


@business.route('/business/createItem',methods=['POST'])
def createItem():

    userId = request.form["userId"]
    itemName = request.form['itemName']
    description = request.form['description']
    price = request.form['price']
    # print(request.form.get("itemName"))
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # # 构建 SQL 查询语句
    sql_query = "INSERT INTO item (userId,itemName, description, price) VALUES (%s,%s, %s, %s)"
    cursor.execute(sql_query, (userId, itemName, description, price))
    connection.commit()  # 提交事务
    cursor.close()
    connection.close()
    return jsonify({"message": "Item created successfully"})

@business.route('/business/changeStatus',methods=['POST'])
def changeStatus():

    userId = request.form["userId"]
    itemId = request.form['itemId']
    status = request.form['status']
    # print(request.form)
    # print(request.form.get("itemName"))
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "UPDATE item SET status=%s where userId=%s and itemId=%s"
    cursor.execute(sql_query, (status, userId, itemId,))
    connection.commit()  # 提交事务
    cursor.close()
    connection.close()
    return jsonify({"message": "Item changed successfully"})

@business.route('/business/deleteItem',methods=['POST'])
def deleteItem():
    userId = request.form.get('userId', type=int)
    itemId = request.form.get('itemId', type=int)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query = "UPDATE item SET isDeleted=1 where userId=%s and itemId=%s"
    cursor.execute(sql_query, (userId,itemId))
    connection.commit()  # 提交事务
    # 获取查询结果
    cursor.close()
    connection.close()
    return jsonify({"message": "Item deleted successfully"})

@business.route('/business/getOrderList',methods=['GET'])
def getOrderList():
    businessId = request.args.get('businessId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "select orders.* from orders where businessId=%s"
    sql_query1 = "select orders.*,user.customerName,user.userId from orders,user" \
                 " where orders.customerId=user.userId and businessId=%s and customerStatus!=0 and customerStatus!=3"
    cursor.execute(sql_query1, (businessId,))
    # 获取查询结果
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(res)
@business.route('/business/getOrderDetail',methods=['GET'])
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


@business.route('/business/confirm',methods=['POST'])
def confirm():
    orderId = request.form.get('orderId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "update orders set businessStatus=1 where orderId=%s"
    cursor.execute(sql_query1, (orderId,))
    connection.commit()
    return jsonify("pay successfully")

@business.route('/business/refund',methods=['POST'])
def refund():
    orderId = request.form.get('orderId', type=int)
    # print(userId)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 构建 SQL 查询语句
    sql_query1 = "update orders set customerStatus=2 , businessStatus=2 where orderId=%s"
    cursor.execute(sql_query1, (orderId,))
    connection.commit()
    return jsonify("canceled successfully")