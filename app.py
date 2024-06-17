from flask import Flask
from login.login import login
from login.customerRegister import customerRegister
from login.businessRegister import businessRegister
from business.business import business
from customer.customer import customer
from AI.AI import AI
app = Flask(__name__)

app.register_blueprint(login)
app.register_blueprint(customerRegister)
app.register_blueprint(businessRegister)
app.register_blueprint(business)
app.register_blueprint(customer)
app.register_blueprint(AI)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
