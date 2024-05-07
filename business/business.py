from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块

import mysql.connector

business = Blueprint('business', __name__)

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