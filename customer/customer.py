from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块

import mysql.connector

customer = Blueprint('customer', __name__)

#获取数据库连接
def get_db_connection():

    # 如果连接不存在，则创建一个新的连接

    db_connection = mysql.connector.connect(
            host="47.108.105.205",
            user="root",
            password="root",
            database="flask"
    )
    return db_connection

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
    sql_query1 = "select * from orders where customerId=%s and businessId=%s"
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

    else:
        sql_query3 = "UPDATE orderDetail SET quantity = %s WHERE orderId = %s AND itemId = %s"
        cursor.execute(sql_query3, (quantity,orderId, itemId))
        connection.commit()
    cursor.close()
    connection.close()
    return jsonify("item added successfully")

