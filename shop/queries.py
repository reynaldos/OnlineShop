from .models import User,Product,Cart
from . import db

# returns all user Ids
def getUserIds():
    result = db.engine.execute("<SELECT UserId FROM User >")
    return result

# returns all products a user has posted
def userActiveProducts(userId):
    productList = db.engine.execute(f"<SELECT ProductsForSale FROM User WHERE UserId = {userId} >")
    result = [product for product in productList if product.isSold == False]
    return result

# returns active products sort
def sortProductBy(attribute, order="DESC"):
    result = db.engine.execute(f"<SELECT * FROM Product WHERE isSold = TRUE ORDER BY {attribute} {order}>")
    return result