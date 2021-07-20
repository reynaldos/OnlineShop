from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    myapp = Flask(__name__)
    myapp.config['SECRET_KEY'] = 'secret'
    myapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    myapp.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  
    db.init_app(myapp)

    from .app import app
    from .app import query


    myapp.register_blueprint(app, url_prefix='/')
    myapp.register_blueprint(query, url_prefix='/')

    from .models import User, Product, Cart, Img

    # create DB
    create_database(myapp)

    login_manager = LoginManager()
    login_manager.login_view = 'app.login'
    login_manager.init_app(myapp)
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        # login reviewer

    return myapp


# database setup
def create_database(app):
    # if no db found in directory, create a new one
    # might not work on different os
    if not path.exists('shop/' + DB_NAME): 
        db.create_all(app=app)
        print('DB Created')


def addProducts():
    from .models import Product,Img
    exampleProducts = list()

    for i in range(20):
        newProduct = Product(
            SellerID = 2,
            Name = f"Eaxmple {i}",
            Description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            Price = 34.99)

        db.session.add(newProduct)

        newImage = Img(
                ProductId = newProduct.PID,
                img= '/static/logo.png',
                name= "examplet.png",
                mimetype="image/png")
        db.session.add(newImage)
        db.session.commit()
