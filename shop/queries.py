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


def userActiveProducts(userId):
    """returns all products a user has posted"""
    with db.engine.connect() as connection:
        productData = connection.execute(f"SELECT ProductsForSale FROM User WHERE UserId = {userId} ").fetchall()
    productList = [dict(row) for row in productData]
        # check output type
    result = [product for product in productList if product['isSold'] == False]
    return result


def getProductImgs(productID):
    """returns all imgs that belong to a post"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM product JOIN img WHERE ProductId = {productID}")).fetchall() 
    result = [dict(row) for row in data]
    return result


def sortProductBy(search='', attribute = "Name", order="DESC"):
    """Returns active products sort"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM (SELECT * FROM product WHERE Name LIKE '%{search}%' OR Description LIKE '%{search}%') WHERE isSold = FALSE ORDER BY {attribute} {order}")).fetchall()   
    result = [dict(row) for row in data]
    return result


def getItemsFromCart(userId):
    """Returns items user added to car"""
    with db.engine.connect() as connection:
        data = connection.execute(f"SELECT Products FROM Cart NATURAL JOIN User WHERE UserId = {userId}").fetchall()
    result = [dict(row) for row in data]
    return result


def searchProduct(search):
    """Returns active products from search"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM (SELECT * FROM PRODUCT WHERE Name LIKE '%{search}%' OR Description LIKE '%{search}%') WHERE isSold = FALSE")).fetchall()
    result = [dict(row) for row in data]
    return result