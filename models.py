from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    userType = db.Column(db.Integer, nullable=False, comment='商家还是顾客 0为顾客 1为商家')
    shopName = db.Column(db.String(255))
    customerName = db.Column(db.String(255))
    avatar = db.Column(MEDIUMTEXT)

    items = db.relationship('Item', backref='user', lazy=True)
    orders = db.relationship('Orders', foreign_keys='Orders.customerId', backref='customer', lazy=True)
    business_orders = db.relationship('Orders', foreign_keys='Orders.businessId', backref='business', lazy=True)


class Item(db.Model):
    __tablename__ = 'item'
    itemId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    itemName = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    isDeleted = db.Column(db.Integer, nullable=False, default=0, comment='假删除 1表示被删除')
    avatar = db.Column(MEDIUMTEXT)

    order_details = db.relationship('OrderDetail', backref='item', lazy=True)


class Orders(db.Model):
    __tablename__ = 'orders'
    orderId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customerId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    businessId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    totalPrice = db.Column(db.Float, default=0)
    customerStatus = db.Column(db.Integer, default=0,
                               comment='(status==0){未支付}(status==1){ 已支付   }(status==2){"已退款"   }(status==3){"已取消"}status==4 已评价')
    businessStatus = db.Column(db.Integer, nullable=False, default=0,
                               comment='(status==0){     return "未确认"   }else if (status==1)"已确认"   }else if (status==2){     return "已退款"   }')

    order_details = db.relationship('OrderDetail', backref='order', lazy=True)


class OrderDetail(db.Model):
    __tablename__ = 'orderDetail'
    orderId = db.Column(db.Integer, db.ForeignKey('orders.orderId'), primary_key=True)
    itemId = db.Column(db.Integer, db.ForeignKey('item.itemId'), primary_key=True)
    quantity = db.Column(db.Integer)

class Cart(db.Model):
    __tablename__ = 'cart'
    cartId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    itemId = db.Column(db.Integer, db.ForeignKey('item.itemId'), nullable=False)
    businessId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    customerId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    quantity = db.Column(db.Integer)

    # 一个购物车项属于一个商品
    item = db.relationship('Item', backref=db.backref('carts', lazy=True))

    # 一个购物车项属于一个商家
    business = db.relationship('User', foreign_keys=[businessId],
                               backref=db.backref('business_carts', lazy=True))

    # 一个购物车项属于一个顾客
    customer = db.relationship('User', foreign_keys=[customerId],
                               backref=db.backref('customer_carts', lazy=True))

class Comment(db.Model):
    __tablename__ = 'comment'
    commentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderId = db.Column(db.Integer, db.ForeignKey('orders.orderId'), nullable=False)
    customerId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    businessId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    star = db.Column(db.Integer, nullable=False, comment='Rating given by the customer to the business (1-5)')
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    # Relationship with Orders
    order = db.relationship('Orders', backref=db.backref('comments', lazy=True))

    # Relationship with Users (as a customer)
    customer = db.relationship('User', foreign_keys=[customerId], backref=db.backref('customer_comments', lazy=True))

    # Relationship with Users (as a business)
    business = db.relationship('User', foreign_keys=[businessId], backref=db.backref('business_comments', lazy=True))

class Collect(db.Model):
    __tablename__ = 'collect'
    collectId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    itemId = db.Column(db.Integer, db.ForeignKey('item.itemId'), nullable=False)



