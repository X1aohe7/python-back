from flask import Flask
from models import db
from business import business
from customer import customer
from login import login
from register import register
from AI import AI
from models import Collect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:hjdhjd@47.108.105.205/market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# with app.app_context():
#     # 单独创建Collect表
#     Collect.__table__.create(db.engine)

app.register_blueprint(business)
app.register_blueprint(customer)
app.register_blueprint(login)
app.register_blueprint(AI)
app.register_blueprint(register)

with app.app_context():
    db.create_all()


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

if __name__ == '__main__':
    app.run(debug=True)
