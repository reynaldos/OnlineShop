from flask import Blueprint
from sqlalchemy.orm import session
# from sqlalchemy.sql.expression import text
from sqlalchemy import text


from .models import User,Product,Cart
from . import db

query = Blueprint('query', __name__)


# reads in queries
def read(data):
        """Takes in results of query and returns a list of dicts, whose keys are column names."""
        
        results = []

        if len(data)==0:
            return results

        # results from sqlalchemy are returned as a list of tuples; this procedure converts it into a list of dicts
        for row_number, row in enumerate(data):
            results.append({})
            for column_number, value in enumerate(row):
                results[row_number][row.keys()[column_number]] = value

        return results


def getUserIds():
    """Returns all user Ids"""

    with db.engine.connect() as connection:
        data = connection.execute("SELECT UserId FROM User").fetchall()
        result = read(data)
        return result


def userActiveProducts(userId):
    """returns all products a user has posted"""
    with db.engine.connect() as connection:
        productData = connection.execute(f"SELECT ProductsForSale FROM User WHERE UserId = {userId} ").fetchall()
        productList = read(productData)

        # check output type
        result = [product for product in productList if product[8] == False]
    return result


def sortProductBy(attribute = "Name", order="DESC"):
    """Returns active products sort"""
    with db.engine.connect() as connection:
        data = connection.execute(text(f"SELECT * FROM Product WHERE isSold = TRUE ORDER BY {attribute} {order}")).fetchall()
        result = read(data)
        return result


def getItemsFromCart(userId):
    """Returns items user added to car"""

    with db.engine.connect() as connection:
        data = connection.execute(f"SELECT Products FROM Cart NATURAL JOIN User WHERE UserId = {userId}").fetchall()
        result = read(data)
        return result
