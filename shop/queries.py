from flask import Blueprint
from sqlalchemy.orm import session
# from sqlalchemy.sql.expression import text
from sqlalchemy import text


from .models import User,Product,Cart
from . import db

query = Blueprint('query', __name__)


def getUserIds():
    """Returns all user Ids"""
    with db.engine.connect() as connection:
        data = connection.execute(text("SELECT UserId FROM User")).fetchall()
    result = [dict(row) for row in data]
    return result

def getSoldProducts():
    """Returns all prodcuts sold"""
    with db.engine.connect() as connection:
        data = connection.execute(text("SELECT * FROM product WHERE isSold = True")).fetchall()
    result = [dict(row) for row in data]
    return result

def getUserCartProducts(UserId):
    """Returns products in cart of user"""
    with db.engine.connect() as connection:
        data = connection.execute(text("SELECT PID FROM cart JOIN user JOIN Product WHERE UserId = {UserId}")).fetchall()
    result = [dict(row) for row in data]
    return result

def userActiveProducts(userid, search='', attribute = "Name", order="DESC"):
    """returns all products a user has posted"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM (SELECT * FROM product WHERE Name LIKE '%{search}%' OR Description LIKE '%{search}%') WHERE SellerId = {userid} ORDER BY {attribute} {order}")).fetchall()   
    result = [dict(row) for row in data]
    return result


def getProductImgs(productID):
    """returns all imgs that belong to a post"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM img WHERE ProductId = {productID}")).fetchall() 
    result = [dict(row) for row in data]
    return result


def sortProductBy(search='', attribute = "Name", order="DESC"):
    """Returns active products sort"""
    with db.        engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM (SELECT * FROM product WHERE Name LIKE '%{search}%' OR Description LIKE '%{search}%') WHERE isSold = FALSE ORDER BY {attribute} {order}")).fetchall()   
    result = [dict(row) for row in data]
    return result


def getItemsFromCart(userId):
    """Returns items user added to car"""
    with db.engine.connect() as connection:
        data = connection.execute(f"SELECT * FROM cart WHERE UserId = {userId}").first()
    # result = [dict(row) for row in data]
    return data


def searchProduct(search):
    """Returns active products from search"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM (SELECT * FROM PRODUCT WHERE Name LIKE '%{search}%' OR Description LIKE '%{search}%') WHERE isSold = FALSE")).fetchall()
    result = [dict(row) for row in data]
    return result

def get_all_users():
    """Returns all users and their respective products"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM User")).fetchall()
    result = [dict(row) for row in data]
    return result
